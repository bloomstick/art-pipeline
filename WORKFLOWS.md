# Workflow Index (image pipeline only)

Every image workflow in one place. Non-image workflows live with their own
repos and are NOT indexed here — this file, like the repo, has no outward
dependencies. Consuming projects point AT this repo (submodule pin +
`image-gen` skill); nothing here points back out.

| # | Workflow | Trigger (use when…) | Cost | Last proven |
|---|---|---|---|---|
| 1 | [anime concept](#1-anime-concept) | anime character/concept art, correct anatomy | ~2–7 min/image (RX 6600 XT) | 2026-10-16 |
| 2 | [face detailer](#2-face-detailer) | close-up face quality on anime gens | +1–2 min | 2026-10-16 (pending owner QC) |
| 3 | [4-view turnaround](#3-4-view-turnaround) | character reference for 3D (front/sides/back) | TBD (in flight) | — |
| 4 | [finish + verify](#4-finish--verify) | cutout/upscale/verify of generated art | seconds–minutes | 2026-10 (standing) |
| 5 | [recovery](#5-recovery) | unledgered images whose settings are lost | minutes | 2026-10-16 |

Full canonical workflow (setup, recipes, negatives, ledger rule):
`skills/image-gen/SKILL.md`.

## Entries

### 1. anime concept

- **Recipe:** `skills/image-gen/SKILL.md` §1 (animagine-xl-4.0-**opt**,
  euler_ancestral 28 / CFG 5, native buckets) + §2 prompt patterns + §3
  layered negatives. Crash ban + AMD path per skill §0.
- **Reference runs:** `reference/featured-workflows/` (48 workflows +
  provenance README).

### 2. face detailer

- Impact Pack FaceDetailer preferred (install if absent, record version);
  fallback named with reason. RealESRGAN-upscale alone is NOT a face
  detailer. Ledger MUST name what ran.

### 3. 4-view turnaround

- Winning look → seed-locked img2img per view + IPAdapter identity
  reference; consistency graded per view. SF3D input cut from front view
  (rembg + square crop → 1024px).

### 4. finish + verify

- Order: upscale opaque BEFORE masking → rembg → verify on magenta
  composite + pixel audit. Scripts: `cupscale.py`/`esrgan.py`,
  `rmbg.py`, `magenta.py` (quick-look), `verify.py` (JSON census:
  `has_alpha/transparent_pct/magenta_visible_pct/near_white_pct`),
  `finish_*.py` (see README table).

### 5. recovery

- `tools/extract-workflow.py <png> --outdir DIR` dumps embedded ComfyUI
  workflows. Works only on raw outputs (re-exports strip metadata).
  Recovered artifacts commit under `reference/` with a provenance README.

## Governance (binding)

- ALL image work in every project runs through this repo: consume via
  submodule pin (`tools/art`) + the `image-gen` skill. No parallel image
  pipelines, no vendored copies drifting in app repos.
- Amendments land HERE as commits (semver: fixes PATCH, scripts/recipes
  MINOR, breaking env/flag changes MAJOR). Project-specific recipes stay
  in the consuming projects and reference upstream versions, never fork logic.
- Provenance rule: no workflow counts as proven without its ledger row.
