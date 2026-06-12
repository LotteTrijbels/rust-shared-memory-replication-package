import json
import matplotlib.pyplot as plt
import os
from collections import defaultdict


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(SCRIPT_DIR, "..", "primitive_counts_results.json")
FIGURES_DIR = os.path.join(SCRIPT_DIR, "..", "figures")
OUTPUT_FILE = os.path.join(FIGURES_DIR, "primitive_bar_chart.png")

with open(INPUT_FILE, "r") as f:
    data = json.load(f)

primitive_file_counts = defaultdict(int)

for file  in data:
    for primitive, present in file ["binary"].items():
        primitive_file_counts[primitive] += present
        
sorted_items = sorted(
    primitive_file_counts.items(),
    key=lambda x: x[1],
    reverse=True
)

for primitive, count in sorted_items:
    print(f"{primitive}: {count}")

primitives = [item[0] for item in sorted_items]
counts = [item[1] for item in sorted_items]

plt.figure()
plt.bar(primitives, counts)
plt.xticks(rotation=45)
plt.ylabel("Number of analysed files using primitive")
plt.title("Occurrence of Shared-memory Concurrency\nPrimitives in Analysed Projects")
plt.tight_layout()

plt.savefig(OUTPUT_FILE, dpi=300)
plt.close()