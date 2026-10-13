# Changelog — art-pipeline

Shared image-gen workflow. Semver tags (`vMAJOR.MINOR.PATCH`); apps pin
`tools/art` to a tag via submodule. Pipeline fixes bump PATCH, new
scripts/recipes bump MINOR, breaking flag/model changes bump MAJOR.

## [Unreleased]

### Added

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
