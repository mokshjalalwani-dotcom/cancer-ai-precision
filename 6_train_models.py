import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
import joblib

INPUT_FILE = "target_ready_dataset.tsv"

print("Loading dataset...")
df = pd.read_csv(INPUT_FILE, sep="\t", low_memory=False)
print("Shape:", df.shape)

# find patient id
id_col = [c for c in df.columns if "case_id" in c.lower()][0]

# gene columns
gene_cols = [c for c in df.columns if c.startswith("ENSG")]

print("Total genes:", len(gene_cols))

X = df[gene_cols].apply(pd.to_numeric, errors="coerce").fillna(0)

print("Feature matrix:", X.shape)

# ==========================
# SURVIVAL MODEL
# ==========================

if "survival_label" in df.columns:

    y = df["survival_label"].fillna(0)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print("Training Survival Model...")

    survival_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        n_jobs=-1
    )

    survival_model.fit(X_train, y_train)

    acc = survival_model.score(X_test, y_test)

    print("Survival Model Accuracy:", acc)

    joblib.dump(survival_model, "survival_model.pkl")

# ==========================
# RECURRENCE MODEL
# ==========================

if "recurrence_label" in df.columns:

    y = df["recurrence_label"].fillna(0)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print("Training Recurrence Model...")

    recurrence_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        n_jobs=-1
    )

    recurrence_model.fit(X_train, y_train)

    acc = recurrence_model.score(X_test, y_test)

    print("Recurrence Model Accuracy:", acc)

    joblib.dump(recurrence_model, "recurrence_model.pkl")

# ==========================
# PATIENT SIMILARITY ENGINE
# ==========================

print("Building Similarity Engine...")

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

knn = NearestNeighbors(
    n_neighbors=5,
    metric="cosine"
)

knn.fit(X_scaled)

joblib.dump(knn, "patient_similarity_model.pkl")
joblib.dump(scaler, "scaler.pkl")

# save patient ids for lookup
df[[id_col]].to_csv("patient_ids.tsv", sep="\t", index=False)

print("Models saved:")
print("survival_model.pkl")
print("recurrence_model.pkl")
print("patient_similarity_model.pkl")
print("scaler.pkl")