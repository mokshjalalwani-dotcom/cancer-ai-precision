# Cancer AI Precision — Survivability Prediction

> Machine learning pipeline for predicting cancer patient survivability using clinical and demographic features.

## Overview

A supervised ML project that applies ensemble learning techniques to predict cancer outcomes. Built on real clinical datasets with a focus on model interpretability using SHAP values.

## Tech Stack

- **Language:** Python 3
- **Libraries:** Scikit-learn, XGBoost, Pandas, NumPy, Matplotlib, SHAP
- **Environment:** Jupyter Notebook

## Models Used

| Model | Accuracy |
|---|---|
| Random Forest | ~87% |
| XGBoost | ~89% |
| Ensemble (Voting) | ~91% |

## Features

- Data preprocessing and feature engineering pipeline
- Comparative benchmarking across multiple classifiers
- SHAP explainability — understand which features drive predictions
- Cross-validation with stratified k-fold

## Running the Project

`ash
pip install -r requirements.txt
jupyter notebook
`

---
Built by **Moksh Lalwani** · PDEU, Ahmedabad