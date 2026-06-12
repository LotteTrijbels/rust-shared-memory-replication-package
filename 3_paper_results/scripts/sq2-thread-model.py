import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
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

def shorten_thread_model(name):
    replacements = {
        "Actor / message-passing model": "Actor / message-passing",
        "Async executor–driven coordination model": "Async executor-driven",
        "Initialisation / singleton coordination model": "Initialisation / singleton",
        "Producer–consumer / pipeline coordination model": "Producer–consumer / pipeline",
        "Resource arbitration model": "Resource arbitration",
        "Shared-state concurrency model": "Shared-state",
        "Snapshot / copy-on-write model": "Snapshot / copy-on-write",
        "Worker-thread pool execution model": "Worker-thread pool",
    }
    return replacements.get(str(name), str(name))


df["primitives"] = df["primitives"].apply(
    lambda x: list(set(
        primitive_category(p.strip())
        for p in str(x).split(",")
    ))
)

exploded = df.explode("primitives")


tm_workload = pd.crosstab(
    df["thread_model"],
    df["workload"]
)
tm_workload.index = tm_workload.index.map(shorten_thread_model)

tm_primitive = (
    exploded
    .groupby(["thread_model", "primitives"])
    .size()
    .unstack(fill_value=0)
)

cols = [c for c in tm_primitive.columns] 
tm_primitive = tm_primitive[cols]
tm_primitive.index = tm_primitive.index.map(shorten_thread_model)

COMMON_CMAP = "crest"

# HEATMAP THREAD MODEL + WORKLOAD

plt.figure(figsize=(11, 6))

ax = sns.heatmap(
    tm_workload,
    annot=True,
    fmt="d",
    cmap=COMMON_CMAP,
    linewidths=0.5,
    annot_kws={"size": 10}
)

ax.set_title(
    "Relationship Between Workload Types and Thread Organisation Models",
    fontsize=14,
    pad=12
)

ax.set_xlabel("Workload Type")
ax.set_ylabel("Thread Organisation Model")

plt.xticks(rotation=20, ha="right", fontsize=9)
plt.yticks(rotation=0, fontsize=9)

plt.tight_layout()

plt.savefig(FIGURES_DIR / "workload_thread_model_heatmap.png", dpi=300, bbox_inches="tight")

plt.close()

# HEATMAP THREAD MODEL + PRIMITIVES

plt.figure(figsize=(11, 6))

ax = sns.heatmap(
    tm_primitive,
    annot=True,
    fmt="d",
    cmap=COMMON_CMAP,
    linewidths=0.5,
    annot_kws={"size": 9}
)

ax.set_title(
    "Relationship Between Thread Organisation Models and Concurrency Primitive Categories",
    fontsize=14,
    pad=12
)

ax.set_xlabel("Concurrency Primitive Category")
ax.set_ylabel("Thread Organisation Model")

plt.xticks(rotation=20, ha="right", fontsize=9)
plt.yticks(rotation=0, fontsize=9)

plt.tight_layout()

plt.savefig(FIGURES_DIR / "thread_model_primitive_categories_heatmap.png", dpi=300, bbox_inches="tight")
plt.close()

print("\n=== Workload + Thread Model ===")
print(tm_workload.to_string())

print("\n=== Thread Model + Primitive Categories ===")
print(tm_primitive.to_string())

print("- workload_thread_model_heatmap.png")
print("- thread_model_primitive_categories_heatmap.png")
