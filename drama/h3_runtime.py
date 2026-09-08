"""Shared pinned H3 Turbo loader for warm, bounded production runs."""
def load_pipeline(workflow='t2va'):
    import torch
    from diffusers import ModularPipeline,ComponentsManager
    from safetensors.torch import load_file
    pipe=ModularPipeline.from_pretrained('/cache/model',workflow=workflow,components_manager=ComponentsManager())
    pipe.load_components(dtype=torch.bfloat16)
    factors=load_file('/cache/lora/minimax_h3_fl2v_turbo_4step_v0.1.safetensors')
    weights=dict(pipe.transformer.named_parameters()); suffix='.lora_A.default.weight'
    bases=[k[:-len(suffix)] for k in factors if k.endswith(suffix)]
    if not bases: raise ValueError('No compatible Turbo adapter factors')
    with torch.no_grad():
        for key in bases:
            a=factors[key+suffix]; b=factors[key+'.lora_B.default.weight']; target=weights[key+'.weight']
            target.copy_((target.float()+(b.float()@a.float())*(8/a.shape[0])).to(target.dtype))
    del factors,weights
    pipe.to('cuda'); pipe.transformer.set_attention_backend('_native_cudnn')
    return pipe
