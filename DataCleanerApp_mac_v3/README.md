# DataCleanerApp (Mac) — v3 (Persistent Setup)

## Use
1) Double‑click `run.command` (or run `bash run.command` from Terminal).
2) In the app, open **Setup** (do once): upload **Final Template** and **Enrichment Master**.
3) Then go to **Process**: upload **Raw** only → resolve any unmapped columns → **GO**.
4) Download `final.xlsx` (and `flagged.xlsx` if shown) from the app; copies are also in `output/`.

## Enrichment Master format
Excel with sheets for: **AreaOfStudy**, **Degree**, **CourseLevel**. Each sheet must have columns:
- Output
- Keyword
- Weight
(Headers can be fuzzy; we auto-detect.)

## Transform (optional)
In **Setup**, configure Intake/Deadline parsing (source column in RAW, output columns in Final Template).
