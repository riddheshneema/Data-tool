# Flow brief: the linear garden (garden boulevards)

> **For the Claude session on the Mac.** Paste:
> *"Pull the repo and follow `brochure/Flow_Brief_Linear_Garden.md`. Stop at every CHECKPOINT and show me the result before going on."*

The brochure doesn't yet show the **linear garden**: the 3 m planted strip down the middle of the three garden boulevards. The current pictures (`03`, `03b`) are high aerial views, and the garden in them is small. They also put the stream next to the boulevard, which the plan does not.

This brief asks for 3 close, human-scale pictures that sell the linear garden. They go on page 5.

---

## 0. Rules

1. Use the **same Flow mode, model and download settings as the final set**. They are listed in `brochure/source/images/credits.md`. Make 4 variants for each prompt.
2. Never use Veo. Don't buy credits or change any setting. Never type or ask for a password.
3. No text, signs, logos or close-up faces. Keep Google's watermark; don't crop it out.
4. Stop at every **CHECKPOINT** for the owner's approval.

## 1. What the street really is (get this right)

| Part | Width | What it looks like |
|---|---|---|
| Footpath | 1 m | edge strip along each plot wall |
| Lane | 3.5 m | grey interlocking paver blocks, granite kerbs |
| **Linear garden** | **3 m (10 ft)** | a **1 m stone or paver walking path** down the middle, with flower beds and low clipped hedges on both sides. It has small trees (champa/frangipani, kachnar, young neem) every 8–10 m, a few benches and low bollard lights. |
| Lane | 3.5 m | as above |
| Footpath | 1 m | as above |

- The whole street is **12 m (40 ft)** wall to wall. The garden is **narrow**. It must not look like a park.
- Each garden runs **60–100 m** between junctions, then the street meets a cross road. Don't show an endless avenue.
- On both sides are plots behind **low sandstone boundary walls** with gates. Show a few small **single-storey cottages (about 1,000 sq ft)** set back on big lawns, and some plots still open green land. No large villas and no buildings filling a plot.
- **The stream is not visible from these streets. Show no water.**
- Setting: flat Nimar countryside, golden hour or early dusk, warm path lights.

## 2. References to attach (every image)

- `brochure/flow_references/ref_03b_boulevard_section.png`: the street cross-section, to scale
- `brochure/flow_references/ref_03a_boulevard_topdown.png`: the boulevard from above
- `brochure/source/images/03b_garden_boulevard_walkable.png`: the approved look (materials, colour and light only, **not** its layout)

## 3. The pictures

### 09_linear_garden_eye.png (3:4 portrait). The hero shot
> Photorealistic eye-level photograph (35 mm lens, 1.6 m high). You are standing on the narrow stone walking path in the middle of a 3 m wide planted garden strip that runs down the centre of a 12 m residential street in a new gated farmhouse community in central India. Look along the path. Show flower beds and low clipped hedges on both sides of the path, small flowering trees (frangipani, kachnar) every few metres, a wooden bench and low bollard lights. Grey paver-block lanes run along each side of the garden strip, with granite kerbs. Beyond the lanes are low sandstone plot walls with gates, and small single-storey cottages set back on large lawns, with some plots still open. A couple is walking away down the path in the distance. Golden-hour light, long soft shadows, calm and premium. The garden strip is only about 3 m wide, so it is not a park. No water, no text.

### 10_linear_garden_drone.png (3:4 portrait)
> Photorealistic low drone photograph, about 20 m up, centred over a garden boulevard and looking along it. The boulevard is a 12 m street with a continuous 3 m planted garden strip down the middle. The strip has a narrow stone path, flower beds, small trees and warm path lights. Grey paver-block lanes run on both sides. Low sandstone walls separate the large plots on each side. There are a few small single-storey cottages on lawns and some open plots. About 80 m ahead, the boulevard meets a cross street. Early dusk, the path lights just on, Nimar fields and trees on the horizon. No water, no text.

### 11_linear_garden_bench.png (4:5 portrait). Life in the garden
> Photorealistic photograph at human scale. A family sits on a wooden bench under a small flowering tree in a narrow 3 m garden strip in the middle of a quiet residential street. They are seen from the side and behind, with no faces. There are flower beds and a stone path, and a child is walking on the path. Across a grey paver-block lane is a low sandstone wall with a gate, and a small single-storey cottage behind it. Warm evening light, soft and natural. No water, no text.

**CHECKPOINT:** show the owner the variants of each picture. Keep the one they pick.

**Reject** any variant where:
- the garden strip is wider than a lane;
- there is a river, stream or pond;
- houses are big or fill their plots;
- the lanes are tarmac rather than paver blocks;
- the avenue runs on for hundreds of metres.

## 4. Deliver

1. Save the approved pictures at full resolution to `brochure/source/images/` as `09_linear_garden_eye.png`, `10_linear_garden_drone.png` and `11_linear_garden_bench.png`.
2. Add each one to `brochure/source/images/credits.md`, with its model, prompt and references.
3. Commit and push to the same branch:
   ```bash
   git add brochure/source/images
   git commit -m "Add linear garden pictures for the brochure"
   git push origin ccr-feb95d7f-lj0rjx
   ```
4. Tell the owner they're pushed. The cloud session then puts them on page 5.
