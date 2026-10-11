# ComfyUI launcher (comfyui-rocm fork, RDNA2-ready).
$ErrorActionPreference = 'Stop'
# TQDM_DISABLE=1: tqdm progress bars crash with Errno 22 when stderr is a
# pipe (all KSampler runs error, GPU idles). Proven 2026-10-11.
$env:TQDM_DISABLE = '1'
& C:\comfyui-rocm\python_env\python.exe C:\comfyui-rocm\main.py --listen 127.0.0.1 --port 8188 --lowvram --disable-pinned-memory --preview-method auto --disable-auto-launch
