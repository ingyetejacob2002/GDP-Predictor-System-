# Youth Unemployment in Africa — Model Explorer

An interactive, multi-page web app built on top of the youth unemployment
prediction project. Compares 8 machine learning algorithms via Leave-One-Out
Cross-Validation and serves live predictions from the final deployed model
(Lasso Regression).

## Pages

- **/** — Overview: headline stats, signature "driver bars" finding, quick model comparison
- **/analysis** — EDA: correlation chart, GDP/Education scatter plots, sortable country table
- **/models** — Methodology (why LOOCV), full 8-model comparison chart, final model rationale, predicted-vs-actual plot
- **/predict** — Live prediction tool: pick a country or drag sliders, get a real-time prediction from the deployed model
- **/about** — Dataset caveats, key takeaways, next steps

## Running it locally

```bash
pip install -r requirements.txt
python app.py
```

Then open **http://127.0.0.1:5000** in your browser.

The model is already trained and saved (`model/model.pkl`), along with all
precomputed analysis data (`data/precomputed.json`). If you want to retrain
from scratch (e.g. after changing the dataset), run:

```bash
python model/train_model.py
```

This regenerates both `model/model.pkl` and `data/precomputed.json`.

## Project structure

```
app.py                  Flask app: routes + /api/predict endpoint
model/
  train_model.py        Trains all 8 models, saves final Lasso model + LOOCV results
  model.pkl              Saved final model (Lasso Regression pipeline)
data/
  youth_unemployment_africa.csv   Source dataset
  precomputed.json        All analysis data the app reads (no retraining at request time)
templates/               Jinja2 page templates (base.html + 5 pages)
static/
  css/style.css          Design system (colors, type, layout)
  js/                    Page-specific interactivity (charts, sliders, sortable table)
  js/vendor/chart.umd.min.js   Self-hosted Chart.js (no external CDN dependency)
```

## Notes

- The dataset is small (40 countries, one year) and illustrative — built for
  the DSN AI Bootcamp, not drawn from live labor-market records. The app
  says this plainly in a few places; keep that framing if you present it.
- Chart.js is self-hosted under `static/js/vendor/` so the app works without
  internet access once dependencies are installed. Google Fonts (Fraunces,
  IBM Plex Sans/Mono) are still loaded from Google's CDN in `base.html` — if
  you need a fully offline version, download and self-host those too.
