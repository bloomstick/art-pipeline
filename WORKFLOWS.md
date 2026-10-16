# Workflow Catalog

One index for every proven workflow across all projects. Pick the right
workflow on the first attempt: match your situation to a Trigger, follow
the recipe, append your ledger row. No rediscovery.

## Rule (binding)

A workflow counts as **proven** only with its ledger row (date, inputs,
cost, output pointer). Unledgered runs are anecdotes, not workflows —
this catalog exists because unrecorded runs cost us the `featured/`
generation settings (Oct 2026, unrecoverable).

## Index

| # | Workflow | Trigger (use when…) | Lives | Cost | Last proven |
|---|---|---|---|---|---|
| 1 | [goal-loop](#1-goal-loop--code-loop) | multi-step code task, 2+ file-disjoint parts | `opencode-goal-loop` repo + global skill | model time | 2026-10-16 |
| 2 | [subagent dispatch](#2-subagent-dispatch) | parallel research or delegation inside a session | global (`default.subagent`) | model time | 2026-10-15 |
| 3 | [anime concept (ComfyUI)](#3-anime-concept-comfyui) | anime character/concept art, correct anatomy | `C:\comfyui-rocm`, recipes below | ~2–7 min/image (RX 6600 XT) | 2026-10-16 |
| 4 | [face detailer](#4-face-detailer) | close-up face quality on anime gens | ComfyUI custom nodes | +1–2 min | 2026-10-16 (pending proof) |
| 5 | [4-view turnaround sheet](#5-4-view-turnaround-sheet) | character reference for 3D (front/sides/back) | ComfyUI (seed-lock + identity ref) | TBD (in flight) | — |
| 6 | [image-to-3D bake-off](#6-image-to-3d-bake-off) | choosing a mesh backend on your hardware | `C:\Python314` venvs, `HF_HOME=C:\my\projects\hf` | ~1–8 min/candidate | 2026-10-16 |
| 7 | [3D generative pipeline](#7-3d-generative-pipeline) | concept→mesh→rig→animate→Godot character | `project-FATHER` (`characters/heroine_final/`, `tools/gen3d/`) | ~15 min char (CPU) | 2026-10-16 (loose bar) |
| 8 | [TripoSR CPU accessory](#8-triposr-cpu-accessory) | single accessory/part mesh from image | `C:\AI\triposr-src` + `tripo_infer_cpu.py` | ~8 min | 2026-10-15 |
| 9 | [Godot headless proof](#9-godot-headless-proof) | validating a GLB in-engine without the editor | Godot 4.7.2 binary | ~1 min | 2026-10-16 |
| 10 | [dream-monorepo merge + release](#10-dream-monorepo-merge--release) | landing work / cutting a release in dream-monorepo | `dart tools/merge_to_main.dart`, `dart tools/release.dart` | minutes | 2026-10 (standing) |
| 11 | [HF gated weights setup](#11-hf-gated-weights-setup) | 401-gated model download (SF3D etc.) | `C:\Python314\Scripts\hf.exe`, `HF_HOME=C:\my\projects\hf` | one-time ~10 min | 2026-10-15 |

## Entries

### 1. goal-loop — code loop

- **Trigger:** requirements→verified-code, hands-off; 2+ file-disjoint parts.
- **Recipe:** `/goal <task>` → clarify → `reqs-manifest.md` → DAG → one
  worktree+branch per worker via `subagent` (fallback foreground
  `opencode run`) → checker verdict per run → integrate one-by-one to
  `main` → LAND proof (`ls-remote` == local + contains) → DONE block.
- **Never:** background runs, schedules, silent stops; one invocation ends.
- **Ledger:** the manifest itself (`Runs` + `Log`); goal branch pushed
  after every mutation.
- **Source of truth:** `C:\my\projects\opencode-goal-loop` (skill + agents).

### 2. subagent dispatch

- **Trigger:** parallel research/delegation inside a session.
- **Recipe:** one `default.subagent` call per message (`agent`,
  `description`, self-contained `prompt`); `sessionID` continues;
  `background:true` only for independent work. NEVER set `model`.
  Resend needs `agent` + `sessionID` both.
- **Proof:** 3 parallel research agents 2026-10-15; full spec in
  `project-FATHER/docs/subagents.md`.

### 3. anime concept (ComfyUI)

- **Trigger:** anime character/concept art with correct anatomy.
- **Recipe:** animagine-xl-4.0 at NATIVE buckets (832×1216 portrait,
  1024² square) + `euler_ancestral` 28 steps / CFG 5.0 + anatomy negative
  (`bad anatomy, bad hands, extra digits…`). Drafts: turbo_fp16, euler,
  1–4 steps, CFG 0, 512px.
- **Crash ban (RX 6600 XT, measured):** plain `euler` above 512px kills the
  GPU — enforced in `project-FATHER/tools/comfy/gen.py`.
- **AMD path:** ROCm via patientx-cfz fork (TheRock nightly builds — official
  ROCm 7.x lacks gfx1032) + Adrenalin 26.x + TdrDelay/TdrDdiDelay=60+;
  live server is `C:\comfyui-rocm`, NOT `C:\AI`. Opt variant
  (`animagine-xl-4.0-opt`) is the default for character/scene work.
- **Batch discipline:** batches of 3 candidates, pick best; optional
  img2img refine at low denoise for finalists. Never ship Turbo raw;
  upscale opaque BEFORE masking; magenta-composite verification only.
  Full recipe: `C:\AI\media\WORKFLOW.md` (2026-10-04).
- **Ledger:** prompt/seed/checkpoint/sampler/steps/CFG + sha256 beside the
  asset, always. (Missing ledgers = the `featured/` loss.)

### 4. face detailer

- **Trigger:** close-up face quality (eyes resolve at 1024px).
- **Recipe:** Impact Pack FaceDetailer preferred (install if absent, record
  version); fallback hires-fix/bbox refiner — worker NAMES what worked.
- **Status:** in flight on heroine-final HF-01 rework; entry graduates on
  owner QC pass.

### 5. 4-view turnaround sheet

- **Trigger:** character reference for 3D: front, left, right, back, same
  outfit/face.
- **Recipe (pending proof):** winning look → seed-locked img2img per view
  + IPAdapter identity reference; consistency graded per view in ledger.
- **Status:** required deliverable of heroine-final HF-01; entry graduates
  on acceptance.

### 6. image-to-3D bake-off

- **Trigger:** choosing a mesh backend on YOUR hardware.
- **Recipe:** same input image × candidates (SF3D / TripoSR / Hunyuan),
  stock settings; judge front likeness, back coherence, topology,
  texture, wall time, VRAM, license. Winner + evidence table or the
  decision is void. 200MB committed-binary cap.
- **Known results (RX 6600 XT, no CUDA):** TripoSR CPU 468s watertight
  36.5k tris MIT; SF3D CPU 73s textured + quad 9,856f (needs HF login,
  Stability <$1M license); Hunyuan NO-GO (74GB weights, territorial
  license). Full table: `project-FATHER/docs/3dgen-bench*.md`.

### 7. 3D generative pipeline

- **Trigger:** full character concept→mesh→rig→animate→Godot.
- **Recipe:** run-guide `project-FATHER/docs/3dgen-pipeline.md`
  (env → bench → concept → mesh → rig → anim-qa → sunset).
- **Budgets:** ≤30k tris, <60 bones, 1024 textures (from art-style).
- **Status:** proven loose-bar 2026-10-16; strict-bar pass in flight
  (heroine-final).

### 8. TripoSR CPU accessory

- **Trigger:** single part mesh from one image.
- **Recipe:** `C:\AI\tripo_infer_cpu.py` + cleanup + kit-mount pattern
  (earmodule/hairpin landed in idle-stance).
- **Note:** full-mesh fallback if SF3D ever blocked; backs are weak.

### 9. Godot headless proof

- **Trigger:** engine validation of a GLB without opening the editor.
- **Recipe:** `godot --headless` import (0 ERROR required) + scripted
  scene boot with the asset + renders. Pattern in idle-stance and
  `docs/3dgen-qa.md`.

### 10. dream-monorepo merge + release

- **Trigger:** landing / releasing in dream-monorepo ONLY.
- **Recipe:** `dart tools/merge_to_main.dart acquire→merge→finish→release`
  (ONLY supported path; never hand-merge in the main worktree); releases
  via `dart tools/release.dart`; tags one ref per push.
- **Do NOT use in other repos** (solo repos merge locally per goal-loop).

### 11. HF gated weights setup

- **Trigger:** `401 GatedRepoError` on a model download.
- **Recipe:** token (Read) at `huggingface.co/settings/tokens` → accept
  gated terms on the model page → `C:\Python314\Scripts\hf.exe auth login`
  (v2.x CLI is `hf`, NOT `huggingface-cli`) with
  `HF_HOME=C:\my\projects\hf` set (token + weights land there).
- **Gotcha:** CMD vs PowerShell env syntax; fresh terminal for `setx` vars.

## Contributing

New entry = recipe + first ledger row in the same commit. Amendments quote
the run that taught them. Anything cited here without a ledger pointer
gets challenged.
