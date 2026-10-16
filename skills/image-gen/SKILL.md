---
name: image-gen
description: Canonical local anime image-generation workflow (ComfyUI + AMD RX 6600 XT). Use for ANY anime character/concept/splash task: setup, proven recipes, anatomy negatives, face detailing, turnaround sheets, and the mandatory ledger rule. Encodes all experience to date — follow it instead of rediscovering.
---

# image-gen — canonical anime generation workflow

## 0. Machine setup (do once, verify per session)

- Server: `C:\AI\start-comfyui.ps1` → patientx-cfz fork `main.py --listen
  127.0.0.1 --port 8188 --lowvram --disable-pinned-memory --preview-method
  auto --disable-auto-launch`. LIVE instance is `C:\comfyui-rocm`
  (stock `C:\AI\ComfyUI` stays untouched).
- GPU: AMD RX 6600 XT (gfx1032) via TheRock nightly builds — official ROCm
  7.x lacks gfx1032. Adrenalin 26.x + TdrDelay/TdrDdiDelay=60+.
- Checkpoints (`models/checkpoints/`): `animagine-xl-4.0` + **`-opt`
  (DEFAULT for all character/scene work — card-documented anatomy wins)**,
  `sd_xl_base_1.0` (logos/marks), `sd_xl_turbo_1.0_fp16` (drafts only).
- Gated downloads: `hf` CLI (`C:\Python314\Scripts\hf.exe`, v2.x name —
  `huggingface-cli` is dead) with `HF_HOME=C:\my\projects\hf`.
- Crash ban (measured): plain `euler` above 512px kills the GPU. Finals use
  `euler_ancestral` (Animagine) or `dpmpp_2m/karras` (SDXL base).
  `tools/comfy/gen.py`-style clients must enforce this (exit, don't run).

## 1. Recipe table (start here, deviate only with a ledger note)

| use | ckpt | sampler / sched | steps / CFG | size |
|---|---|---|---|---|
| smoke probe | turbo_fp16 | euler / normal | 1–4 / 0.0 | 512 |
| character sheet (final) | animagine-xl-4.0-**opt** | euler_ancestral / normal | 28 / 5.0 | 832×1216 portrait, 1024² square |
| logos/marks | sd_xl_base_1.0 | dpmpp_2m / karras | 40 / 7.0 | 1024² native |
| drafts (never ship) | turbo_fp16 | euler / normal | 1–4 / 0.0 | 512 |

Native buckets only — off-bucket sizes degrade anatomy by themselves.

## 2. Prompt patterns

- Tag-style, comma phrases. Composition guards always:
  `centered with generous margins on all sides`, `facing viewer`,
  `full body` (forces complete bodies, no cropped torsos).
- Character sheets: `character reference sheet`, plain white/light
  background, `neutral expression`, outfit locked per phrase.
- Provenance: the `featured/` quality run (seeds 911–919) is archived with
  full workflows at `C:\my\projects\hf\featured_meta\` — steal structure
  from those prompts before inventing.

## 3. Negative blocks (layered — use ALL THREE for characters)

1. Base: `lowres, bad anatomy, bad hands, text, error, missing finger,
   extra digits, fewer digits, cropped, worst quality, low quality,
   low score, bad score, average score, signature, watermark`
2. Face (the sharp-eyes upgrade): `deformed face, deformed eyes,
   asymmetrical eyes, crossed eyes, ugly face`
3. Task-specific: photorealistic/3d/neon/monochrome exclusions per brief.

## 4. Face detailing (mandatory for close-up quality)

- Impact Pack FaceDetailer preferred; install if absent and RECORD version.
  Fallback (hires-fix / bbox refiner / RealESRGAN upscale) allowed ONLY
  with the reason named. RealESRGAN-upscale alone is NOT a face detailer.
- Ledger MUST name which detailer ran (answers "are you using it" with
  evidence, not memory).

## 5. Turnaround sheets (character reference for 3D)

- Deliverable: front, left side, right side, back — same outfit/face.
  Posed splash art is never a concept.
- Method: winning look → seed-locked img2img per view + IPAdapter identity
  reference; grade consistency per view in the ledger.
- SF3D input: rembg + square center-crop → 1024px, cut from the FRONT view.

## 6. Batch + finish discipline

- Batches of 3 candidates, pick best with written reasons; img2img refine
  at low denoise for finalists only. Never ship Turbo raw.
- Cutouts: upscale opaque BEFORE masking (upscalers invent detail in
  transparent zones); rembg isnet-general-use; verify on magenta
  composite `(255,0,255)` + pixel audit, never eyeballed previews.

## 7. LEDGER RULE (binding — the reason this skill exists)

Every shipped image carries its generation record. Minimum: checkpoint,
full positive + negative prompt, seed, sampler/scheduler/steps/CFG, size,
device flags, detailer + installs with sizes, output sha256. Store as
`<asset-name>.json` (or ledger.md row) BESIDE the asset, same commit.
Never strip PNG workflow metadata before ledgering. An unledgered image is
an anecdote — unrepeatable by design (see: the `featured/` loss,
recovered only from raw ComfyUI outputs).
