# Layout workspace

These are the tools the cloud session used to design the Jalkoti colony layout. They make the drawings, the DXF, the T&CP checks and the brochure's master plan. All of them were tested from a fresh copy of this folder and rebuilt the same outputs.

**Not included, because this repo is public:** the survey PDF (Drg SU/10/01), the text extracted from it, and your Google Earth places file. The survey geometry the tools need is in `site/geo.pkl` and `plan/approach.pkl`.

## Set up once on the Mac

```bash
cd Data-tool
git checkout ccr-feb95d7f-lj0rjx && git pull
python3 -m pip install -r workspace/requirements.txt
python3 workspace/fix_paths.py        # points the scripts at this folder
```

## Commands

Run these from inside `workspace/plan/` unless noted.

| What | Command | Writes |
|---|---|---|
| Layout plan: PNG, PDF, DXF and plot schedule | `python3 d11_render.py '{"th":100,"y0":0,"pw":45,"pd":90,"option":1,"drive_w":12}' Plan_4000_Max_RiverDrive12m "4,000 SQ FT – MAXIMUM PLOTS (ALL ROADS 12 m)"` | `site_plans/Plan_4000_Max_RiverDrive12m.*` |
| Manual layout edits: the SE re-cut, V42 chamfer, S1 corridor and S5 link | `python3 make_all_edits.py`, then run `d11_render.py` again | `plan/edits_Plan_4000_Max_RiverDrive12m.json` |
| Dimensioned drawing set, portrait (cover + 7 sheets) | `python3 build_pdf3.py` | `site_plans/Jalkoti_Colony_Dimensioned_Layout.pdf` |
| Dimensioned drawing set, landscape | `python3 build_pdf2.py` | `site_plans/Jalkoti_Colony_Dimensioned_Layout.pdf` (rename the portrait copy first) |
| Dimensioned DXF | `python3 dxf_dims.py` | `site_plans/Jalkoti_Colony_Dimensioned_Layout.dxf` |
| T&CP checks (BVN 2012) | `python3 tncp_test2.py Plan_4000_Max_RiverDrive12m` | printed results |
| Brochure master plan (page 4) | in `workspace/brochure2/`: `python3 plan_consumer.py` | `workspace/brochure2/plan_consumer.svg`. Copy it to `brochure/source/` |
| Fit the stream from the zip's `08_master_plan.png` | in `workspace/brochure2/`: `python3 fit08.py` | `workspace/brochure2/stream08.pkl` |
| Flow reference images | in `workspace/brochure/`: `python3 make_refs.py` | `brochure/flow_references/` (SVGs; screenshot with `shot2.js`) |

The brochure itself is built in `brochure/source/`. See the README there.

## What the files are

- `plan/dims.py`: loads the final layout and computes every plot, road, median and garden dimension. Most other scripts start by running it.
- `plan/d11_render.py`: the main renderer. It reads `base_original.pkl` (the layout before manual edits), applies `edits_*.json`, and writes `state_*` and `final_*` pickles plus the drawings.
- `plan/roadnet.py`, `tncp_test.py`, `tncp_test2.py`: road-network checks (dead ends, farthest plot, frontage) and the T&CP tests.
- `plan/approach.pkl`: the approach road traced from the survey. `site/geo.pkl` is the surveyed site outline, and `site/river.npy` is the survey's river mask.
- `plan/d2_*` to `plan/d10_*` and `layout*.py`: earlier design stages, kept for the record. The final layout doesn't need them re-run.
- `brochure/geo_kml.py` rebuilt the Google Earth KML from your own places file, which is not in the repo. The KML it made is `brochure/flow_references/colony_layout_google_earth.kml`.
- `reference/`: MP Bhumi Vikas Rules 2012, consolidated to 6 March 2025.
