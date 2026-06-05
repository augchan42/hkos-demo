# `/verse-to-prompt` demo — the abstract verse

A live demo for the Inkstone `verse-to-prompt` skill (HKOSCon 2026, Slide 18 — *Abstract Verses: The Mechanism*).

It takes the **hardest kind of verse** — fully abstract, no imagery to paint — and shows the prompt **before** and **after** the skill, with a real image generated from each.

## The point isn't "naive looks ugly" — it's "naive ignores the verse"

`z-image/turbo` is a strong model, so a naive prompt still makes a *pretty* picture. The problem is that it's **arbitrary and unfaithful**. Across three abstract verses, the naive "translation + ink-painting-style" prompt:

| Verse | Meaning | Naive result | Failure |
|---|---|---|---|
| **41-19** 元吉无咎，安寧不殆 | Supremely auspicious, peace, no peril | a generic "beauty" portrait | ignores the verse entirely — any abstract verse gives the same cliché |
| **58-25** 結網得解… | The *knotted net finds release*; ease, blessing | a woman tangled in a fishing **net** | latches onto the one stray concrete word and inverts the meaning |
| **28-23** 廓落失業… | Vast, vacant, livelihood *lost*; disaster | a pleasant prosperous village | tone is exactly backwards |

The skill, by contrast, maps **tone → style** and forces a faithful, composed scene — so the three verses produce three **distinct, on-theme** paintings:

- **41-19 → `ink-landscape`** — calm dawn valley, a figure crossing a bridge safely ("free from peril")
- **58-25 → `figures-in-mist`** — a fisherman at ease, the released net a slack detail at his feet
- **28-23 → `atmospheric-night`** — a ruined gateway, guttering lantern, empty basket ("profit nowhere to be found")

**Same model, same seed (`410419`) for every image. The prompt is the only variable.**

## Everything is tied to its verse + prompt

No orphaned images. The pipeline is manifest-driven and self-contained (verse text is
embedded in `attempts.json` — no dependency on any other repo):

```
attempts.json                    source of truth: verse text + each {verse_key, approach, style, prompt}
generate.py                      reads attempts.json, calls fal, writes everything below
images/<verse>__<approach>.png   the image
images/<verse>__<approach>.json  sidecar: verse zh/en, transition, prompt, style, seed, model, source url, timestamp
manifest.json / manifest.js      full table the viewer renders from
runs.jsonl                       append-only audit log of every generation
index.html                       side-by-side viewer (renders from manifest.js)
```

## Reproduce

```bash
export FAL_API_KEY=your-fal-key      # or: export FAL_ENV_FILE=/path/to/some/.env
python3 generate.py                  # regenerates all images + manifest + sidecars + log
open index.html                      # side-by-side viewer for presenting
```

`generate.py` reads `FAL_API_KEY` from the environment (no secrets in the repo) and calls
fal.ai's `z-image/turbo` sync endpoint. To add or change an attempt, edit `attempts.json`
and re-run.

## The skill's full output for 41-19 (the headline verse)

> **Style:** `ink-landscape` — purely auspicious and abstract; the skill's fallback maps an auspicious tone to a calm shanshui landscape.
>
> **Prompt:** "Through a weathered stone gate, mossy steps descend like pale brushstrokes toward a still valley. In the midground a lone figure in a vermillion robe crosses a low bridge over calm water that mirrors the sky like spilled silver. Pine boughs frame the upper edge; terraced hills fade into amber dawn mist behind. Chinese ink painting."
>
> **Translation:** Supremely auspicious, without blame; peaceful and tranquil, free from peril.

All 7 composition rules woven in (not appended): frame (stone gate + pine boughs) · depth (steps → bridge figure → terraced hills) · contrast (dark gate vs bright water) · warm accent (vermillion robe + amber dawn) · diagonals (steps, pine bough) · discoverable detail (moss, terraces, reflection) · painterly language ("like pale brushstrokes", "like spilled silver").
