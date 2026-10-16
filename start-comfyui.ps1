# ComfyUI launcher (portable: all machine paths via env, fail loudly).
#
# Required env (see docs/MACHINE-SETUP.md):
#   COMFY_DIR     ComfyUI install dir (contains main.py)
#   COMFY_PYTHON  Python that runs it ( ROCm/fork venv python)
# Optional env:
#   COMFY_URL     default http://127.0.0.1:8188 (port parsed from it)
#   TQDM_DISABLE  forced to 1 below (tqdm bars crash with Errno 22 when
#                 stderr is a pipe — all KSampler runs error, GPU idles).
param(
  [string]$ComfyDir = $env:COMFY_DIR,
  [string]$ComfyPython = $env:COMFY_PYTHON
)
$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($ComfyDir)) { throw 'COMFY_DIR is not set (ComfyUI install dir; see docs/MACHINE-SETUP.md)' }
if ([string]::IsNullOrWhiteSpace($ComfyPython)) { throw 'COMFY_PYTHON is not set (fork venv python; see docs/MACHINE-SETUP.md)' }
$Port = 8188
if ($env:COMFY_URL -match ':(\d+)(/|$)') { $Port = [int]$Matches[1] }
$env:TQDM_DISABLE = '1'
& $ComfyPython (Join-Path $ComfyDir 'main.py') --listen 127.0.0.1 --port $Port --lowvram --disable-pinned-memory --preview-method auto --disable-auto-launch
