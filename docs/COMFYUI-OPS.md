# ComfyUI ops runbook (hard-won, read before scripting runs)

Companion to `MACHINE-SETUP.md` (install) and the `image-gen` skill
(recipes). This file is pure operations: how to start, probe, queue, and
stop the server without losing time. Portable env contract holds here —
`COMFY_URL`, `COMFY_DIR`, `COMFY_PYTHON` only, never machine paths.

## 1. Health probe (the bug that ate 7 minutes)

- NEVER probe the root page (`GET /`) with `Invoke-WebRequest` from a
  non-interactive/background shell. It ALWAYS fails there with
  `Windows PowerShell is in NonInteractive mode. Read and Prompt
  functionality is not available` — even when the server is up. A
  wait-loop on `/` therefore waits forever and concludes "server never
  came up" on a healthy server. (Witnessed 2026-10-16.)
- ALWAYS probe the API with `Invoke-RestMethod` instead:

```powershell
# ready when this answers; use it as the wait-loop condition
$q = Invoke-RestMethod -Uri "$env:COMFY_URL/queue" -TimeoutSec 8
"running=$($q.queue_running.Count) pending=$($q.queue_pending.Count)"
```

- `/system_stats` is an equivalent alternative. `/` in a browser is
  fine — the ban is only on `Invoke-WebRequest /` from automation.

## 2. Wait-loop budget

- Cold boot to ready takes MINUTES (model load + node init + registry
  fetch), not seconds. Budget at least 15 min (e.g. 60 × 15 s), polling
  `/queue`, and `echo` every attempt so a stuck waiter is visible in its
  log — an empty log means "still waiting", which must be
  distinguishable from "dead".
- Python submitters (`urllib` to `/prompt`) have no such problem — only
  the PowerShell probe was broken. Prefer: start server, poll `/queue`
  from the SAME Python script, submit when ready. One process, no
  two-shell race.

## 3. One queue, two clients

- Browser UI jobs and API-script jobs share ONE server queue. A browser
  prompt (random `client_id`) and a script prompt (your `client_id`,
  e.g. `rework35`) serialize — the second waits while the first runs
  (~110 s for a 1024² 8-step Z-Turbo gen on RX 6600 XT).
- "Why is my job waiting?" diagnosis order (all read-only, 30 s):
  1. `GET /queue` — `running`/`pending` empty means NOTHING is queued;
     the wait is on YOUR side (waiter/loop), not the server's.
  2. `GET /history` — your `client_id`/`prompt_id` absent means your job
     was never submitted. Present + `completed:false` means genuinely
     running — leave it alone.
  3. Waiter log — no `SERVER-UP` (or equivalent) line means the waiter
     never fired. Check for the §1 probe bug first.
  4. Process list — no submitter `python.exe` besides the server means
     nothing is even trying.

## 4. Single-job discipline (8 GB VRAM)

- Submit ONE gen at a time; the next only after the previous lands.
  Parallel prompts on gfx1032 thrash and slow everything.
- Keep ONE warm server for a whole batch (cold-start once per session,
  fresh process per the BSOD rule). The first gen of a boot pays model
  init (~30 s `Model Initialization`) plus slower early steps; later
  gens on the warm server run at full speed (~110 s per 1024² Z-Turbo
  8-step).

## 5. Stop + prove down
- After the batch: kill the server process, then PROVE the port is
  closed (`/queue` must refuse). A live process + dead port = hung
  teardown — clear it before the next session. Never leave a server
  running idle (BSOD precaution).

## 6. Every output embeds its UI workflow (mandatory since 2026-10-16)

- `SaveImage` embeds a `workflow` chunk ONLY if the `/prompt` request
  includes `extra_data.extra_pnginfo.workflow`. Raw `{prompt,
  client_id}` submissions produce PNGs with a `prompt` chunk alone —
  and "open as workflow" silently does nothing on those (diagnosed
  2026-10-16: script-made `shot3_action_v2_00001_.png -> ['prompt']` vs
  browser-made `ComfyUI_00001_.png -> ['prompt', 'workflow']`).
- Hence: ALL scripted gens go through `gen_z.py` (repo root), which
  patches `reference/z-image-turbo-int8/workflow.json` and ALWAYS sends
  it as `extra_data.extra_pnginfo.workflow`, plus writes a
  `<name>.workflow.json` sidecar next to the staged PNG. Raw API-only
  submissions are banned.
- Backfill tool for pre-rule images: `tools/embed_workflow.py --png ..
  --prompt .. --seed .. --prefix ..` (lossless: pixels verified
  identical, existing chunks preserved). Backfill the SERVER-side
  original in the ComfyUI output dir too — the Assets panel reads those
  files, so staged copies alone don't fix "open as workflow" from the UI.
- Unrelated look-alike: if the button fails even on workflow-carrying
  images, suspect the popup blocker (allow popups for the `COMFY_URL`
  origin) or a stale frontend (hard-refresh).
