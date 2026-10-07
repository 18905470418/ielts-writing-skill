# IELTS Academic Writing Task 2 corpus

Final deliverable: `output/ielts_task2_collection.md`.

**Target: 200 essays per band across 7 bands = 1400 essays.**
Delivered: 1400 target essays (200 in every band) plus 90 leftover inventory,
1490 unique essays in one file. No essay is repeated.

## Counts in the delivered file

| Band | Target essays | Leftover inventory | Total |
| ---- | ------------: | -----------------: | ----: |
| 6.0  |           200 |                 11 |   211 |
| 6.5  |           200 |                 14 |   214 |
| 7.0  |           200 |                 10 |   210 |
| 7.5  |           200 |                 17 |   217 |
| 8.0  |           200 |                 12 |   212 |
| 8.5  |           200 |                 16 |   216 |
| 9.0  |           200 |                 10 |   210 |
| **Total** | **1400** |             **90** | **1490** |

## File layout

1. `第001–1400篇` — the target corpus, 200 per band, bands in ascending order
   (6.0 → 6.5 → 7.0 → 7.5 → 8.0 → 8.5 → 9.0).
2. `# 额外库存` → `第1401–1490篇` — the remaining essays gathered along the way.
3. A closing count block splitting 主体 / 额外库存 / 合计.

Every entry carries `分数` (the band the source states for that essay), `题目`
(the matching task prompt), `文章` (the full essay, verbatim), and `来源`
(the original URL).

## Where the essays come from

Per-band source mix of the 1400 target essays:

| Band | IELTS-Blog | IELTS International | CD IELTS Prep | IWCS | IELTS Prep Studio | AllThingsIELTS | Band Nine | writing9 |
| ---- | ---------: | ------------------: | ------------: | ---: | ----------------: | -------------: | --------: | -------: |
| 6.0  | 21 | 2 | – | – | – | – | – | 177 |
| 6.5  | – | – | 57 | 4 | – | – | – | 139 |
| 7.0  | 18 | 3 | – | – | – | – | 1 | 178 |
| 7.5  | – | 2 | 57 | 4 | – | 2 | – | 135 |
| 8.0  | 102 | 3 | – | – | 5 | 1 | – | 89 |
| 8.5  | – | – | – | – | – | 1 | – | 199 |
| 9.0  | 52 | – | 57 | 4 | – | – | – | 87 |

How each source states the band:

| Source | Band stated how | Reliability |
| ------ | --------------- | ----------- |
| ielts-blog.com | Essay filed under the site's Band 5–9 category; marked by an IELTS teacher | teacher-marked |
| ielts.international | Each essay labelled "Band 6.0 / 7.0 / 8.0" with per-criterion breakdown | examiner-style labelled |
| cdieltsprep.com | Answer labelled "Band 6.5 / 7.5 / 9.0" with per-criterion scores | labelled teaching illustration |
| ieltswritingcorrectionservice.com | Answer labelled "Band 6.5 / 7.5 / 9.0" with per-criterion scores | labelled teaching illustration |
| ieltsprepstudio.com | Article titled "Band 8 Sample Essays", each essay labelled Band 8 | labelled sample |
| allthingsielts.com | Each sample headed "(Band N)" | labelled sample |
| bandnine.ai | Answer labelled "Band 7 sample response" | labelled sample |
| writing9.com | Each essay page prints "Band score N.0" from the site's checker | **automated estimate** |

## Caveats worth knowing

- **Band 8.5 has almost no published examiner-scored Task 2 samples.** Neither
  ielts-blog (no 8.5 category), IELTS Advantage (only a "Band 7, 8 and 9" pool),
  IELTS Liz, nor ielts.international publishes per-essay Band 8.5 material, so
  199 of the 200 Band 8.5 essays come from writing9.com's automated band label.
  The same applies to most of the half-band (6.5 / 7.5) and to the writing9
  portion of the whole-band counts. No score in this corpus was assigned by this
  pipeline: every band label is copied from the source page.
- **ielts.org, British Council and IDP** return HTTP 403 to non-browser clients
  and their text proxies were unreachable, so no official candidate responses
  could be captured. Cambridge IELTS books had no lawfully accessible full-text
  source in this environment.
- **IELTS Advantage's "100 Real Band 7, 8 + 9 Task 2 Samples"** labels its essays
  collectively as "Band 7, 8 or 9", with no per-essay score, so it cannot be
  filed under a specific band.
- Prompts and essays are reproduced verbatim, including student spelling and
  grammar errors. Nothing is corrected, rewritten or summarised.
- Task 1 material that occasionally appeared inside a Task 2 band listing on
  writing9 is filtered out; 1230 of the 1490 essays have a distinct prompt and
  the rest are different essays written on prompts that recur across bands.

## Method

1. Each source is fetched with its own parser (`scripts/collect_*.py`); raw HTML
   is cached under `data/raw/`, extracted items under `data/items/`.
2. `scripts/validate.py` flags short, contaminated or off-task items.
3. `scripts/render.py` de-duplicates by essay text, spreads each band across
   sources and unique prompts, writes `output/ielts_task2_collection.md`,
   `output/index_by_band.md`, `output/index_by_band.csv` and
   `output/manifest.json`.

## Reproducing

```bash
python3 -m venv .venv && .venv/bin/pip install beautifulsoup4 lxml requests pypdf
.venv/bin/python scripts/collect_ieltsblog.py --bands 6,7,8,9 --per-band 500
.venv/bin/python scripts/collect_cdieltsprep.py
.venv/bin/python scripts/collect_iwcs.py
.venv/bin/python scripts/collect_ieltsinternational.py
.venv/bin/python scripts/collect_inline_sources.py
.venv/bin/python scripts/collect_writing9.py --max-pages 80 \
  --targets "6:90,6.5:150,7:95,7.5:150,8:90,8.5:215,9:95"
.venv/bin/python scripts/render.py --per-band 200
```
