# Vessel Landscape website

Static site for Vessel Landscape (Sergio Garcia, Springville, Utah), live at https://vessellandscape.com via GitHub Pages.

- Edit `_src/build.py` (pages, copy, schema) and `_src/styles.css`, then run `python3 _src/build.py` from the repo root. It writes the HTML, `404.html`, `sitemap.xml` and `robots.txt` here. Bump `LASTMOD` when page content changes and keep `REVIEW_COUNT` matching Google.
- Standing decisions: keep the nav uncluttered (services live in the Services dropdown), no blog, no mention of permits or engineering in site copy, plain short wording.
- Old domain vesselgroundworks.com redirects page-by-page from the separate repo `sgvieuai/vesselgroundworks-redirect`. Email for that domain runs on Microsoft 365, so never touch its MX, SPF or autodiscover records.

## Job photos (Sergio's standing rule: every photo gets this treatment)

Sergio sends phone videos (.MOV) and photos (.HEIC). Tools are in `_src/photos.py` (run with `--help`).

1. **Review everything first.** `photos.py sheet` for video strips, `photos.py heic` to open HEIC photos. iPhone video is HDR; the tools tone-map it so colors aren't gray and washed out.
2. **Only use the best.** His own jobs only; if a job may have been done as a sub for another company, ask before posting. Skip blurry or near-duplicate shots, the photographer's shadow, harsh clutter, and branded end cards from old videos. Finished "after" shots and true before/after pairs are worth the most. Say plainly when a batch has nothing worth using.
3. **Pull stills** with `photos.py still VIDEO START END OUT.png` (picks the sharpest frame in the window).
4. **Crop on purpose.** Layouts crop with object-fit to 1:1 (gallery, desktop hero), 4:3, 3:4 (before/after, steps) and 4:5 (split sections), so frame portrait shots about 4:5 and landscape shots about 4:3 with the subject centered.
5. **Privacy.** Crop people out where possible, especially faces. Blur house numbers, street signs, mailboxes with numbers and license plates (`--blur x0,y0,x1,y1` in source pixels; check at 3–4x zoom). Exported WebP files carry no GPS or EXIF.
6. **Light grade only** (`photos.py export`): levels, gentle lift for dark shots, slight warmth on cold ones, a touch of contrast and color. It must still look real; drop `--color` (e.g. 0.9) for photos that are already very saturated. `photos.py regrade NAME` applies the same pass to a photo already on the site.
7. **Look at every final image** before it goes on a page, then screenshot the page (desktop and phone) after building.
8. **Publish and verify**: commit, push, wait for the Pages deploy, then load the live page.

Naming: `images/<what-it-shows>.webp` plus `-sm.webp`, descriptive kebab-case (e.g. `pool-deck-concrete-removed`). Alt text describes the scene; captions are short.
