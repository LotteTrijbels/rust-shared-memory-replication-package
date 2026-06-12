## 2. Manual Qualitative Analysis

The qualitative analysis was conducted in six phases. Each phase produces a structured CSV file stored in `analysis_files/`.

### Phase overview

- Phase 1: Repository orientation and system summary
- Phase 2: Identification of concurrency entry points
- Phase 3: File selection based on structural and concurrency heuristics
- Phase 4: Deep analysis of concurrency behaviour
- Phase 5: Role assignment
- Phase 6: Workload and thread model classification

Each phase builds on the outputs of the previous phase.

---

### Phase 1: Orientation
Each repository was reviewed to understand its purpose, architecture, and module structure using README files and source tree inspection.

---

### Phase 2: Entry-point analysis
Primary entry points (e.g., `main.rs`, `lib.rs`) were analysed to identify runtime initialisation, thread spawning, and asynchronous execution patterns.

---

### Phase 3: File selection

This phase identifies candidate files for detailed analysis using a combination of structural and static heuristics.

File selection is based on:

(1) Entry-point tracing (e.g., `main.rs`, `lib.rs`) to identify execution and concurrency initialisation paths  
(2) Static analysis of shared-memory concurrency primitives using a dedicated scanning script (see `2_manual_analysis/script_output/analysis-primitive-count.py`)  
(3) Identification of architecturally relevant files based on execution flow and module structure  

The primitive scanning script traverses Rust source files and detects occurrences of concurrency primitives (e.g., `Arc`, `Mutex`, `RwLock`, atomic types, `Condvar`, `Barrier`). The results are stored in `primitive_counts.json` and used as a heuristic signal during manual file selection.

All candidate files are recorded in `file_selection_phase3.csv`, including detected primitives, and selection decisions. Only files marked `YES` are included in downstream analysis.

---

### Phase 4: Deep analysis
Selected files were analysed to identify shared-state usage, coordination mechanisms, and concurrency patterns.

---

### Phase 5: Component assignment
Files were assigned a functional role based off the recorded analysis noted.

---

### Phase 6: Workload and thread model
Each file was classified according to workload characteristics and thread model.

---

### Label definitions
Detailed label definitions are provided in `labels.csv`.

---

### Reproducibility
All completed worksheets are included in `analysis_files/` and represent the final dataset used in the study. The primitive detection results used during file selection are available in `2_manual_analysis/script_output/primitive_counts.json`.