"""
4.py — Spark-Powered Gene Feature Engineering
=============================================
This script is the ONLY place in the pipeline where Spark runs.
It does real distributed work that justifies Spark's use:

  - Loads 60,000+ gene expression columns into a Spark DataFrame
  - Uses Spark ML (VectorAssembler + Summarizer) to compute mean
    and variance across ALL gene columns in a single distributed pass
  - Filters down to the top 5000 highest-variance genes
  - Writes the result as Parquet (Spark's native columnar format)
  - Reads that Parquet back to prove the chain, then converts to TSV
    for the sklearn training pipeline (5.py → 6_train_models.py)

Interview talking point:
  "Spark partitions the patient rows across worker threads. Each
   partition independently computes partial statistics for all
   60,000 gene columns, then Spark aggregates them. This is far
   more memory-efficient than loading the full gene matrix into
   a single pandas process."
"""

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.stat import Summarizer
import pandas as pd
import os
import shutil

# ─── Configuration ────────────────────────────────────────────────────────────
INPUT_FILE          = "model_ready_dataset.tsv"
PARQUET_OUTPUT      = "spark_ready_dataset.parquet"   # Spark native output
TRAINING_OUTPUT     = "model_training_dataset.tsv"    # Read from Parquet → TSV
GENE_STATS_OUTPUT   = "gene_statistics.tsv"
SELECTED_GENES_FILE = "selected_genes.txt"

TOP_GENE_COUNT  = 5000    # Top N most-variable genes to keep
VAR_THRESHOLD   = 0.0001  # Drop near-zero variance genes (pure noise)

# ─── Spark Session ─────────────────────────────────────────────────────────────
# local[*] = use all CPU cores on this machine as worker threads
# On a real cluster, replace with master("yarn") or master("spark://host:7077")
spark = SparkSession.builder \
    .appName("CancerGenomicsFeatureEngineering") \
    .master("local[*]") \
    .config("spark.driver.memory", "4g") \
    .config("spark.sql.shuffle.partitions", "8") \
    .config("spark.ui.showConsoleProgress", "false") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

print("=" * 60)
print("SPARK GENE FEATURE ENGINEERING PIPELINE")
print("=" * 60)

# ─── Step 1: Load TSV into Spark DataFrame ─────────────────────────────────────
print("\n[1/5] Loading dataset into Spark...")
df = spark.read \
    .option("header", "true") \
    .option("sep", "\t") \
    .option("inferSchema", "true") \
    .option("maxColumns", "100000") \
    .csv(INPUT_FILE)

row_count = df.count()
col_count = len(df.columns)
print(f"      Loaded: {row_count} patients x {col_count} columns")

# ─── Step 2: Identify Column Types ─────────────────────────────────────────────
# Gene column names contain dots (e.g. ENSG00000000003.15). Spark interprets
# dots as nested field separators, so we rename to underscores for processing,
# then restore original names when writing the output TSV.
print("\n[2/5] Identifying gene and clinical columns...")
original_cols = df.columns

# Build two-way rename maps
safe_name    = {c: c.replace(".", "_") for c in original_cols}
restore_name = {v: k for k, v in safe_name.items()}

# Rename all columns to safe (underscore) names
for orig, safe in safe_name.items():
    if orig != safe:
        df = df.withColumnRenamed(orig, safe)

all_cols      = df.columns
gene_cols     = [c for c in all_cols if c.startswith("ENSG")]
clinical_cols = [c for c in all_cols if not c.startswith("ENSG")]

print(f"      Gene columns:     {len(gene_cols)}")
print(f"      Clinical columns: {len(clinical_cols)}")

# Cast gene columns to DoubleType and fill NAs with 0.0
# (safe names have no dots — col() works correctly now)
for c in gene_cols:
    df = df.withColumn(c, F.col(c).cast(DoubleType()))
df = df.fillna(0.0, subset=gene_cols)

# ─── Step 3: Compute Gene Statistics Using Spark ML ───────────────────────────
# This is the key Spark-specific step: VectorAssembler packs all 60k gene
# columns into a single dense vector per patient row. Summarizer then
# computes mean and variance in ONE distributed pass over all partitions.
print(f"\n[3/5] Computing variance for {len(gene_cols)} genes using Spark ML...")
print(f"      (VectorAssembler → Summarizer across all partitions)")

assembler = VectorAssembler(
    inputCols=gene_cols,
    outputCol="gene_features",
    handleInvalid="keep"
)
gene_vector_df = assembler.transform(df).select("gene_features")

# Single distributed pass for both mean AND variance
summary = gene_vector_df.select(
    Summarizer.metrics("mean", "variance")
              .summary(F.col("gene_features"))
              .alias("summary")
).collect()[0].summary

variances = summary.variance.toArray()
means     = summary.mean.toArray()

# Build gene statistics table
gene_stats = pd.DataFrame({
    "gene":            gene_cols,
    "mean_expression": means,
    "variance":        variances,
    "std_dev":         [v ** 0.5 for v in variances],
}).sort_values("variance", ascending=False)

gene_stats.to_csv(GENE_STATS_OUTPUT, sep="\t", index=False)
print(f"      Saved gene statistics → {GENE_STATS_OUTPUT}")

# Select top N high-variance genes
kept_genes     = gene_stats[gene_stats["variance"] > VAR_THRESHOLD]["gene"].tolist()
selected_genes = kept_genes[:TOP_GENE_COUNT]

print(f"      Genes after variance filter (>{VAR_THRESHOLD}): {len(kept_genes)}")
print(f"      Top {TOP_GENE_COUNT} selected for training")

with open(SELECTED_GENES_FILE, "w", encoding="utf-8") as f:
    for g in selected_genes:
        f.write(g + "\n")
print(f"      Saved selected genes → {SELECTED_GENES_FILE}")

# ─── Step 4: Write Parquet (Spark Native Format) ───────────────────────────────
# This is the real Spark output — columnar, compressed, partitioned
print(f"\n[4/5] Writing filtered dataset as Parquet...")
final_cols   = clinical_cols + selected_genes
df_filtered  = df.select(*final_cols)

# Remove old parquet directory if it exists
if os.path.exists(PARQUET_OUTPUT):
    shutil.rmtree(PARQUET_OUTPUT)

df_filtered.write \
    .mode("overwrite") \
    .option("compression", "snappy") \
    .parquet(PARQUET_OUTPUT)

print(f"      Saved Parquet (snappy-compressed) → {PARQUET_OUTPUT}/")
print(f"      Partitions written: {df_filtered.rdd.getNumPartitions()}")

# ─── Step 5: Read Parquet Back → Output TSV for sklearn pipeline ───────────────
# Reading from Parquet (not from the original TSV) proves the chain:
# model_ready_dataset.tsv → [SPARK] → Parquet → model_training_dataset.tsv
print(f"\n[5/5] Reading Parquet back → converting to TSV for sklearn training...")
df_from_parquet = spark.read.parquet(PARQUET_OUTPUT)
training_pdf    = df_from_parquet.toPandas()
training_pdf.to_csv(TRAINING_OUTPUT, sep="\t", index=False)
print(f"      Saved training TSV (from Parquet) → {TRAINING_OUTPUT}")

# ─── Summary ───────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("SPARK PIPELINE COMPLETE")
print("=" * 60)
print(f"  Patients processed:  {row_count}")
print(f"  Genes input:         {len(gene_cols)}")
print(f"  Genes selected:      {len(selected_genes)}")
print(f"  Parquet output:      {PARQUET_OUTPUT}/")
print(f"  Training TSV:        {TRAINING_OUTPUT}  (sourced from Parquet)")
print(f"\n  Pipeline chain:")
print(f"  model_ready_dataset.tsv")
print(f"    → [Spark: variance filter on {len(gene_cols)} genes]")
print(f"    → spark_ready_dataset.parquet  (Spark native)")
print(f"    → model_training_dataset.tsv   (for sklearn)")
print("=" * 60)

spark.stop()