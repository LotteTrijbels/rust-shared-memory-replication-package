import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

DATA_FILE = SCRIPT_DIR / ".." / ".." / "2_manual_analysis" / "analysis_files" / "final_no_evidence.csv"
FIGURES_DIR = SCRIPT_DIR / ".." / "figures"

TITLE_KW = dict(fontsize=14, pad=12)
AXIS_KW = dict(fontsize=13, labelpad=11)
TICK_SIZE = 11

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

role_tm_grouped = role_tm_grouped.reindex(group_order).fillna(0).astype(int)
role_tm_grouped = role_tm_grouped.loc[(role_tm_grouped != 0).any(axis=1)]

plt.figure(figsize=(11, 6))

ax = sns.heatmap(
    role_tm_grouped,
    annot=True,
    fmt="d",
    cmap="crest",
    linewidths=0.5,
    annot_kws={"size": 11},
    cbar_kws={"shrink": 0.8}
)

ax.set_title(
    "Relationship Between Functional Role Groups and Thread Organisation Models",
    **TITLE_KW
)

ax.set_xlabel("Thread Organisation Model", **AXIS_KW)
ax.set_ylabel("Functional Role Group", **AXIS_KW)

ax.tick_params(axis="x", labelsize=TICK_SIZE)
ax.tick_params(axis="y", labelsize=TICK_SIZE)

plt.xticks(rotation=20, ha="right")
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

plt.xlabel("Number of Analysed Files", fontsize=13, labelpad=10)
plt.ylabel("Functional Role", fontsize=13, labelpad=10)
plt.title("Distribution of Functional Roles Across Analysed Files", fontsize=14, pad=12)

plt.xticks(fontsize=11)
plt.yticks(fontsize=11)

plt.gca().invert_yaxis()

plt.tight_layout()
plt.savefig(FIGURES_DIR / "functional_role_distribution.png", dpi=300, bbox_inches="tight")
plt.close()

print("- role_group_thread_model_heatmap.png")
print("- functional_role_distribution.png")