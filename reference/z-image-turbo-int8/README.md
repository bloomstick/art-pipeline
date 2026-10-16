# Z-Image-Turbo int8 (local, RX 6600 XT)

Canonical UI workflow for the seed-locked character/scene pipeline behind
the CA-01 scene set and the shot-3/shot-5 v2 re-rolls (visual-novel
direction, project-FATHER `cinematic-art-2-5d`).

- `workflow.json` — the graph. Placeholders: `__POSITIVE__` (node 67),
  `__NEGATIVE__` (node 71), seed = first widget of node 70 (default 1),
  `__PREFIX__` (SaveImage node 9). Everything else is frozen: UNET
  `z_image_turbo_int8_convrot`, CLIP `qwen_3_4b_fp8_mixed` (`lumina2`),
  VAE `ae`, AuraFlow shift 3.0, KSampler `res_multistep`/`simple`,
  8 steps / CFG 1.0, 1024².
- Provenance: graph structure copied from a working browser session
  (frontend 1.53.10); node set identical to the API scripts that produced
  `shot3_action_v2` (seed 848272900) and `shot5_back34_v2` (seed
  848272835) on 2026-10-16. Per-image workflow sidecars (exact texts +
  seeds) sit next to the staged PNGs in `output/`, and the `workflow`
  chunk is embedded in the PNGs themselves.
- Submitter: `gen_z.py` (repo root) patches this template and ALWAYS
  sends it as `extra_data.extra_pnginfo.workflow`, so every output is
  one-click reloadable. Raw API-only submissions (no `extra_data`) are
  banned by `docs/COMFYUI-OPS.md` §6.
