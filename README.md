# art-pipeline — shared local image-gen workflow (ComfyUI + rembg)

Single source of truth for the generative-art pipeline used by
`noveldream` (visual-novel sprites/BGs) and `emberpact` (battler
tokens/arenas). Versioned with semver tags; apps consume it as a git
submodule pinned to a tag — never copy these scripts into an app repo.

Provenance: extracted 2026-10-11 from noveldream `tools/art/` at
noveldream@`4ecb3b2` (PR #13: vendored from `C:\AI\media\`, origin
snapshot kept as `WORKFLOW.orig.md`).

## Consuming (pinned, no drift)

In an app repo (mount point `tools/art`):

```powershell
git submodule add https://github.com/bloomstick/art-pipeline.git tools/art
git -C tools/art checkout v1.0.0
git add .gitmodules tools/art
```

Upgrading is always explicit: `git -C tools/art fetch --tags`,
`checkout vX.Y.Z`, verify (`python -m compileall tools/art`, regen one
known asset, compare), commit the pointer bump. Apps may pin different
tags — that is intentional and recorded in each app's
`docs/art-pipeline.md`. Worktrees/clones need
`git submodule update --init` once.

## Prerequisites (machine-level, one-time)

- ComfyUI server: `start-comfyui.ps1` (reference copy of
  `C:\AI\start-comfyui.ps1`) → `C:\comfyui-rocm\main.py --listen 127.0.0.1
  --port 8188 --lowvram --disable-pinned-memory --preview-method auto
  --disable-auto-launch` (patientx-cfz fork; stock ROCm 7.x lacks gfx1032
  support). Override URL/input dir per-run with `COMFY_URL` (default
  `http://127.0.0.1:8188`) and `COMFY_INPUT` (default
  `C:\comfyui-rocm\input`). Requires Adrenalin 26.x + TdrDelay/TdrDdiDelay=60+.
- Checkpoints in ComfyUI `models/checkpoints/`: `animagine-xl-4.0`
  + `animagine-xl-4.0-opt.safetensors` (Opt is the DEFAULT for all
  character/scene work: card-documented stability/anatomy wins, clean
  faces three runs straight including an 8-head crossover, Aniplace
  verdict 2026-10-13; noveldream keeps base 4.0 for single VN sprites
  per their 2026-10-11 A/B until they re-test),
  `sd_xl_base_1.0` (logos/marks — Opt is an illustration model, not a
  mark tool), `sd_xl_turbo_1.0_fp16` (drafts only).
  IPAdapter (`models/ipadapter` + `models/clip_vision`) for `ipa.py`.
  Upscaler `RealESRGAN_x4plus.pth` for `cupscale.py`.
- Python 3.12 with `rembg[cpu]`, `Pillow`, `numpy`, `opencv-python`
  (any venv; `C:\AI\venv` on this machine). `dematte.py` additionally needs
  `pymatting`. `svgprobe.py` is stdlib-only.
- VTracer binary (`C:\AI\tools\vtracer\vtracer`, external, not vendored —
  licensed third-party tool) for logo marks only.

## Scripts (in pipeline order)

| script | purpose |
|---|---|
| `smoke.py` | Server check: waits for ComfyUI, runs SDXL-Turbo 512px job (`smoke.py [OUT]`) |
| `gen.py` | ComfyUI txt2img. `--prompt --out [--ckpt --steps --cfg --sampler --scheduler --w --h --seed]` (defaults: 4-step Turbo 512 drafts at cfg 0.0 — finals MUST override ckpt/steps; Turbo never takes guidance or a negative prompt per its card) |
| `ipa.py` | Style-locked txt2img via IPAdapter (`--ref` style anchor, `--weight` default 0.5 locked, `--wtype`) |
| `refine.py` | img2img polish / expression variants (`--denoise`, expression-only prompt deltas) |
| `patch.py` | Surgical patch: crop `--box` → img2img repaint → feathered paste-back (anti-hallucination ladder step 1) |
| `cupscale.py` | ESRGAN upscale inside ComfyUI. OPAQUE ONLY, before masking |
| `esrgan.py` | Direct Real-ESRGAN x4 (tile-safe for 8 GB, CUDA→CPU fallback). Alternative to `cupscale.py` when ComfyUI is down |
| `upscale.py` | Pillow Lanczos fallback (CPU, always available) |
| `rmbg.py` | Cutout. `--model birefnet-general --dc` for sprites (see app pipeline docs) |
| `whiten.py` | Corner flood-fill to white (deterministic assist, unproven) |
| `key_white.py` | White-bg keying via border flood-fill + unblended edge band (`key_white.py IN OUT [thr]`) |
| `unwhite.py` | White-background removal by exact unblend (`unwhite.py IN OUT`) |
| `dematte.py` | Closed-form alpha matting refinement (`--rad`; needs `pymatting`) |
| `rmsig2.py` | Signature/cartouche removal via boxed Telea inpaint (`--box --thr`) |
| `finish_e5b.py` | Deterministic badge finish (connectivity/thickness/color rules, navy surround, circular mask; scale-aware flags for HD) |
| `finish_badge.py` | Ring-detect badge finish (Hough circle + vector-drawn gold border) |
| `finish_v2.py` / `finish_v3.py` | Badge finish alternates (radial annulus / elliptical keep) |
| `crop_circle.py` | Circular crop with transparent outside (`--cx --cy --r --feather`) |
| `pop_ears.py` | Badge with ears popping out (circle crop + upper light components pasted back) |
| `rectify.py` | Rectangular full-bleed: navy beyond disc + recenter emblem (`--inn --out [--ecx --ecy --r-fill --navy]`) |
| `atten.py` | Edge attenuation of near-white halo (`atten.py IN OUT [thr sat alph]`) |
| `magenta.py` | Verification: stats + magenta composite (`magenta.py IN OUT`) |
| `svgprobe.py` | Vector audit: fill-color census of VTracer SVG (`svgprobe.py [FILE]`) |
| `finish_upscale.py` | Fixed mapping: staging dir → 2048 webp assets (`--src-dir` defaults to `ART_SRC_DIR` env, `--assets-dir` defaults to the consuming repo's `assets/` dir) |
| `start-comfyui.ps1` | Reference copy of the ComfyUI launcher (run the `C:\AI\` original) |
| `opencode-media-tools.index.ts` | Reference copy of the global opencode plugin (Turbo-default `media_generate`; finals must override) |
| `WORKFLOW.orig.md` | Superseded origin doc from `C:\AI\media\` (provenance only) |

Not vendored (one-off debug, hardcoded single-file paths): `dbg.py`,
`dbg3.py`, `dbg4.py` (ComfyUI node probes), `makepal.py` (palette dump),
`rmsig.py` (superseded by parameterized `rmsig2.py`).

## Vectorizing illustrated art (VTracer recipe, proven 2026-10-13)

Defaults (`stacked` + color-cluster) posterize gradients and fuse
white-on-white. For flat anime/sticker art use
`--hierarchical cutout --clustering watershed` with a curated `--palette`
(+ chroma-key trick for transparency: composite the cutout onto pure
green, trace, drop green-dominant fills — stacked mode paints a
full-canvas underpaint slab, cutout does not). Finish with
`--simplify 1.5` and verify by rendering the SVG (Edge headless
screenshot), never by path counts alone. Small features the regions eat
(fangs, shines) get rebuilt from measured source pixels and spliced in.

## App recipes (live in the apps, not here)

- noveldream `docs/art-pipeline.md`: VN cast recipe, prompt templates,
  per-asset ledgers (`assets/cast/*.json`, `assets/bg/backgrounds.json`,
  `assets/cg/cgs.json`, `assets/cover.json`).
- emberpact `docs/art-pipeline.md`: unit-token / arena / icon recipes
  (UNPROVEN until run on the box), ledgers beside shipped assets.
