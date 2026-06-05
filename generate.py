#!/usr/bin/env python3
"""verse-to-prompt demo generator.

Reads attempts.json, generates one image per attempt via fal.ai z-image/turbo,
and ties EVERY image to the exact verse + prompt + seed that produced it:

  images/<verse>__<approach>.png   the image
  images/<verse>__<approach>.json  sidecar: verse text, prompt, seed, model, url
  manifest.json                    full table the viewer renders from
  runs.jsonl                       append-only log of every generation (audit trail)

Same model + same seed for every attempt -> the prompt is the only variable.
"""
import json, os, sys, time, urllib.request, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
IMG = ROOT / "images"; IMG.mkdir(exist_ok=True)

def fal_key():
    # 1) environment variable (recommended), 2) an env file pointed to by FAL_ENV_FILE.
    # No private paths are hardcoded — safe for a public repo.
    if os.environ.get("FAL_API_KEY"):
        return os.environ["FAL_API_KEY"].strip()
    env_file = os.environ.get("FAL_ENV_FILE")
    if env_file and pathlib.Path(env_file).exists():
        for line in pathlib.Path(env_file).read_text().splitlines():
            if line.startswith("FAL_API_KEY="):
                return line.split("=", 1)[1].strip()
    sys.exit("Set FAL_API_KEY in your environment (export FAL_API_KEY=...) "
             "or point FAL_ENV_FILE at a file containing FAL_API_KEY=...")

def post(url, payload, headers):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())

def main():
    cfg = json.loads((ROOT / "attempts.json").read_text())
    verses = cfg["verses"]  # embedded; the demo is self-contained
    key = fal_key()
    model, size, seed = cfg["model"], cfg["image_size"], cfg["seed"]
    headers = {"Authorization": f"Key {key}", "Content-Type": "application/json"}
    runs = ROOT / "runs.jsonl"
    manifest = []

    for a in cfg["attempts"]:
        vk = a["verse_key"]; v = verses[vk]
        aid = f"{vk}__{a['approach']}"
        print(f"[{aid}] generating ...", flush=True)
        res = post(f"https://fal.run/{model}",
                   {"prompt": a["prompt"], "image_size": size,
                    "num_images": 1, "seed": seed}, headers)
        img = res["images"][0]
        png = IMG / f"{aid}.png"
        with urllib.request.urlopen(img["url"], timeout=120) as r:
            png.write_bytes(r.read())

        record = {
            "id": aid,
            "verse_key": vk,
            "transition": v["transition"],
            "verse_zh": v["zh"],
            "verse_en": v["en"],
            "approach": a["approach"],
            "style": a.get("style"),
            "note": a.get("note"),
            "prompt": a["prompt"],
            "model": model,
            "seed": seed,
            "returned_seed": res.get("seed"),
            "image": f"images/{aid}.png",
            "source_url": img["url"],
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        (IMG / f"{aid}.json").write_text(json.dumps(record, ensure_ascii=False, indent=2))
        with runs.open("a") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        manifest.append(record)
        print(f"[{aid}] saved -> {record['image']}")

    (ROOT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    # manifest.js lets index.html render over file:// (no fetch / CORS needed for a live demo)
    (ROOT / "manifest.js").write_text(
        "window.MANIFEST = " + json.dumps(manifest, ensure_ascii=False, indent=2) + ";\n")
    print(f"\nWrote manifest.json + manifest.js ({len(manifest)} attempts). Open index.html to compare.")

if __name__ == "__main__":
    main()
