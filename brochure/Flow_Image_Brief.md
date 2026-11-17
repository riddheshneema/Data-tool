# Flow image brief: Maheshwar Greens brochure

> **Give this to your Claude session on the Mac** (the one that can drive your Chrome). Paste:
> *"Pull the repo and follow `brochure/Flow_Image_Brief.md` step by step. Stop at every CHECKPOINT and show me the result before going on."*

The goal is a set of photorealistic, truthful images for a 4-page consumer brochure for the plotted colony at Jalkoti, Maheshwar. They are made in **Google Flow with the Omni model only. Do not use Veo.** Every image must look like *this* land and *this* layout, so use the references below on every image.

---

## 0. Rules

1. **Flow: Omni model only. Never use Veo.** Don't buy credits, change plans or change any setting. Never type or ask for passwords.
2. **Truthful.** The site has a **small stream, about 10 ft (3 m) wide**. It is not the Narmada. Never show a big river at the site. The layout is new: most plots are empty, with a few villas at most.
3. No text, logos or watermarks in the images, and no close-up faces.
4. Stop at every **CHECKPOINT** for the owner's approval.
5. In the brochure every image is labelled **"AI-generated concept visualisation"**.

---

## 1. Get the materials

```bash
git clone https://github.com/riddheshneema/Data-tool.git   # or: cd Data-tool && git fetch
cd Data-tool && git checkout ccr-feb95d7f-lj0rjx && git pull
```

Everything is in **`brochure/flow_references/`**:

| File | What it is | Use it for |
|---|---|---|
| `colony_layout_google_earth.kml` | **The plot layout placed on the real land.** Layers: plots, 12 m roads, garden medians, riverside garden, walkway, services, resort, access road, approach road, and your own hand-drawn outline | Google Earth captures (step 2) |
| `site_coordinates.json` | Site centre 22.1838 N, 75.5493 E · colony gate 22.18396 N, 75.54977 E · main entry 22.18203 N, 75.54939 E · approach road meets the main road at 22.17774 N, 75.55171 E | Navigating Google Earth |
| `ref_01_layout_topdown.png` | Whole colony from above, drawn to scale from the final plan: stream bend, 15 m garden strip, river drive, 3 garden boulevards, plots | Cover aerial |
| `ref_04_garden_strip_topdown.png` | Close-up from above of the garden strip between the stream and the river-front plots | Garden image |
| `ref_03a_boulevard_topdown.png` | Close-up from above of a garden boulevard (S3) with its median and avenue trees | Boulevard image |
| `ref_03b_boulevard_section.png` | Cross-section of the 12 m garden street, to scale: 1 m footpath, 3.5 m lane, 3 m planted median, 3.5 m lane, 1 m footpath | Boulevard image |
| `ref_05_villa_plot_topdown.png` | A 45 × 90 ft plot on a boulevard; the dashed line is the area you can build on | Villa image |
| `ref_06_site_context_map.png` | Main road → 553 m tree-lined approach road (15 m, over a bridge) → main entry → access road → colony gate | Entrance image |
| `ref_07_colony_layout_plan.png` | Full colony layout plan with plot numbers | Overall understanding |

Also useful: `site_plans/Jalkoti_Colony_Dimensioned_Layout.pdf` (all dimensions) and `brochure/Maheshwar_Greens_Brochure.pdf` (draft layout; shows where each image goes).

---

## 2. Google Earth captures of the real land (references only)

1. Open **earth.google.com** in Chrome. Go to **Projects → New project → Import KML file from computer**, and import `colony_layout_google_earth.kml`.
2. **Check the overlay.** The riverside garden (light green) should follow the stream bend, and the approach road should line up with the road on the ground. If it's clearly off, move the view, not the KML, and note the offset for the owner. The placement is approximate (±20–30 m).
3. Capture these and save them to `brochure/flow_references/google_earth/`:

| File | View |
|---|---|
| `ge_01_overlay_aerial.png` | 3D tilt about 45°, about 400 m eye altitude, looking **north-west** over the colony, **overlay ON** |
| `ge_02_land_aerial.png` | The same view, **overlay OFF**: the bare land, stream and trees as they are |
| `ge_03_overlay_topdown.png` | Straight down, overlay ON, the whole colony filling the frame |
| `ge_04_approach.png` | Low 3D view from the main-road junction looking up the approach road towards the site |
| `ge_05_maheshwar_ghats.png` | 3D view of the Maheshwar ghats and Ahilya Fort on the Narmada (22.1716 N, 75.5894 E) |

These are **private references for Flow only**. Don't put Google Earth captures in the brochure.

**CHECKPOINT 1:** show the owner the 5 captures.

---

## 3. Make the images in Flow (Omni only)

For each image:
1. Open a new project in Flow and choose **Omni**.
2. Add the listed **reference images** as ingredients or reference images.
3. Paste the prompt.
4. Make **3–4 variants**.
5. **CHECKPOINT:** show them to the owner and keep the one they pick.

If Flow only makes video for a prompt, make an 8-second clip with a slow camera move and export its best still frame at full resolution.

Style for every image:
- photorealistic, golden-hour light, gentle haze, warm natural grade;
- **Nimar countryside of Madhya Pradesh**: flat black-soil fields, neem, babul, mango and gulmohar trees;
- palette leaning to deep green, sandstone and warm saffron;
- no text.

### 01_cover_aerial.png (4:5 portrait; the brochure cover)
**References:** `ge_01_overlay_aerial.png`, `ge_02_land_aerial.png`, `ref_01_layout_topdown.png`

> Photorealistic drone photograph at golden hour, about 45° tilt, of **this exact land** (follow the Google Earth references for the terrain, stream and surroundings) with the plotted community built **exactly as in the layout reference**. Show:
> - a **small natural stream, about 3 m wide**, bending along the north-west and north edge;
> - a continuous **15 m landscaped garden strip** of lawn and young native trees along the stream;
> - behind it, a row of large river-front plots, then the **river drive**, a 12 m road lined with young trees, following the bend;
> - **three garden boulevards** running north–south, each with a green planted median;
> - neat rows of villa plots with low boundary stones;
> - a **link road** at the south-east;
> - a **single entry gate** at the south, where the access road comes in;
> - beyond the gate, the resort land left green and natural;
> - Nimar fields all around.
>
> Most plots are still empty, with fresh red-brown soil and boundary markers, and only 4–6 modern single-storey villas with sloping roofs. Soft warm light, long shadows, calm and premium. No big river, no lake, no high-rises, no text.

### 02_maheshwar_ghats.png (16:9; page 2 header, will be cropped to a wide band)
**References:** `ge_05_maheshwar_ghats.png`, plus any real photos of Maheshwar the owner has

> Photorealistic sunrise view of the historic stone ghats of **Maheshwar on the wide Narmada river** in Madhya Pradesh: broad sandstone steps into the water, the **Ahilya Fort** walls and carved temple spires above, small wooden boats on calm water, soft golden mist, a few people at prayer far away, warm colours, high detail. Keep the real character of Maheshwar's riverfront.

### 03_garden_boulevard.png (4:3; page 3)
**References:** `ref_03b_boulevard_section.png`, `ref_03a_boulevard_topdown.png`

> Photorealistic eye-level photograph (35 mm) along a **40-ft (12 m) residential garden boulevard** in a new gated colony in central India, built exactly to the section: **1 m footpath, 3.5 m paved lane, 3 m planted median with young neem and gulmohar trees and low shrubs, 3.5 m paved lane, 1 m footpath**. Show:
> - low boundary walls of plots on both sides;
> - a few modern single-storey villas with front lawns, and some plots still open;
> - soft evening golden light;
> - a couple walking far away.
>
> Clean, calm, green. No text.

### 04_streamside_garden.png (4:3; page 3 or 4)
**References:** `ref_04_garden_strip_topdown.png`, a crop of `ge_02_land_aerial.png` showing the stream

> Photorealistic photograph of a **15 m wide landscaped garden** between a **small natural stream (about 3 m wide, with grassy natural banks)** and the back walls of large residential plots. Each plot has a small **garden gate** in a low wall or hedge opening onto the garden. Show:
> - soft lawns, native neem, peepal and gulmohar trees;
> - a narrow stone footpath, wooden benches, low garden lights;
> - warm sunset light;
> - a family walking far away.
>
> Natural and calm, Nimar countryside beyond. No big river, no text.

### 05_villa.png (4:3; page 4, optional)
**References:** `ref_05_villa_plot_topdown.png`

> Photorealistic photograph of a modern single-storey (or G+1) Indian villa on a **45 × 90 ft plot**: a small front lawn (3.6 m front setback), sandstone and white facade, sloping terracotta-tile roof, bougainvillea. It faces a garden boulevard with a planted median and young trees. Golden hour. No text.

### 06_entrance.png (4:3; optional)
**References:** `ge_04_approach.png`, `ref_06_site_context_map.png`

> Photorealistic photograph of a modest, elegant **gated entrance** to a residential colony at the end of a **15 m tree-lined approach road** in the Nimar countryside: sandstone pillars, a low wall, a simple gate with a **blank** name panel, avenue trees on both sides, early-morning light. No text.

---

## 4. Deliver

1. Save the approved images at full resolution to **`brochure/source/images/`**, named exactly `01_cover_aerial.png`, `02_maheshwar_ghats.png`, `03_garden_boulevard.png`, `04_streamside_garden.png` and, if made, `05_villa.png` and `06_entrance.png`.
2. Add `brochure/source/images/credits.md`. For each image, list the model (Omni), the prompt used and the references used.
3. Commit and push to the same branch:
   ```bash
   git add brochure/source/images brochure/flow_references/google_earth
   git commit -m "Add Flow images for the brochure"
   git push origin ccr-feb95d7f-lj0rjx
   ```
4. Tell the owner they're pushed. The cloud session then builds the final brochure using **only these images**.
