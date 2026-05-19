#!/usr/bin/env python3
"""
Bundle index.html + SVG assets into a single self-contained HTML file.
Output: index-bundle.html

Strategy:
  - Logo:         replace src="lw-white.svg" with a base64 data URI.
  - Cube SVG:     inject a fetch() shim before </head> that intercepts
                  fetch('led-cube-base.svg') and returns the inlined SVG.
                  The existing JS is left completely untouched.
"""

import base64
from pathlib import Path

src = Path(__file__).parent

html = (src / 'index.html').read_text()

# ── Logo ──────────────────────────────────────────────────────────────────
logo_b64 = base64.b64encode((src / 'lw-white.svg').read_bytes()).decode()
html = html.replace(
    'src="lw-white.svg"',
    f'src="data:image/svg+xml;base64,{logo_b64}"',
)

# ── Cube SVG: fetch() shim ────────────────────────────────────────────────
cube_svg = (src / 'led-cube-base.svg').read_text()
cube_svg_js = (
    cube_svg
    .replace('\\', '\\\\')   # must be first
    .replace('`',  '\\`')
    .replace('${', '\\${')
)

shim = f"""\
<script>
(function () {{
    var _svg = `{cube_svg_js}`;
    var _fetch = window.fetch;
    window.fetch = function (url) {{
        if (url === 'led-cube-base.svg')
            return Promise.resolve(new Response(_svg, {{ status: 200 }}));
        return _fetch.apply(this, arguments);
    }};
}})();
</script>
"""

html = html.replace('</head>', shim + '</head>', 1)

# ── Write output ──────────────────────────────────────────────────────────
out = src / 'index-bundle.html'
out.write_text(html)
print(f'Built → {out}')
