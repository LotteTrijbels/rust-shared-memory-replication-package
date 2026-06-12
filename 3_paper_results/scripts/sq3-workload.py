import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

DATA_FILE = SCRIPT_DIR / ".." / ".." / "2_manual_analysis" / "analysis_files" / "final_no_evidence.csv"
FIGURES_DIR = SCRIPT_DIR / ".." / "figures"

df = pd.read_csv(DATA_FILE, sep=";")

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)

sns.set_theme(style="white", font_scale=1.0)

def primitive_category(p):
    p = p.lower().strip()

    if "barrier" in p or "latch" in p:
        return "Coordination"

    if "atomic" in p:
        return "Atomic"

    if "lazy" in p or "once" in p:
        return "Lazy initialisation"

    if "mutex" in p or "rwlock" in p or "lock" in p:
        return "Lock-based"

    if "arcswap" in p:
        return "Snapshot sharing"

    if "arc" in p or "rc" in p or "weak" in p:
        return "Shared ownership"

    if "condvar" in p or "semaphore" in p:
        return "Coordination"
    
    if "send" in p or "sync" in p:
        return "Coordination"

    if "rwsignal" in p:
        return "Shared ownership"

    return "Other"

df["primitive_categories"] = df["primitives"].apply(
    lambda x: [primitive_category(p.strip()) for p in str(x).split(",")]
)

exploded = df.explode("primitive_categories")


# Workload + Primitive Categories

workload_primitive = (
    exploded
    .groupby(["workload", "primitive_categories"])
    .size()
    .unstack(fill_value=0)
)

category_order = [
    "Lock-based",
    "Atomic",
    "Shared ownership",
    "Snapshot sharing",
    "Coordination",
    "Lazy initialisation"
]

for c in category_order:
    if c not in workload_primitive.columns:
        workload_primitive[c] = 0

workload_primitive = workload_primitive[category_order]

workload_order = [
    "I/O-bound",
    "CPU-bound",
    "Mixed",
    "Coordination-heavy"
]

workload_primitive = workload_primitive.reindex(workload_order).fillna(0)

workload_primitive = workload_primitive.astype(int)

plt.figure(figsize=(10, 5))

ax = sns.heatmap(
    workload_primitive,
    annot=True,
    fmt="d",
    cmap="crest",
    linewidths=0.5,
    cbar=True
)

plt.title("Relationship Between Workload Types and Concurrency Primitive Categories")
plt.xlabel("Concurrency Primitive Category")
plt.ylabel("Workload Type")

plt.xticks(rotation=25, ha="right")
plt.yticks(rotation=0)

plt.tight_layout()

plt.savefig(FIGURES_DIR / "workload_primitives.png", dpi=300, bbox_inches="tight")
plt.close()

print("\n=== Workload + primitive ===")
print(workload_primitive.to_string())

print("- workload_primitives.png")
