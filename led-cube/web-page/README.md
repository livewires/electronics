# LED Cube Animator — Web Page

## Development

Edit `index.html` directly. The page loads `led-cube-base.svg` (the cube diagram) and `lw-white.svg` (the logo) as separate files, so it must be served over HTTP — opening `index.html` directly from the filesystem won't work. A simple way to run it locally:

```bash
python3 -m http.server
```

Then open `http://localhost:8000`.

## Building for distribution

`index.html` references two external SVG files, which means it can't be shared as a single file or hosted on a plain static page without them alongside it.

Running the build script produces `index-bundle.html` — a fully self-contained file with all assets inlined:

```bash
python3 build.py
```

`index-bundle.html` can be opened directly from the filesystem (no server needed), attached to an email, or dropped onto any static host as a single file.

Edit `index.html` for development, run `build.py` when you want to publish or share.
