#!/usr/bin/env python3
"""Generate tech-noir-v2 + stipple matrix images for the verse-to-prompt demo.

Reads attempts-matrix.json, generates images via fal.ai z-image/turbo,
and produces manifest-matrix.js for matrix.html.
"""
import json, os, sys, time, urllib.request, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
IMG = ROOT / "images"
IMG.mkdir(exist_ok=True)

def fal_key():
    if os.environ.get("FAL_API_KEY"):
        return os.environ["FAL_API_KEY"].strip()
    env_file = os.environ.get("FAL_ENV_FILE")
    if env_file and pathlib.Path(env_file).exists():
        for line in pathlib.Path(env_file).read_text().splitlines():
            if line.startswith("FAL_API_KEY="):
                return line.split("=", 1)[1].strip()
    sys.exit("Set FAL_API_KEY in your environment or point FAL_ENV_FILE at a .env file.")

def post(url, payload, headers):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())

def main():
    cfg = json.loads((ROOT / "attempts-matrix.json").read_text())
    verses = cfg["verses"]
    key = fal_key()
    model, size, seed = cfg["model"], cfg["image_size"], cfg["seed"]
    headers = {"Authorization": f"Key {key}", "Content-Type": "application/json"}
    manifest = []

    for a in cfg["attempts"]:
        vk = a["verse_key"]
        v = verses[vk]
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
        manifest.append(record)
        print(f"[{aid}] saved -> {record['image']}")

    (ROOT / "manifest-matrix.js").write_text(
        "window.MANIFEST_MATRIX = " + json.dumps(manifest, ensure_ascii=False, indent=2) + ";\n")
    print(f"\nWrote manifest-matrix.js ({len(manifest)} attempts). Open matrix.html to view.")

if __name__ == "__main__":
    main()
