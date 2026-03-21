from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
import joblib
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI(title="Breast Cancer Prediction API")

# Allow CORS so the React frontend can talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins for now (localhost, vercel)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Load artifacts
# -----------------------------
DATA_FILE = "target_ready_dataset.tsv"
SELECTED_GENES_FILE = "selected_genes.txt"
SURVIVAL_MODEL_FILE = "survival_model.pkl"
RECURRENCE_MODEL_FILE = "recurrence_model.pkl"
SIMILARITY_MODEL_FILE = "patient_similarity_model.pkl"
SCALER_FILE = "scaler.pkl"

df = pd.read_csv(DATA_FILE, sep="\t", low_memory=False)

with open(SELECTED_GENES_FILE, "r", encoding="utf-8") as f:
    selected_genes = [line.strip() for line in f if line.strip()]

survival_model = joblib.load(SURVIVAL_MODEL_FILE)
recurrence_model = joblib.load(RECURRENCE_MODEL_FILE)
knn_model = joblib.load(SIMILARITY_MODEL_FILE)
scaler = joblib.load(SCALER_FILE)

id_col = [c for c in df.columns if "case_id" in c.lower()][0]

gene_cols = [c for c in selected_genes if c in df.columns]

X_all = df[gene_cols].apply(pd.to_numeric, errors="coerce").fillna(0)
X_all_scaled = scaler.transform(X_all)

patient_id_to_index = {
    str(pid): idx for idx, pid in enumerate(df[id_col].astype(str).tolist())
}

# -----------------------------
# Request schemas
# -----------------------------
class PatientRequest(BaseModel):
    case_id: str | None = None
    genes: dict[str, float] | None = None


# -----------------------------
# Helpers
# -----------------------------
def get_feature_vector_from_request(req: PatientRequest):
    """
    Build a gene feature vector in the same order as training.
    """
    if req.case_id:
        row = df[df[id_col].astype(str) == str(req.case_id)]
        if row.empty:
            raise HTTPException(status_code=404, detail="case_id not found")
        vec = row.iloc[0][gene_cols].apply(pd.to_numeric, errors="coerce").fillna(0).values
        return vec.reshape(1, -1)

    if req.genes:
        vec = []
        for g in gene_cols:
            vec.append(float(req.genes.get(g, 0.0)))
        return np.array(vec).reshape(1, -1)

    raise HTTPException(status_code=400, detail="Provide either case_id or genes")


def make_similarity_report(case_id: str, top_k: int = 5):
    if case_id not in patient_id_to_index:
        raise HTTPException(status_code=404, detail="case_id not found")

    idx = patient_id_to_index[case_id]
    target_vec = X_all_scaled[idx].reshape(1, -1)

    sims = cosine_similarity(target_vec, X_all_scaled).flatten()
    best_idx = np.argsort(-sims)

    neighbors = []
    for i in best_idx[1:top_k + 1]:
        pid = str(df.iloc[i][id_col])
        surv = df.iloc[i].get("survival_label", np.nan)
        rec = df.iloc[i].get("recurrence_label", np.nan)
        risk = df.iloc[i].get("high_risk_flag", np.nan)

        neighbors.append({
            "case_id": pid,
            "similarity": float(sims[i]),
            "survival_label": None if pd.isna(surv) else int(surv),
            "recurrence_label": None if pd.isna(rec) else int(rec),
            "high_risk_flag": None if pd.isna(risk) else int(risk),
        })

    return neighbors


def build_treatment_insight(similar_patients):
    """
    Simple insight layer based on similar patient outcomes.
    This is an exploratory summary, not a medical recommendation.
    """
    if not similar_patients:
        return {
            "summary": "No similar patient data available."
        }

    survival_vals = [p["survival_label"] for p in similar_patients if p["survival_label"] is not None]
    recurrence_vals = [p["recurrence_label"] for p in similar_patients if p["recurrence_label"] is not None]
    risk_vals = [p["high_risk_flag"] for p in similar_patients if p["high_risk_flag"] is not None]

    survived = sum(1 for v in survival_vals if v == 1)
    dead = sum(1 for v in survival_vals if v == 0)
    recur = sum(1 for v in recurrence_vals if v == 1)
    non_recur = sum(1 for v in recurrence_vals if v == 0)
    high_risk = sum(1 for v in risk_vals if v == 1)

    survival_pct = round((survived / len(survival_vals)) * 100, 2) if survival_vals else None
    recurrence_pct = round((recur / len(recurrence_vals)) * 100, 2) if recurrence_vals else None
    high_risk_pct = round((high_risk / len(risk_vals)) * 100, 2) if risk_vals else None

    return {
        "similar_patients_considered": len(similar_patients),
        "survival_percentage_among_similar": survival_pct,
        "recurrence_percentage_among_similar": recurrence_pct,
        "high_risk_percentage_among_similar": high_risk_pct,
        "interpretation": (
            "This is an exploratory outcome summary from similar historical patients. "
            "It can be used as a reference for pattern analysis."
        )
    }


# -----------------------------
# Routes
# -----------------------------
@app.get("/health")
def health():
    return {"status": "ok", "patients": len(df), "genes": len(gene_cols)}


@app.post("/predict/survival")
def predict_survival(req: PatientRequest):
    X = get_feature_vector_from_request(req)
    prob = survival_model.predict_proba(X)[0, 1]
    pred = int(prob >= 0.5)

    return {
        "survival_probability": round(float(prob) * 100, 2),
        "predicted_label": pred
    }


@app.post("/predict/recurrence")
def predict_recurrence(req: PatientRequest):
    X = get_feature_vector_from_request(req)
    prob = recurrence_model.predict_proba(X)[0, 1]
    pred = int(prob >= 0.5)

    return {
        "recurrence_probability": round(float(prob) * 100, 2),
        "predicted_label": pred
    }


@app.post("/similar-patients")
def similar_patients(req: PatientRequest):
    if not req.case_id:
        raise HTTPException(status_code=400, detail="case_id is required for similar patient search")

    neighbors = make_similarity_report(req.case_id, top_k=5)

    return {
        "case_id": req.case_id,
        "neighbors": neighbors,
        "treatment_insight": build_treatment_insight(neighbors)
    }


@app.post("/predict/all")
def predict_all(req: PatientRequest):
    X = get_feature_vector_from_request(req)

    surv_prob = survival_model.predict_proba(X)[0, 1]
    rec_prob = recurrence_model.predict_proba(X)[0, 1]

    if req.case_id:
        neighbors = make_similarity_report(req.case_id, top_k=5)
        insight = build_treatment_insight(neighbors)
    else:
        neighbors = []
        insight = {"summary": "No similar patient analysis because case_id was not provided."}

    aggressiveness_score = round(
    (
        (1 - surv_prob) * 60 +
        rec_prob * 30 +
        10
    ),
    2
)

    return {
        "survival_probability": round(float(surv_prob) * 100, 2),
        "recurrence_probability": round(float(rec_prob) * 100, 2),
        "aggressiveness_score": aggressiveness_score,
        "similar_patients": neighbors,
        "treatment_insight": insight
    }