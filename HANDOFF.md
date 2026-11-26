# Handoff: Jalkoti colony (Maheshwar Greens)

> **For a Claude Code session on the owner's Mac.** Start it in this repo folder and paste:
> *"Pull branch ccr-feb95d7f-lj0rjx, read HANDOFF.md and workspace/README.md, run the setup in workspace/README.md, then tell me you're ready."*

This picks up the cloud session's work. Everything is on branch `ccr-feb95d7f-lj0rjx` (draft PR #1).

## The project

- **Land:** 23.325 acres at Jalkoti, Maheshwar (Khargone, MP). It is outside any planning area and already diverted. Survey Drg SU/10/01.
- **Front half** (by the main entry) is a planned resort, a separate project. **Back half** is the colony, 11.80 acres on the stream bend.
- **The stream** is seasonal, about 10 m wide (median), on the north-west and north edges. It is not the Narmada. Never call it "riverside" in marketing.
- **The owner calls it a farmhouse project.** Cottages are about 1,000 sq ft.

## The final layout (`site_plans/`)

- **62 plots:** 19 streamside (R1–R19, 5,275–10,853 sq ft) and 43 garden plots (V1–V43, 3,616–6,489 sq ft). 23 of the garden plots are 45 × 90 ft (4,050 sq ft).
- **Sellable area:** 325,383 sq ft = 7.47 acres = 63.3% of the colony.
- **Roads:**
  - All colony roads are 12 m. The access road through the resort is 15 m and 223 m long. The approach road is 15 m and 553 m long.
  - The gate is about 800 m from the main road.
- **Garden streets S2, S3 and S4:** each has a 3 m planted median (61 m, 100 m and 64 m long).
- **Open space:**
  - The 15 m streamside garden is 6,156 m² (12.9%).
  - The 7 ft walkway between R10 and R11 is 2.13 × 31.3 m.
  - The services plot (STP, tank, waste) is 549 m².
- **Dead ends:** two, each with a 12 × 11 m turning space.
- **T&CP:** it passes every BVN 2012 rule that can be measured. See `reports/TCP compliance test - Jalkoti colony layout.md`. Open items:
  - The garden's shape is at T&CP's discretion (Rule 47(3)).
  - Dedicate the access and approach roads as public streets.
  - Check the diversion purpose.
  - Get a high-water-level survey of the stream.
  - Check the Narmada 300 m rule.
  - Register with RERA before any advertising.
- **Drawings:**
  - `Jalkoti_Colony_Dimensioned_Layout.pdf` (portrait, cover + 7 sheets) and its landscape twin.
  - `Jalkoti_Colony_Dimensioned_Layout.dxf` and `Plan_4000_Max_RiverDrive12m.*`.
- **Tools:** in `workspace/`.

## The brochure (`brochure/`)

- **`Maheshwar_Greens_Brochure.pdf`:** 6 pages, A4 portrait. It uses only the final Flow image set in `brochure/source/images/` (= `brochure_images.zip` @ e834f9c). The pages are:
  1. cover
  2. Maheshwar
  3. 1–1½ hours from Indore (the owner's figure), about 95 km
  4. master plan
  5. gardens
  6. plots, the resort next door, contact
- **Page 4's plan** is redrawn from the layout geometry. The zip's `08_master_plan.png` wrongly says 61 plots and uses "riverside" labels.
- **To rebuild:** see `brochure/source/README.md`.

**Rules the owner set**
- No prices in any marketing.
- No technical data in the brochure.
- Every AI image is labelled "AI-generated concept visualisation".
- Keep Google's watermark; crop from the bottom-right only.
- Never use Veo in Flow, never buy credits, never type passwords.
- The stream is never "riverside" or the Narmada. The check dam is only a proposal. The resort is a separate project.

**Open items**
1. **Linear garden photos:** the owner feels the brochure doesn't show the 3 m garden down the middle of the boulevards. Run `brochure/Flow_Brief_Linear_Garden.md` in Flow. Then put `09`–`11` on page 5 as the lead pictures.
2. **Blanks:** the phone/WhatsApp number and the MP RERA number. Fill them in only after RERA registration; the brochure can't be advertised before then.
3. **Optional:** real photos for page 2 (Maheshwar) and of the land itself, instead of AI.
4. **Optional:** check whether the site sits on the Dhamnod–Maheshwar road. The survey labels the main road "Jalkoti ← → Maheshwar". If it does, page 3 can say "on the way from Dhamnod".

## Earlier answers the owner asked for (no drawing changes made)

- **South-facing streamside plots:** discussed entrances from the garden side and 2–3 more 7 ft garden entrances. Not drawn.
- **Widening S2–S4 to 14 m:** costs about 5,400 sq ft of plots. Not done.
- **Paver-block roads with a walkway inside the 3 m median:** discussed. Not drawn.

## Colony layout after the engineer's Option 6 (v7 is the current sheet)

- **v6** (`site_plans/v6_engineer/`) put plots on the engineer's road network with a packing routine. The owner rejected it: plots at odd angles, gaps between neighbours, 54 different sizes.
- **v7** (`site_plans/v7_set_out/`) is set out from the road geometry instead:
  - two straight plot grids follow the two reaches of the stream (headings 22.94° and 10.40°) and meet on Cross Street;
  - Stream Drive along the 9 m green, Second and Third Streets parallel to it, a 12 m Avenue from the gate;
  - every block is two 75 ft plots deep, so side and back walls are shared.
- **Numbers:** 75 plots, 248,023 sq ft, 51.4% of 11.07 ac (10.79 ac without the clubhouse plot). All plots are 3,014 sq ft or more with a 40 ft or wider street front.
- **Files:** `Jalkoti_Colony_v7_Layout` (plan), `Jalkoti_Colony_v7_Plot_Guide` (price groups and plot list), `Jalkoti_Colony_v7_Plot_Schedule.csv`.
- **To rebuild:** in `workspace/v7/` run `plan_v7.py`, `analyze_v7.py`, `render_v7.py`, `sheet2_v7.py` in that order (after `fix_paths.py`).
- **Owner's standing limits:** colony on about 10 acres, 11 at most; plots 3,000 sq ft and up; roads 9 m or less except the entry avenue; nothing planned on the resort land.

### v8 (current): v7 plus three changes the owner asked for

- `site_plans/v8_more_plots/`: 77 plots, 262,115 sq ft, 54.4% of 11.07 ac. Roads unchanged (9 m streets, 12 m Avenue).
- **Central Park** narrowed from 34 m to 24 m (1,089 m²); adds plot 77 and widens plots 12-15.
- **Plot 76** cut from the east end of the clubhouse land beside plot 7 (3,145 sq ft, irregular, faces the foot of Cross Street).
- **North-east garden removed:** plot 75 widened to 90 ft, plots 60 and 61 extended back to the boundary.
- Parks and gardens are now 10.1% in three places, so there is no room to shrink them further.
- Old plot numbers are kept; new plots are 76 and 77.
- **To rebuild v8:** `plan_v7.py '{"v8":1,"pw":24.0,"out":"plan8"}'`, then `TAG=8` for `analyze_v7.py`, `render_v7.py`, `sheet2_v7.py`.
- **Not done, offered:** extending plots 42 and 26 into the green wedge at the east end would add about 8,500 sq ft (to about 56%).
- **Landscape sheet:** `site_plans/v8_more_plots/Jalkoti_Colony_v8_Landscape` (concept). Built by `workspace/v7/landscape_v8.py` after the v8 steps above. It uses only green land and road verges; plots and roads are unchanged.
- **Road widths:** owner asked whether 9 m streets should be 12 m. Advice given: keep 9 m (12 m everywhere costs roughly 5% of the land); the Avenue is already 12 m. No decision yet.

### Final drawing set (layout v8)

- `site_plans/final/Jalkoti_Colony_Final_Drawing_Set.pdf`: 6 sheets (master plan with landscape, key dimensions, three enlarged sheets with every plot's side lengths in feet, plot schedule). PNG copies of each sheet sit beside it.
- `Jalkoti_Colony_Final_Layout.dxf`: CAD file in metres with layers for boundary, plots, roads, road centre lines, park, clubhouse, 9 m strip, plot numbers, areas and side lengths.
- `Jalkoti_Colony_Final_Plot_Schedule.csv`: all 77 plots.
- Built by `workspace/v7/final_set.py` after the v8 and landscape steps.
