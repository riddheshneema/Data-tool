# Brochure source

`../Maheshwar_Greens_Brochure.pdf` is a 6-page A4 portrait consumer brochure. It uses only the final image set in `images/`, which is the same as `../brochure_images.zip` at commit e834f9c.

| Page | Content | Image |
|---|---|---|
| 1 | Cover | `01_cover_aerial` |
| 2 | Maheshwar, the town | `02_maheshwar_ghats` |
| 3 | Location: about two hours from Indore, with nearby places | `06_entrance` |
| 4 | Master plan | `plan_consumer.svg` (see below) |
| 5 | Streamside garden and garden boulevards | `04_streamside_garden`, `03_garden_boulevard`, `03b_garden_boulevard_walkable` |
| 6 | Plots, the planned resort next door, contact | `05_villa`, `07_resort_cottages` (lower picture only) |

## Rules carried over from `images/README.md`

- Every Flow image (01–07) has an "AI-generated concept visualisation" label.
- Each crop is anchored at the bottom-right corner, so Google's provenance watermark stays in the picture. `prep_images.py` checks this.
- The stream is always called a stream, never "riverside" or the Narmada. The check dam in `04` is captioned as a proposal.
- `07` is presented as the resort, as a separate project. It is never shown as the colony plots.
- The brochure shows no prices. The MP RERA number is left blank, to be filled in after registration and before release.

## Master plan (page 4)

`08_master_plan.png` in the zip is a technical drawing. Its title says "61 plots" and a label says "42 villa plots", but the layout has **62 plots (19 streamside + 43 garden)**. It also uses "riverside" and "river-front" labels.

`plan_consumer.svg` is the same plan redrawn for consumers, with the same plot geometry, the same colours and north up. Its stream line is taken from the `08` image itself (fitted to the plan at IoU 0.83). It has no dimensions or technical labels.

To make it again, run `workspace/brochure2/plan_consumer.py` (see `workspace/README.md`). Then copy the new `plan_consumer.svg` here.

## Rebuild

```bash
python3 prep_images.py "$PWD/images" "$PWD/img"   # crops, bottom-right anchored
python3 build_brochure.py                          # writes brochure.html
node render.js "$PWD/brochure.html" "$PWD/../Maheshwar_Greens_Brochure.pdf" "$PWD/preview"
```

`render.js` needs Playwright with Chromium. Fonts: Cormorant Garamond (in `fonts/`, SIL Open Font License) and Inter (installed system-wide).
