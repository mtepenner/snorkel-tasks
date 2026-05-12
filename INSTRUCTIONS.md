## 📋 Submission Checklist

*Complete these steps before uploading to the Snorkel Platform.*

### Task Design & Files

* [ ] **Clarity:** Problem statement is unambiguous with explicit requirements.
* [ ] **Paths:** All instructions use **absolute paths** (e.g., `/app/file.txt`).
* [ ] **Files:** Included `task.toml`, `environment/Dockerfile`, `solution/solve.sh`, `tests/test.sh`, and `tests/test_outputs.py`.
* [ ] **Milestones:** If `number_of_milestones >= 2`, ensure the `steps/` directory structure is used instead of root-level files.

### Technical Verification

* [ ] **Deterministic:** The solution script (`solve.sh`) works every time without randomness.
* [ ] **Pinned:** All Docker base images and package dependencies (pip, npm) use **exact versions** (avoid `latest`).
* [ ] **Reward File:** `tests/test.sh` **must** generate `/logs/verifier/reward.txt` (1 for pass, 0 for fail).
* [ ] **No Leaks:** Tests verify behavior without revealing the solution or hints.

### Automated Checks (Local)

* [ ] **Oracle Agent:** `harbor run -a oracle -p <task-folder>` passes.
* [ ] **CI Checks:** `harbor tasks check <task-folder> -m openai/@openai/gpt-5.2` returns all green.

---

## 🏗️ Task Structure & Components

### File Hierarchy (Non-Milestone)

```text
my-task-folder/
├── instruction.md      # Concise, human-style engineering prompt
├── task.toml           # Essential metadata and runtime limits
├── environment/        # Setup files
│   └── Dockerfile      # Pinned environment definition
├── solution/           
│   └── solve.sh        # The "Oracle" solution script
└── tests/              
    ├── test.sh         # Entry point for verification
    └── test_outputs.py # Pytest validation logic

```

### The Manifest: `task.toml`

| Field | Requirement |
| --- | --- |
| **difficulty** | Based on pass rate (`Easy > 80%`, `Medium 21-80%`, `Hard <= 20%`). |
| **codebase_size** | `minimal` (0–20 files), `small` (20+), or `large` (200+). |
| **task_type** | Must choose one from the official 9-type taxonomy. |
| **runtime_limits** | Must define `agent`, `verifier`, and `build` timeouts. |

---

## 🛠️ Technical Standards

### 1. Docker Environment (`environment/Dockerfile`)

* **Version Pinning:** You must pin your base image and all packages.
* ✅ `FROM python:3.11-slim`
* ✅ `RUN pip install pandas==2.1.0`
* ❌ `FROM python:latest`


* **Security:** No privileged containers.
* **Hygiene:** Never copy `solution/` or `tests/` into the Docker image; the harness mounts them at runtime.

### 2. The Reward System (`tests/test.sh`)

Your test runner must be a bash script that explicitly writes the success state to the verifier log.

```bash
# Example Reward Generation
if [ $? -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

```

### 3. Oracle Solution (`solution/solve.sh`)

* Must be **human-written** (no LLM-generated solutions).
* Must demonstrate the command sequence an expert would use.
* Must be **idempotent** (can run multiple times without breaking).

---

## 🎯 Quality & Difficulty Guidelines

### What Makes a "Good" Task?

> "An expert human can solve it confidently, but it stumps current AI agents."

* **Multi-step Reasoning:** Requires more than a single command.
* **Niche Knowledge:** Uses specific libraries or bespoke rules that aren't common in training data.
* **Debugging focus:** Agents must find the root cause, not just "write code."

### Difficulty Targets

| Pass Rate | Difficulty Level | Description |
| --- | --- | --- |
| **> 80%** | **Easy** | Straightforward; tasks with 100% pass rate are rejected. |
| **21% - 80%** | **Medium** | Requires moderate complexity and domain knowledge. |
| **<= 20%** | **Hard** | Requires deep expertise and complex multi-step reasoning. |

---

## 🚫 What to Avoid

* **Trivia:** Testing memorization rather than reasoning.
* **External Dependencies:** Tasks requiring internet access or API keys.
* **Brittle Tests:** Using string matching on console output instead of checking state/behavior.
* **Canary Strings:** These are no longer required in Terminus Edition 2.

---

## 🚀 Submission Method

1. Create a **ZIP of the files** (not the parent folder).
2. Upload to the `terminus-project-v2` project on the **Snorkel Expert Platform**.
3. Ensure the metadata in the UI matches your `task.toml`.
