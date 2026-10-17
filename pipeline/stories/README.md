# pipeline/stories/

One JSON file per reel. The file name without `.json` must equal the `id` inside it.

| File | What it is |
|---|---|
| `example-markets.json` | A markets reel with animated ticker bars. Use it as the test reel in setup |
| `example-world.json` | A world-news reel without bars |

Field-by-field reference, writing rules and the AI-reaction rules: [../../docs/STORY-SCHEMA.md](../../docs/STORY-SCHEMA.md).

Daily story files you write are personal to the day. They are fine to keep locally; do not commit stories that contain private information (they should not, since stories use only public news text).

Render one: `cd .. && python3 produce.py stories/<id>.json`.
