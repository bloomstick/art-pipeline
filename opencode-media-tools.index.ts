// Vendored reference copy of the global opencode `media-tools` plugin
// (live install: ~/.config/opencode/plugins/media-tools/index.ts).
// NOTE: media_generate defaults to 4-step SDXL-Turbo 1024 — VN finals MUST
// override ckpt/steps (see docs/art-pipeline.md §3). Kept for provenance;
// the repo pipeline runs via tools/art/*.py directly.
import { Plugin } from '@opencode/plugin'
import { execFile } from 'node:child_process'
import { promisify } from 'node:util'
import { writeFile } from 'node:fs/promises'
import { join } from 'node:path'

const run = promisify(execFile)
const COMFY = process.env.ART_COMFY_URL ?? 'http://127.0.0.1:8188'
const VENV_PY = process.env.ART_VENV_PY
const PIPELINE_DIR = process.env.ART_PIPELINE_DIR
if (!VENV_PY) throw new Error('ART_VENV_PY is not set (venv python; see art-pipeline docs/MACHINE-SETUP.md)')
if (!PIPELINE_DIR) throw new Error('ART_PIPELINE_DIR is not set (art-pipeline repo checkout; see docs/MACHINE-SETUP.md)')

function workflow(prompt: string, negative: string, ckpt: string, w: number, h: number, seed: number) {
  return {
    '1': { class_type: 'CheckpointLoaderSimple', inputs: { ckpt_name: ckpt } },
    '2': { class_type: 'CLIPTextEncode', inputs: { text: prompt, clip: ['1', 1] } },
    '3': { class_type: 'CLIPTextEncode', inputs: { text: negative, clip: ['1', 1] } },
    '4': { class_type: 'EmptyLatentImage', inputs: { width: w, height: h, batch_size: 1 } },
    '5': {
      class_type: 'KSampler',
      inputs: {
        model: ['1', 0], positive: ['2', 0], negative: ['3', 0], latent_image: ['4', 0],
        seed, steps: 4, cfg: 1.5, sampler_name: 'euler', scheduler: 'normal', denoise: 1.0,
      },
    },
    '6': { class_type: 'VAEDecode', inputs: { samples: ['5', 0], vae: ['1', 2] } },
    '7': { class_type: 'SaveImage', inputs: { images: ['6', 0], filename_prefix: 'opencode' } },
  }
}

async function generate(prompt: string, out: string, opts: { ckpt?: string; w?: number; h?: number; seed?: number }, signal?: AbortSignal) {
  const ckpt = opts.ckpt ?? 'sd_xl_turbo_1.0_fp16.safetensors'
  const w = opts.w ?? 1024
  const h = opts.h ?? 1024
  const seed = opts.seed ?? Math.floor(Math.random() * 2 ** 31)
  const client = `opencode-${Date.now()}`
  const res = await fetch(`${COMFY}/prompt`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ prompt: workflow(prompt, '', ckpt, w, h, seed), client_id: client }),
    signal,
  })
  if (!res.ok) throw new Error(`ComfyUI /prompt ${res.status}: ${await res.text()}. Is the ComfyUI server running? (ART_COMFY_URL=${COMFY}; see art-pipeline docs/MACHINE-SETUP.md)`)
  const { prompt_id } = (await res.json()) as { prompt_id: string }
  for (let i = 0; i < 120; i++) {
    if (signal?.aborted) throw new Error('aborted')
    await new Promise((r) => setTimeout(r, 5000))
    const hres = await fetch(`${COMFY}/history/${prompt_id}`, { signal })
    if (!hres.ok) continue
    const hist = (await hres.json()) as Record<string, any>
    const entry = hist[prompt_id]
    if (!entry?.status?.completed) continue
    const images = entry.outputs?.['7']?.images
    if (!images?.length) throw new Error(`no images in ${prompt_id}`)
    const img = images[0]
    const vres = await fetch(
      `${COMFY}/view?filename=${encodeURIComponent(img.filename)}&subfolder=${encodeURIComponent(img.subfolder ?? '')}&type=${img.type ?? 'output'}`,
      { signal },
    )
    if (!vres.ok) throw new Error(`ComfyUI /view ${vres.status}`)
    await writeFile(out, Buffer.from(await vres.arrayBuffer()))
    return out
  }
  throw new Error('timed out waiting for ComfyUI')
}

export default Plugin.define({
  id: 'media-tools',
  async setup(ctx) {
    await ctx.tool.transform((editor) => {
      editor.namespace({ name: 'media', description: 'Local brand asset pipeline (ComfyUI + Pillow + rembg)' })
      editor.add({
        name: 'generate',
        description: 'Generate a PNG locally with ComfyUI. Requires the ComfyUI server running (ART_COMFY_URL).',
        input: {
          type: 'object',
          properties: {
            prompt: { type: 'string' },
            out: { type: 'string', description: 'Absolute output path, e.g. asset file in the app repo' },
            ckpt: { type: 'string' },
            w: { type: 'number' },
            h: { type: 'number' },
            seed: { type: 'number' },
          },
          required: ['prompt', 'out'],
          additionalProperties: false,
        },
        options: { namespace: 'media', codemode: true },
        execute: async (input, context) => {
          const { prompt, out, ...rest } = input as { prompt: string; out: string } & Record<string, number | string>
          await context.progress({ status: 'generating' })
          const file = await generate(prompt, out, rest as any, context.signal)
          return { content: `generated ${file}` }
        },
      })
      editor.add({
        name: 'upscale',
        description: 'Upscale a PNG with Pillow (CPU).',
        input: {
          type: 'object',
          properties: {
            inn: { type: 'string' },
            out: { type: 'string' },
            scale: { type: 'number' },
          },
          required: ['inn', 'out'],
          additionalProperties: false,
        },
        options: { namespace: 'media', codemode: true },
        execute: async (input, context) => {
          const { inn, out, scale } = input as { inn: string; out: string; scale?: number }
          await context.progress({ status: 'upscaling' })
          await run(VENV_PY, [join(PIPELINE_DIR, 'upscale.py'), '--inn', inn, '--out', out, '--scale', String(scale ?? 2)], { signal: context.signal as any })
          return { content: `upscaled ${out}` }
        },
      })
      editor.add({
        name: 'rmbg',
        description: 'Remove image background with rembg (isnet-general-use).',
        input: {
          type: 'object',
          properties: { inn: { type: 'string' }, out: { type: 'string' } },
          required: ['inn', 'out'],
          additionalProperties: false,
        },
        options: { namespace: 'media', codemode: true },
        execute: async (input, context) => {
          const { inn, out } = input as { inn: string; out: string }
          await context.progress({ status: 'removing background' })
          await run(VENV_PY, [join(PIPELINE_DIR, 'rmbg.py'), '--inn', inn, '--out', out], { signal: context.signal as any })
          return { content: `background removed ${out}` }
        },
      })
    })
  },
})
