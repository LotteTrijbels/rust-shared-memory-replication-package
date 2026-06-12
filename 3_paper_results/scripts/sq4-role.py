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

def shorten_thread_model(name):
    replacements = {
        "Actor / message-passing model": "Actor / message-passing",
        "Async executor–driven coordination model": "Async executor-driven",
        "Initialisation / singleton coordination model": "Initialisation / singleton",
        "Producer–consumer / pipeline coordination model": "Producer-consumer / pipeline",
        "Resource arbitration model": "Resource arbitration",
        "Shared-state concurrency model": "Shared-state",
        "Snapshot / copy-on-write model": "Snapshot / copy-on-write",
        "Worker-thread pool execution model": "Worker-thread pool",
    }
    return replacements.get(str(name), str(name))

role_group_map = {
    "Runtime coordination layer": "A. Runtime & control plane",
    "Execution loop": "A. Runtime & control plane",
    "OS integration bridge": "A. Runtime & control plane",

    "Event dispatch system": "B. Communication & interaction",
    "Request coordination layer": "B. Communication & interaction",
    "Connection coordination layer": "B. Communication & interaction",
    "Logging system": "B. Communication & interaction",

    "Resource coordination layer": "C. Resource & system management",
    "Synchronisation primitive layer": "C. Resource & system management",
    "Database coordination layer": "C. Resource & system management",
    "Session coordination layer": "C. Resource & system management",

    "I/O coordination layer": "D. I/O & data flow",

    "State synchronisation layer": "E. State & configuration",
    "Shared configuration system": "E. State & configuration",
    "Caching layer": "E. State & configuration",
    "Rendering coordination layer": "E. State & configuration",
}

df["role_group"] = df["role"].map(role_group_map)
df["role_group"] = df["role_group"].fillna("F. Other / Unclassified")

# GROUPED ROLE + THREAD MODEL HEATMAP

role_tm_grouped = (
    df.groupby(["role_group", "thread_model"])
    .size()
    .unstack(fill_value=0)
)

role_tm_grouped.columns = [
    shorten_thread_model(c)
    for c in role_tm_grouped.columns
]

group_order = [
    "A. Runtime & control plane",
    "B. Communication & interaction",
    "C. Resource & system management",
    "D. I/O & data flow",
    "E. State & configuration",
    "F. Other / Unclassified"
]

role_tm_grouped = role_tm_grouped.reindex(
    [g for g in group_order if g in role_tm_grouped.index]
)

plt.figure(figsize=(12, 7))

sns.heatmap(
    role_tm_grouped,
    annot=True,
    fmt="d",
    cmap="crest",
    linewidths=0.5,
    cbar_kws={"shrink": 0.8}
)

plt.title("Relationship Between Functional Role Groups and Thread Organisation Models")
plt.xlabel("Thread Organisation Model")
plt.ylabel("Functional Role Group")

plt.xticks(rotation=25, ha="right")
plt.yticks(rotation=0)

plt.tight_layout()
plt.savefig(FIGURES_DIR / "role_group_thread_model_heatmap.png", dpi=300, bbox_inches="tight")

plt.close()

# FUNCTIONAL ROLE DISTRIBUTION (A–E ORDERED)

roles = df["role"].astype(str)

role_counts = roles.value_counts()

role_groups = {
    "Runtime coordination layer": "A",
    "Execution loop": "A",
    "OS integration bridge": "A",

    "Event dispatch system": "B",
    "Request coordination layer": "B",
    "Connection coordination layer": "B",
    "Logging system": "B",

    "Resource coordination layer": "C",
    "Synchronisation primitive layer": "C",
    "Database coordination layer": "C",
    "Session coordination layer": "C",

    "I/O coordination layer": "D",

    "State synchronisation layer": "E",
    "Shared configuration system": "E",
    "Caching layer": "E",
    "Rendering coordination layer": "E",
}

ordered_labels = []
ordered_counts = []

for group in ["A", "B", "C", "D", "E"]:

    group_roles = [
        comp for comp, grp in role_groups.items()
        if grp == group
    ]

    group_roles = [
        c for c in group_roles
        if c in role_counts.index
    ]

    group_roles = sorted(
        group_roles,
        key=lambda c: role_counts[c],
        reverse=True
    )

    for i, comp in enumerate(group_roles, start=1):
        ordered_labels.append(f"{group}{i} {comp}")
        ordered_counts.append(role_counts[comp])

plt.figure(figsize=(10, 6))

plt.barh(ordered_labels, ordered_counts)
plt.xlabel("Number of Analysed Files")
plt.ylabel("Functional Role")
plt.title("Distribution of Functional Roles Across Analysed Files")

plt.gca().invert_yaxis()

plt.tight_layout()
plt.savefig(FIGURES_DIR / "functional_role_distribution.png", dpi=300, bbox_inches="tight")

plt.close()


print("- role_group_thread_model_heatmap.png")
print("- functional_role_distribution.png")