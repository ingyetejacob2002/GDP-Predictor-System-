"""
Trains the final Lasso model and precomputes everything the Flask app needs
(LOOCV comparison across 8 algorithms, correlations, coefficients, country
lookup, predicted-vs-actual points) so the web app never has to retrain
anything at request time.
"""
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import ElasticNet, Lasso, LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import LeaveOneOut
from sklearn.neighbors import KNeighborsRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR

BASE = Path(__file__).resolve().parent.parent
DATA_CSV = BASE / "data" / "youth_unemployment_africa.csv"
MODEL_PATH = BASE / "model" / "model.pkl"
PRECOMPUTED_PATH = BASE / "data" / "precomputed.json"

FEATURES = ["GDP_Per_Capita", "Education_Index", "Urban_Population_Percent"]
TARGET = "Youth_Unemployment_Rate"

FEATURE_META = {
    "GDP_Per_Capita": {
        "label": "GDP per Capita",
        "unit": "$",
        "min": 500,
        "max": 10000,
        "step": 50,
        "default": 2500,
    },
    "Education_Index": {
        "label": "Education Index",
        "unit": "",
        "min": 0.40,
        "max": 0.85,
        "step": 0.01,
        "default": 0.58,
    },
    "Urban_Population_Percent": {
        "label": "Urban Population",
        "unit": "%",
        "min": 15,
        "max": 80,
        "step": 0.5,
        "default": 45.0,
    },
}


def build_models():
    return {
        "Linear Regression": make_pipeline(StandardScaler(), LinearRegression()),
        "Ridge": make_pipeline(StandardScaler(), Ridge(alpha=1.0)),
        "Lasso": make_pipeline(StandardScaler(), Lasso(alpha=0.1)),
        "ElasticNet": make_pipeline(StandardScaler(), ElasticNet(alpha=0.1)),
        "KNN": make_pipeline(StandardScaler(), KNeighborsRegressor(n_neighbors=5)),
        "SVR (RBF)": make_pipeline(StandardScaler(), SVR(kernel="rbf", C=10, epsilon=0.5)),
        "Random Forest": RandomForestRegressor(n_estimators=300, max_depth=4, random_state=42),
        "Gradient Boosting": GradientBoostingRegressor(
            n_estimators=100, max_depth=2, learning_rate=0.05, random_state=42
        ),
    }


def main():
    df = pd.read_csv(DATA_CSV)
    X = df[FEATURES]
    y = df[TARGET]
    loo = LeaveOneOut()

    # ---- LOOCV comparison across all 8 models ----
    model_results = []
    for name, model in build_models().items():
        preds = np.array(
            [
                model.fit(X.iloc[tr], y.iloc[tr]).predict(X.iloc[te])[0]
                for tr, te in loo.split(X)
            ]
        )
        mae = mean_absolute_error(y, preds)
        rmse = np.sqrt(mean_squared_error(y, preds))
        r2 = r2_score(y, preds)
        model_results.append({"name": name, "mae": round(mae, 3), "rmse": round(rmse, 3), "r2": round(r2, 3)})
    model_results.sort(key=lambda r: r["mae"])

    # ---- Final model: Lasso, fit on all data ----
    final_model = make_pipeline(StandardScaler(), Lasso(alpha=0.1))
    loocv_preds = np.array(
        [
            final_model.fit(X.iloc[tr], y.iloc[tr]).predict(X.iloc[te])[0]
            for tr, te in loo.split(X)
        ]
    )
    final_model.fit(X, y)  # refit on all rows for deployment
    joblib.dump(final_model, MODEL_PATH)

    final_mae = mean_absolute_error(y, loocv_preds)
    final_rmse = np.sqrt(mean_squared_error(y, loocv_preds))
    final_r2 = r2_score(y, loocv_preds)

    coefs = final_model.named_steps["lasso"].coef_
    coefficients = [
        {"feature": FEATURE_META[f]["label"], "value": round(float(c), 3)}
        for f, c in zip(FEATURES, coefs)
    ]

    # ---- Correlations ----
    corr = df[FEATURES + [TARGET]].corr()[TARGET].drop(TARGET)
    correlations = [
        {"feature": FEATURE_META[f]["label"], "value": round(float(corr[f]), 3)} for f in FEATURES
    ]

    # ---- Country lookup for autofill + explorer ----
    countries = []
    for _, row in df.iterrows():
        countries.append(
            {
                "country": row["Country"],
                "gdp": round(float(row["GDP_Per_Capita"]), 2),
                "education": round(float(row["Education_Index"]), 3),
                "urban": round(float(row["Urban_Population_Percent"]), 1),
                "unemployment": round(float(row["Youth_Unemployment_Rate"]), 1),
            }
        )
    countries.sort(key=lambda c: c["country"])

    # ---- Predicted vs actual (final model, LOOCV) ----
    pred_vs_actual = [
        {"country": c, "actual": round(float(a), 2), "predicted": round(float(p), 2)}
        for c, a, p in zip(df["Country"], y, loocv_preds)
    ]

    precomputed = {
        "features": FEATURES,
        "feature_meta": FEATURE_META,
        "model_results": model_results,
        "final_model": {
            "name": "Lasso Regression",
            "mae": round(final_mae, 3),
            "rmse": round(final_rmse, 3),
            "r2": round(final_r2, 3),
            "best_model_name": model_results[0]["name"],
            "best_model_mae": model_results[0]["mae"],
        },
        "coefficients": coefficients,
        "correlations": correlations,
        "countries": countries,
        "pred_vs_actual": pred_vs_actual,
        "dataset_stats": {
            "n_countries": int(len(df)),
            "year": int(df["Year"].iloc[0]),
            "n_features": len(FEATURES),
        },
    }

    with open(PRECOMPUTED_PATH, "w") as f:
        json.dump(precomputed, f, indent=2)

    print("Saved model to", MODEL_PATH)
    print("Saved precomputed data to", PRECOMPUTED_PATH)
    print(f"Final model: Lasso | LOOCV MAE={final_mae:.3f} R2={final_r2:.3f}")


if __name__ == "__main__":
    main()
