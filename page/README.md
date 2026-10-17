# page/

The feed web page.

| File | What it is |
|---|---|
| `index.html` | The whole page: HTML, CSS and JavaScript in one file. Published as a private Claude Artifact. |

How to publish it, what it stores, and how to edit it: [../docs/PAGE.md](../docs/PAGE.md).

Quick facts:

- Capabilities to declare when publishing: `{"db": {}, "downloads": true, "assets": {}}`.
- It reads the deck named by `meta/latest` and the cards with that `date`.
- It writes `ratings/*`, `signals/<date>`, `meta/state` and `requests/pending`.
- Syntax check after editing: extract the `<script>` body to a file and run `node --check <file>`.
- It cannot be tested for playback or sound without the user's device; say so when you change it.
