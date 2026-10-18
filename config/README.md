# config/

| File | What it is |
|---|---|
| `config.example.json` | Template for the user's personal settings |

Setup copies it to **`config.json` at the repo root**, which is git-ignored:

```bash
cp config/config.example.json config.json
```

## Fields

| Field | Used by | Meaning |
|---|---|---|
| `timezone` | Claude (calendar event) | IANA zone, e.g. `America/Los_Angeles` |
| `notify_time` | Claude (calendar event) | Local time of the daily alert, `HH:MM` |
| `voice` | `pipeline/produce.py` | Google Chirp 3 HD voice name |
| `voice_rate` | `pipeline/produce.py` | Speaking rate; 1.0 is normal, 1.2 default |
| `music_volume` | `pipeline/produce.py` | 0 to 1; 0.16 default |
| `reels_per_batch` | Claude (daily run) | Reels per batch; 12 default |
| `interests` | Claude (daily run) | Beats to include: `ai`, `tech`, `bayarea`, `world`, `markets`, `spark` |
| `tickers` | Claude (daily run) | Symbols for the markets card |
| `use_portfolio_from_robinhood` | Claude (daily run) | If true, build the portfolio card from read-only Robinhood data |
| `robinhood_accounts` | Claude (daily run) | List of Robinhood account numbers to read, as strings. The Robinhood tools refuse to pick an account themselves, so without this the portfolio card cannot be built. Local only (config.json is git-ignored); never print these |
| `include_gmail`, `include_calendar` | Claude (daily run) | Include the inbox and schedule cards |
| `artifact_url` | Claude | The user's private feed URL, set after publishing |

Fields marked "Claude" are read by the agent following [../docs/DAILY-RUN.md](../docs/DAILY-RUN.md); the code reads only `voice`, `voice_rate` and `music_volume`.
