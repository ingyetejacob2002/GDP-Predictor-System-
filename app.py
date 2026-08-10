import json
from pathlib import Path

import joblib
import pandas as pd
from flask import Flask, jsonify, render_template, request

BASE = Path(__file__).resolve().parent
MODEL_PATH = BASE / "model" / "model.pkl"
PRECOMPUTED_PATH = BASE / "data" / "precomputed.json"

app = Flask(__name__)

model = joblib.load(MODEL_PATH)
with open(PRECOMPUTED_PATH) as f:
    DATA = json.load(f)

FEATURES = DATA["features"]


@app.context_processor
def inject_nav():
    return {
        "nav_items": [
            {"id": "home", "label": "Overview", "href": "/"},
            {"id": "analysis", "label": "Analysis", "href": "/analysis"},
            {"id": "models", "label": "Models", "href": "/models"},
            {"id": "predict", "label": "Predict", "href": "/predict"},
            {"id": "about", "label": "About", "href": "/about"},
        ],
        "global_final_model": DATA["final_model"],
    }


@app.route("/")
def home():
    max_abs_coef = max(abs(c["value"]) for c in DATA["coefficients"])
    return render_template(
        "home.html",
        active="home",
        final_model=DATA["final_model"],
        dataset_stats=DATA["dataset_stats"],
        coefficients=DATA["coefficients"],
        model_results=DATA["model_results"],
        max_abs_coef=max_abs_coef,
    )


@app.route("/analysis")
def analysis():
    max_abs_corr = max(abs(c["value"]) for c in DATA["correlations"])
    return render_template(
        "analysis.html",
        active="analysis",
        correlations=DATA["correlations"],
        countries=DATA["countries"],
        dataset_stats=DATA["dataset_stats"],
        feature_meta=DATA["feature_meta"],
        max_abs_corr=max_abs_corr,
    )


@app.route("/models")
def models_page():
    max_abs_coef = max(abs(c["value"]) for c in DATA["coefficients"])
    max_mae = max(r["mae"] for r in DATA["model_results"])
    return render_template(
        "models.html",
        active="models",
        model_results=DATA["model_results"],
        final_model=DATA["final_model"],
        coefficients=DATA["coefficients"],
        pred_vs_actual=DATA["pred_vs_actual"],
        max_abs_coef=max_abs_coef,
        max_mae=max_mae,
    )


@app.route("/predict")
def predict_page():
    return render_template(
        "predict.html",
        active="predict",
        feature_meta=DATA["feature_meta"],
        countries=DATA["countries"],
        final_model=DATA["final_model"],
        dataset_stats=DATA["dataset_stats"],
    )


@app.route("/about")
def about():
    return render_template(
        "about.html",
        active="about",
        dataset_stats=DATA["dataset_stats"],
        final_model=DATA["final_model"],
    )


@app.route("/api/predict", methods=["POST"])
def api_predict():
    payload = request.get_json(force=True)
    try:
        row = {
            "GDP_Per_Capita": float(payload["gdp"]),
            "Education_Index": float(payload["education"]),
            "Urban_Population_Percent": float(payload["urban"]),
        }
    except (KeyError, TypeError, ValueError):
        return jsonify({"error": "Invalid input. Expecting gdp, education, urban as numbers."}), 400

    meta = DATA["feature_meta"]
    bounds = {
        "gdp": ("GDP_Per_Capita", row["GDP_Per_Capita"]),
        "education": ("Education_Index", row["Education_Index"]),
        "urban": ("Urban_Population_Percent", row["Urban_Population_Percent"]),
    }
    for key, (feat, val) in bounds.items():
        lo, hi = meta[feat]["min"], meta[feat]["max"]
        if not (lo - 1e-9 <= val <= hi + 1e-9):
            return jsonify({"error": f"{feat} must be between {lo} and {hi}."}), 400

    X = pd.DataFrame([row])[FEATURES]
    pred = float(model.predict(X)[0])
    pred = max(0.0, pred)

    rates = [c["unemployment"] for c in DATA["countries"]]
    rank = sum(1 for r in rates if r < pred)
    percentile = round(100 * rank / len(rates))

    return jsonify(
        {
            "prediction": round(pred, 2),
            "mae": DATA["final_model"]["mae"],
            "percentile": percentile,
            "n_countries": len(rates),
        }
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
