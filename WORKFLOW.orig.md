# Local brand-asset workflow (RX 6600 XT 8GB, Windows)

Proven recipe as of 2026-10-04. All scripts in `C:\AI\media\`, venv `C:\AI\venv`
(Py3.12 + ROCm torch), server `C:\comfyui-rocm` (patientx-cfz fork, RDNA2 builds).

## Server

```
C:\AI\start-comfyui.ps1   # fork python + main.py --lowvram --disable-pinned-memory --port 8188
```

Needs AMD Adrenalin 26.x + TdrDelay/TdrDdiDelay=60+ (see `tdr-fix.reg` in temp).
Official ROCm 7.x does NOT support gfx1032 — the fork's TheRock nightly builds do.

## Models (`C:\comfyui-rocm\models\checkpoints\`)

- `animagine-xl-4.0.safetensors` — DEFAULT for characters/mascots. MUST use its
  documented settings: Euler Ancestral, 25-28 steps, CFG 5, 1024-class res,
  tag-style prompts. It fails badly off-spec (do NOT judge it otherwise).
- `sd_xl_base_1.0.safetensors` — logos/marks (QUALITY DEFAULTS: 40 steps, cfg 7,
  dpmpp_2m/karras, batches of 3 candidates, pick best; optional img2img refine
  pass at low denoise for finalists)
- `sd_xl_turbo_1.0_fp16.safetensors` — fast drafts only (4 steps, rough)
- `animagine-xl-4.0.safetensors` — characters (tag prompts, euler_a); NOT logos
- Upscaler `C:\comfyui-rocm\models\upscale_models\RealESRGAN_x4plus.pth` via ComfyUI node

## Pipeline (scripts take --help-ish args, see headers)

1. `gen.py` — ComfyUI API txt2img. STABLE: 512px euler / 1024px dpmpp_2m+karras.
   1024+euler crashes this GPU (hipErrorLaunchFailure). Never exceed proven sizes.
2. `cupscale.py` — ESRGAN inside ComfyUI (`ImageUpscaleWithModel`; this fork's
   node name, not UpscaleImageUsingModel). OPAQUE images only: it drops alpha
   and invents detail in transparent zones. Upscale BEFORE masking, never after.
3. `rmbg.py` — rembg isnet-general-use (venv CPU torch).
4. `finish_e5b.py` — deterministic badge finish: medallion+cat kept via
   connectivity/thickness/color rules, navy surround, circular transparent mask.
   Scale-aware flags (--dilate/--open-k/--min-cat/--feather) for HD sources.
5. `crop_circle.py` / `pop_ears.py` / `finish_v2.py` / `finish_v3.py` — alternates.
6. `rectify.py` — rectangular full-bleed: navy beyond disc + recenter emblem.
7. VTracer `C:\AI\tools\vtracer\vtracer` — vectorize. Recipe: `--mode spline
   --color-precision 4 --filter-speckle 8` + curated `--palette` (never let it
   invent grays; audit fills with `svgprobe.py`).

## Verification rules (learned the hard way)

- Image previews show RGB through transparency — ONLY magenta composites count:
  paste onto (255,0,255) and view that.
- Pixel audits (numpy alpha/color counts) beat eyeballing downscaled previews.
- ESRGAN and Turbo hallucinate: never upscale masked art, never ship Turbo raw.

## opencode integration

Global plugin `media-tools` (`~/.config/opencode/plugins/media-tools`):
`media_generate` (ComfyUI 4-step), `media_upscale` (Pillow), `media_rmbg`.
Takes effect on opencode restart.
