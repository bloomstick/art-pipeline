# MACHINE-SETUP — one-time per-PC install (instructions only, no binaries)

This repo ships scripts + docs + skill. Everything heavy (models, venvs,
servers) is installed on the machine by YOU following this page, then
pointed to via environment variables. Nothing below is committed.

## 1. Environment variables (required)

| Var | Meaning | Example (reference PC) |
|---|---|---|
| `COMFY_URL` | ComfyUI server URL | `http://127.0.0.1:8188` |
| `COMFY_INPUT` | ComfyUI input dir (REQUIRED, no default) | `C:\comfyui-rocm\input` |
| `COMFY_DIR` | ComfyUI install dir (has `main.py`) | `C:\comfyui-rocm` |
| `COMFY_PYTHON` | Python that runs ComfyUI | `C:\comfyui-rocm\python_env\python.exe` |
| `ART_OUTPUT_DIR` | Staging for generations (default: `output/` in repo) | unset (uses default) |
| `ART_SRC_DIR` | Finish-script source dir (default: repo `output/`) | unset |
| `ART_ESRGAN_MODEL` | RealESRGAN_x4plus `.pth` path (REQUIRED for `esrgan.py`) | `C:\AI\models\RealESRGAN_x4plus.pth` |
| `ART_VENV_PY` | Venv python for rembg/upscale scripts | `C:\AI\venv\Scripts\python.exe` |
| `ART_PIPELINE_DIR` | This repo checkout (plugin use) | `C:\my\projects\art-pipeline` |
| `HF_HOME` | HF token + model cache | `C:\my\projects\hf` |

Scripts fail loudly naming the missing var — never silent defaults.

## 2. ComfyUI server

Patientx-cfz fork (stock ROCm 7.x lacks gfx1032 support on AMD RDNA2).
Launch equivalent of `start-comfyui.ps1` in this repo:

```
<COMFY_PYTHON> <COMFY_DIR>/main.py --listen 127.0.0.1 --port 8188 \
  --lowvram --disable-pinned-memory --preview-method auto --disable-auto-launch
```

Plus: AMD Adrenalin 26.x, `TdrDelay`/`TdrDdiDelay` = 60+, `TQDM_DISABLE=1`
(the launcher sets it — tqdm bars crash piped stderr, GPU then idles).

## 3. Checkpoints (download; sizes for planning)

| File | Source | Size | Use |
|---|---|---|---|
| `animagine-xl-4.0.safetensors` | HuggingFace `cagliostrolab/animagine-xl-4.0` | ~6.9 GB | characters (base) |
| `animagine-xl-4.0-opt.safetensors` | same repo, Opt variant | ~6.9 GB | characters (DEFAULT — anatomy wins) |
| `sd_xl_base_1.0.safetensors` | `stabilityai/stable-diffusion-xl-base-1.0` | ~6.9 GB | logos/marks |
| `sd_xl_turbo_1.0_fp16.safetensors` | `stabilityai/sdxl-turbo` | ~3.4 GB | drafts only |
| `RealESRGAN_x4plus.pth` | `xinntao/Real-ESRGAN` releases | ~64 MB | `esrgan.py` / `cupscale.py` |
| OpenPoseXL2 model | `thibaud/controlnet-openpose-sdxl-1.0` | ~5.0 GB | pose ControlNet (T-pose sheets) |

Custom nodes (via ComfyUI-Manager or git): `comfyui_controlnet_aux`
(DW pose estimators), `ComfyUI_IPAdapter_plus`, face detailer
(Impact Pack FaceDetailer preferred — record what worked).

## 4. Python venv (any venv; reference: Py3.12 + ROCm torch)

`rembg[cpu] Pillow numpy opencv-python` (+ `pymatting` for `dematte.py`,
`basicsr realesrgan` for `esrgan.py`, `trimesh` for mesh QA).

## 5. Verify (in order, stop at first red)

1. `python smoke.py` → `output/smoke.png` (Turbo 512px).
2. `esrgan.py --help` → usage (proves argparse; needs `ART_ESRGAN_MODEL`
   for real runs).
3. `python -m compileall <repo>` → zero errors.
4. ComfyUI `/` → 200 while up; connection-refused after stop.

## 6. Server discipline (BSOD precaution, observed 2026-10-16)

Restart the server between long batches; never leave it warm overnight;
one job at a time; prove it down after. Cause of the observed crash is
UNCONFIRMED — this rule is precaution, not diagnosis.
