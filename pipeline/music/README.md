# pipeline/music/

Royalty-free background tracks. The `.mp3` files are **not committed** (Mixkit's license forbids redistributing tracks on their own). Download them with:

```bash
scripts/fetch_music.sh
```

It fetches six hip-hop beats from Mixkit (ids 235, 257, 262, 267, 293, 303) and names them `<id>.mp3`. `produce.py` picks one per story by hashing the story id and mixes it at `music_volume` (0.16 by default) under the voice, fading out at the end.

To use your own tracks, drop `.mp3` files here and edit the `MUSIC` list at the top of `../produce.py` to their base names. Only use music you are licensed to use.
