# Story schema

One JSON file per reel: `pipeline/stories/<id>.json`. The file name (without `.json`) must equal `id`. Examples: `pipeline/stories/example-markets.json` (with animated bars) and `example-world.json`.

## Fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | string | yes | Lowercase-hyphen, unique. Prefix by beat: `ai-`, `tech-`, `bay-`, `world-`, `mkt-`, `spark-` |
| `topic` | string | yes | One of `ai`, `tech`, `bayarea`, `world`, `markets`, `spark`. Sets the accent color and chip label |
| `date` | string | no | On-video date label, e.g. `Fri Oct 16`. Defaults to today |
| `kicker` | string | no | Small label on the card, e.g. `Markets`, `Economy` |
| `source` | string | yes | Outlet name shown on the card |
| `url` | string | yes | Link behind "Read story" |
| `headline` | string[] | yes | 2 to 3 short lines. Prefix exactly one line with `*` to color it. Lines must fit big type: keep each line to about 12 characters per word group |
| `sentences` | string[] | yes | 5 to 6 short spoken sentences, each 14 words or fewer. Sentence 1 is a punchy hook. Numbers as digits (`21%`). Avoid URLs, parentheses and unusual abbreviations. Each sentence gets its own footage cut |
| `keywords` | string[] | yes | 3 to 5 Mixkit search words, most relevant first. Concrete visual nouns (`robot`, `traffic`, `crowd`, `server`, `forest`), never company or person names. Verify one returns at least 6 clips (see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)) |
| `bars` | object[] | no | Animated bars for market stories, at most 4: `{ "kw": "micro", "label": "SMCI", "pct": -20.9, "text": "−21%" }`. `kw` must appear (case-insensitive, substring) in a sentence; the bar animates in when that word is spoken. `pct` sets bar length (scaled so 22 is full); `text` is the label |
| `comments` | object[] | yes | Exactly 4 AI reactions, see below |
| `why` | string | no | Short personalization note shown on the card |
| `voice`, `rate`, `music_volume` | string, number, number | no | Per-story overrides of `config.json` |

## Reactions (`comments`)

`[{"who": "The skeptic", "text": "..."}]`, 4 per reel, each text at most 140 characters.

Personas are fixed archetypes, never real people: `The optimist`, `The skeptic`, `The nerd`, `The one who read the article`, `The doomscroller`, `The practical one`.

They are **AI-written commentary**, and the page labels them "AI". Rules:

- Witty and reaction-style, like short-video comments; measured for somber stories.
- Never claim to be real viewers. Never invent statistics, like counts or follower numbers. Never attribute a quote to a real person.
- No buy/sell advice. No partisan or insulting content.

## Writing rules for sentences

- Only facts present in the source excerpt or data you fetched. Attribute claims: "says", "reports", "claims", "according to".
- A company's own claim is stated as theirs ("Elorian claims").
- No financial advice; no predictions or price targets unless the source states one (then attribute it).
- Compute percentages from data, double-check the arithmetic, and say what period they cover.
- Roughly 60 to 75 words total gives a 17 to 20 second reel at the default voice speed.

## Minimal example

```json
{
  "id": "mkt-example",
  "topic": "markets",
  "kicker": "Markets",
  "source": "Yahoo Finance",
  "url": "https://finance.yahoo.com/",
  "headline": ["Chip stocks", "*took a hit", "this week"],
  "sentences": [
    "Chip stocks took a hit this week.",
    "Nvidia slid more than 5%.",
    "AMD lost 11%."
  ],
  "keywords": ["stock-market", "trading", "finance"],
  "bars": [{ "kw": "nvidia", "label": "NVDA", "pct": -5.4, "text": "−5%" }],
  "comments": [
    { "who": "The skeptic", "text": "Weekly moves are noise until you check what you own." },
    { "who": "The nerd", "text": "An 11% weekly drop is large for a chip designer." },
    { "who": "The practical one", "text": "Zoom out before you react to one week." },
    { "who": "The optimist", "text": "Volatility is where the interesting prices show up." }
  ]
}
```
