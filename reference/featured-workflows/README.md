# Reference: recovered ComfyUI workflows (2026-10-13 brand-art run)

48 full API workflow JSONs extracted from raw ComfyUI outputs
(`C:\comfyui-rocm\output\opencode_00100_.png` … `opencode_00147_.png`)
with `tools/extract-workflow.py`. These runs produced the
`animedream` featured brand art (crowd + six solos) plus the session's
logo/icon/BG experiments.

Provenance chain that matters:

- `00119`–`00124`: group attempts on base `animagine-xl-4.0`
  (anatomy all over the place).
- `00125`+: switch to **`animagine-xl-4.0-opt`** — instant anatomy fix;
  every shipped solo runs Opt.
- Crowd = seeds 904–907 group-selfie iterations (framing → color → cast).
- Solos = seeds 911–916 (`kitsune 911 / pilot 912 / knight 913 /
  school 914 / pirate 915 / idol 916`), generous-margins + plain-studio
  phrasing.
- Refined faces = seeds 917–919, negatives extended with
  `deformed face, deformed eyes, asymmetrical eyes, crossed eyes,
  ugly face`.

Common settings: `euler_ancestral`, 27–28 steps, CFG 5.0, 1024² native.
See `skills/image-gen/SKILL.md` §1–3 for the distilled recipe.
