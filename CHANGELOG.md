# Changelog — art-pipeline

Shared image-gen workflow. Semver tags (`vMAJOR.MINOR.PATCH`); apps pin
`tools/art` to a tag via submodule. Pipeline fixes bump PATCH, new
scripts/recipes bump MINOR, breaking flag/model changes bump MAJOR.

## [2.0.0] - 2026-10-16 (BREAKING: portable env contract, no local paths)

- Env contract replaces every machine default: `COMFY_URL` (default
  127.0.0.1:8188), `COMFY_INPUT` (REQUIRED), `ART_OUTPUT_DIR` (default
  repo `output/`), `ART_ESRGAN_MODEL` (REQUIRED), `COMFY_DIR` +
  `COMFY_PYTHON` (launcher), `ART_VENV_PY` + `ART_PIPELINE_DIR` (plugin).
  Scripts fail loudly naming the missing var. Old `C:\` defaults are gone.
- `output/` staging dir (git-ignored): generate + curate here, copy good
  results into projects, never commit.
- `docs/MACHINE-SETUP.md`: install instructions only (checkpoints table
  with sizes/sources, nodes, env table, verify steps). No models in repo.
- `scripts/Install-ArtPipeline.ps1`: installs `image-gen` skill globally,
  checks env (never sets machine state).
- Canonical `skills/image-gen/SKILL.md` (setup, recipes, layered
  negatives, face-detailer mandate, turnaround, ledger rule).
- `reference/featured-workflows/`: 48 recovered ComfyUI workflows + README.
- `tools/extract-workflow.py`: dump embedded PNG workflows to JSON.
- Places map in README (repo vs machine-local vs scratch vs ephemeral).

## [Unreleased]

- `verify.py`: cutout verification (magenta composite + JSON pixel audit:
  `w,h,has_alpha,transparent_pct,magenta_visible_pct,near_white_pct`),
  ported from the last FATHER-side image tool with own logic
  (`tools/comfy/verify.py`, retired in the single-pipeline
  consolidation). `magenta.py` kept as-is (quick-look composite).

## [2.0.1] - 2026-10-16

- Governance (binding): ALL image work in every project runs through
  this repo; amendments land here, no parallel pipelines. WORKFLOWS.md
  trimmed to image-only (cross-domain entries removed — those live with
  their own repos).

(nothing pending)

## [1.1.0]

- Opt checkpoint guidance: `animagine-xl-4.0-opt` is the default for
  all character/scene work (card-documented stability/anatomy; clean
  faces three runs straight, Aniplace 2026-10-13). Base 4.0 stays only
  for single VN sprites (noveldream 2026-10-11 A/B stands) and
  `sd_xl_base_1.0` stays the mark tool.
- VTracer recipe for illustrated art: watershed + cutout + curated
  palette, chroma-key transparency handling, `--simplify 1.5`, and
  render-based (not path-count) verification.

## [1.0.0] - 2026-10-11

### Added

- Initial extraction from noveldream `tools/art/` at noveldream@`4ecb3b2`
  (25 scripts: `gen`, `ipa`, `refine`, `patch`, `smoke`, `cupscale`,
  `esrgan`, `upscale`, `rmbg` default `birefnet-general`, `whiten`,
  `key_white`, `unwhite`, `dematte`, `rmsig2`, `finish_e5b/badge/v2/v3`,
  `crop_circle`, `pop_ears`, parameterized `rectify`, `atten`,
  `magenta`, `svgprobe`, parameterized `finish_upscale`) plus launcher,
  opencode-plugin, and `WORKFLOW.orig.md` provenance copies.
