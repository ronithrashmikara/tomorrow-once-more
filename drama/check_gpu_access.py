"""Small bounded hardware-access check; no model download or generation."""
import modal
app=modal.App('aoi-gpu-access-check')
@app.function(gpu='L40S',timeout=15,startup_timeout=30,max_containers=1,
              min_containers=0,scaledown_window=2,retries=0)
def check():
    import subprocess
    return subprocess.check_output(['nvidia-smi','--query-gpu=name,memory.total','--format=csv,noheader'],text=True)
@app.local_entrypoint()
def main():print(check.remote())
