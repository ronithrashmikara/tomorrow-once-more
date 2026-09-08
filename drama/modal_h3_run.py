"""Bounded H3 Turbo benchmark, second attempt.

The first attempt downloaded into a plain local directory, so the repository's
modular_model_index.json still resolved each component against the Hub and the
offline load produced an empty pipeline. Everything now lands in the real HF
cache under /cache/hf, which is what an offline from_pretrained reads.
"""
from pathlib import Path
import json, time
import modal

HERE = Path(__file__).resolve().parent
MODEL = 'MiniMaxAI/MiniMax-H3'
MODEL_REV = '42ed227ee7df40d41602854ae760620d6eb651fe'
LORA = 'lightx2v/Minimax-h3-Turbo'
LORA_REV = '2f015e66b37c585cea9dc4ae6f1850ea8788e742'
LORA_FILE = 'minimax_h3_fl2v_turbo_4step_v0.1.safetensors'
DIFFUSERS_REV = '665f578278365ea4a3318cb8c9b66ce6c01204b9'

app = modal.App('aoi-h3-turbo-run')
cache = modal.Volume.from_name('aoi-h3-cache-v2', create_if_missing=True)
base = (modal.Image.debian_slim(python_version='3.12')
        .apt_install('git', 'ffmpeg')
        .pip_install('huggingface-hub==1.24.0', 'hf_xet')
        .env({'HF_HOME': '/cache/hf'}))
gpu_image = (base.pip_install('torch==2.11.0', 'torchvision==0.26.0',
                              extra_index_url='https://download.pytorch.org/whl/cu130')
             .pip_install('git+https://github.com/huggingface/diffusers.git@' + DIFFUSERS_REV,
                          'transformers==5.8.0', 'accelerate==1.14.0', 'av', 'pillow', 'numpy',
                          'safetensors>=0.8.0')
             .env({'HF_HOME': '/cache/hf', 'HF_HUB_OFFLINE': '1', 'TOKENIZERS_PARALLELISM': 'false'}))


@app.function(image=base.env({'HF_XET_HIGH_PERFORMANCE': '1'}), volumes={'/cache': cache},
              cpu=(8, 8), memory=(16384, 16384), timeout=3600, startup_timeout=120,
              max_containers=1, min_containers=0, scaledown_window=2, retries=0)
def download():
    from huggingface_hub import snapshot_download, hf_hub_download
    started = time.monotonic()
    snapshot_download(MODEL, revision=MODEL_REV,
                      allow_patterns=['*.json', 'tokenizer/*', 'processor/*', 'text_encoder/*',
                                      'transformer/*', 'vae/*', 'audio_vae/*', 'scheduler/*',
                                      'audio_scheduler/*'],
                      ignore_patterns=['FL2VA/*', 'Ref2VA/*', 'transformer_ref/*'], max_workers=12)
    hf_hub_download(LORA, LORA_FILE, revision=LORA_REV)
    cache.commit()
    size = sum(f.stat().st_size for f in Path('/cache/hf').rglob('*') if f.is_file())
    return {'download_seconds': time.monotonic() - started, 'cache_bytes': size}


def build_pipeline():
    """Load the pipeline and merge the 4-step Turbo factors into the transformer."""
    import torch
    from diffusers import ComponentsManager, ModularPipeline
    from huggingface_hub import hf_hub_download
    from safetensors.torch import load_file

    manager = ComponentsManager()
    pipe = ModularPipeline.from_pretrained(MODEL, workflow='t2va', components_manager=manager)
    pipe.load_components(dtype=torch.bfloat16)
    if pipe.transformer is None:
        raise RuntimeError(f'components missing: {sorted(manager.components)}')

    factors = load_file(hf_hub_download(LORA, LORA_FILE, revision=LORA_REV))
    weights = dict(pipe.transformer.named_parameters())
    suffix = '.lora_A.default.weight'
    bases = [k[:-len(suffix)] for k in factors if k.endswith(suffix)]
    if not bases:
        raise ValueError('No compatible Turbo factors')
    with torch.no_grad():
        for key in bases:
            a, b = factors[key + suffix], factors[key + '.lora_B.default.weight']
            target = weights[key + '.weight']
            target.copy_((target.float() + (b.float() @ a.float()) * (8 / a.shape[0])).to(target.dtype))
    del factors, weights
    manager.enable_auto_cpu_offload(device='cuda', memory_reserve_margin='12GB')
    pipe.transformer.set_attention_backend('_native_cudnn')
    return pipe


@app.function(image=gpu_image, volumes={'/cache': cache}, gpu='B200', cpu=(8, 8),
              memory=(196608, 196608), timeout=1800, startup_timeout=180, max_containers=1,
              min_containers=0, scaledown_window=2, retries=0, single_use_containers=True)
def benchmark():
    import torch
    from diffusers.utils.export_utils import encode_video
    started = time.monotonic()
    pipe = build_pipeline()
    load_seconds = time.monotonic() - started

    prompt = ('Contemporary Japanese live-action drama, realistic natural dawn light. '
              'One original fictional Japanese woman, Aoi, age 22, shoulder-length straight dark hair, '
              'cream cotton pajamas, seated in a modest bedroom above a family cafe. '
              'Medium close-up with a whole blue ceramic cup in her hands. She looks toward the door, '
              'eyes suddenly wet with recognition, and softly says exactly <d>[Japanese] おかあさん？</d> '
              'Her mouth closes after the question. Quiet indoor room tone, distant kettle, no music, '
              'no captions, no text on screen, steady camera, five seconds, no cuts.')
    gen_started = time.monotonic()
    with torch.inference_mode():
        result = pipe(prompt=prompt, height=544, width=960, num_frames=124,
                      num_inference_steps=5, generator=torch.Generator('cpu').manual_seed(4112))
    gen_seconds = time.monotonic() - gen_started

    path = '/tmp/aoi_h3_turbo_benchmark.mp4'
    encode_video(result.get('videos')[0], fps=24, output_path=path,
                 audio=result.get('audio')[0].cpu(), audio_sample_rate=result.get('sampling_rate'))
    report = {'gpu': torch.cuda.get_device_name(), 'load_seconds': load_seconds,
              'generation_seconds': gen_seconds, 'total_function_seconds': time.monotonic() - started,
              'frames': len(result.get('videos')[0]), 'fps': 24, 'width': 960, 'height': 544,
              'num_inference_steps': 5, 'model': MODEL, 'model_revision': MODEL_REV,
              'lora': LORA, 'lora_revision': LORA_REV}
    return Path(path).read_bytes(), report


@app.local_entrypoint()
def main():
    out = HERE / 'benchmark'
    out.mkdir(exist_ok=True)
    ledger_path = HERE / 'budget_15.json'
    ledger = json.loads(ledger_path.read_text())
    if ledger['reserved_usd'] + 3 > ledger['limit_usd'] - ledger['reserve_usd']:
        raise RuntimeError('Budget gate: insufficient unreserved budget')
    ledger['reserved_usd'] += 3
    ledger['attempts'].append({'kind': 'benchmark-v2', 'reserved_usd': 3, 'started_epoch': time.time()})
    ledger_path.write_text(json.dumps(ledger, indent=2))

    info = download.remote()
    (out / 'download_v2.json').write_text(json.dumps(info, indent=2))
    print(json.dumps(info, indent=2), flush=True)
    video, report = benchmark.remote()
    (out / 'aoi_h3_turbo_benchmark.mp4').write_bytes(video)
    (out / 'benchmark_v2.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
