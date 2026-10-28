# Cahiers du Soviéma: the podcast's feed

«Cahiers du Soviéma», беседы о советском кино. Feed: <https://soviema.github.io/feed.xml>

- `show.toml` and `episodes.toml`: the show and its episodes.
- `build_feed.py`: writes `feed.xml` and `index.html` from them (Python 3.11+, standard library only).
- `art/`: the show cover and the episode art (3000×3000 JPEG), served by GitHub Pages.
- The audio files are in the repository [`soviema/audio-1`](https://github.com/soviema/audio-1), served by GitHub Pages
  at `https://soviema.github.io/audio-1/` (Pages gives them an audio MIME type, which Apple's player needs).

## Adding an episode

1. Add the audio (AAC in `.m4a`, or MP3; under 100 MB, GitHub's limit per file) to the audio repository, commit and
   push; when it nears 900 MB (Pages' limit is 1 GB per site), start `audio-2`.
2. Put its art in `art/cds-epNN.jpg`.
3. Add an `[[episode]]` to `episodes.toml`:
   - a new random `guid` (`python3 -c "import uuid; print(uuid.uuid4())"`);
   - `audio`: `audio-1/cds-epNN.m4a`;
   - `length`: the file's size in bytes;
   - `duration`: `HH:MM:SS`.
4. Run `python3 build_feed.py`, read `git diff feed.xml`, then commit and push.

Never change an episode's `guid`, file name or date once it is out: podcast apps identify episodes by the guid.

Episodes #1–#8 and #3.а were moved here from Spotify for Creators on 2026-10-28 with their GUIDs, dates and audio
files unchanged.
