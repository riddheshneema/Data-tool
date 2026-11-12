# Brochure source

To rebuild `../Maheshwar_Greens_Brochure.pdf`:
1. Put the Flow images in `images/` using the file names in `../Flow_Image_Brief.md` (`01_cover_aerial.png` … `05_villa.png`). Any image that is missing falls back to the layout artwork.
2. Run `python3 build_brochure.py`. This writes `brochure.html`.
3. Run `node render.js "$PWD/brochure.html" "$PWD/../Maheshwar_Greens_Brochure.pdf" "$PWD/preview"`. This needs Playwright with Chromium.

The artwork (`cover_art.svg`, `plan_art.svg`, `location_map.svg`) is drawn from the final layout geometry. Fonts: Cormorant Garamond (SIL Open Font License) and Inter.
