import pandas as pd

df = pd.read_csv("target_ready_dataset.tsv", sep="\t", low_memory=False)

# Check recurrence source column
rec_candidates = [
    "diagnoses.progression_or_recurrence",
    "follow_ups.progression_or_recurrence"
]
for c in rec_candidates:
    if c in df.columns:
        print(f"\n{c}:")
        print(df[c].value_counts(dropna=False))

# Check survival_label distribution
print("\nsurvival_label distribution:")
print(df["survival_label"].value_counts(dropna=False))

# Check vital_status source
print("\ndemographic.vital_status:")
print(df["demographic.vital_status"].value_counts(dropna=False))

# Check survival_time
print("\nsurvival_time non-null:", df["survival_time"].notna().sum())

# Check days columns
for c in ["diagnoses.days_to_death", "diagnoses.days_to_last_follow_up", "demographic.days_to_death"]:
    if c in df.columns:
        valid = pd.to_numeric(df[c], errors="coerce").dropna()
        print(f"\n{c}: {len(valid)} usable values, mean={valid.mean():.1f}, median={valid.median():.1f}")
