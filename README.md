# Snorkel AI Project Terminus - Task Repository

[cite_start]Welcome to my central repository for task submissions created for **Project Terminus**, a Snorkel AI initiative designed to build a high-quality dataset in the style of Terminal-Bench[cite: 69]. 

[cite_start]The tasks housed in this repository are designed to evaluate how well state-of-the-art AI agents (like GPT-5.2 and Claude Opus 4.6) can accomplish complex, multi-step engineering tasks within a terminal environment[cite: 70, 71].

## 📂 Repository Structure

Each directory in this repository represents a standalone, self-contained task submission. To align with the strict evaluation protocols of the Snorkel Expert Platform, every task follows a uniform structural blueprint:

* [cite_start]**`task.toml`**: The configuration and metadata file detailing task tags, execution boundaries (timeouts and resource limits), and complexity metrics[cite: 79].
* **`instruction.md`**: The prompt provided to the AI agent. [cite_start]These are written in a natural, human-styled tone (mimicking a real developer's request) and exclusively utilize absolute paths[cite: 77].
* [cite_start]**`environment/`**: Contains the unprivileged `Dockerfile` (or `docker-compose.yaml` for multi-container setups) which provisions the sandbox environment and pins all necessary dependencies[cite: 80, 82].
* [cite_start]**`solution/`**: Contains the `solve.sh` script, an expert-authored "Oracle" solution that reliably and deterministically completes the task without internet access[cite: 83].
* **`tests/`**: The verification suite. [cite_start]It includes `test.sh` as the mandatory primary entrypoint, alongside `test_outputs.py` for deterministic state validation using pytest[cite: 83, 84]. 
* [cite_start]**`milestones.md`** *(Optional)*: Included only for highly complex tasks broken down into sequential, standalone subtasks[cite: 84, 91].

## 🎯 Task Design Philosophy

All tasks developed here strictly adhere to the following design constraints:
1.  [cite_start]**Multi-Step Execution:** Tasks require handling intermediate states and chaining commands; they cannot be solved with a single trivial command[cite: 121].
2.  [cite_start]**Deterministic Verification:** Success is evaluated programmatically via binary scoring (0 or 1)—partial credit is not permitted[cite: 15].
3.  [cite_start]**Self-Contained & Offline:** Once initiated, tasks run to completion without user input, and the Oracle solution operates entirely without web access[cite: 11, 123].
4.  **Security Conscious:** Environments are completely sandboxed. [cite_start]Privileged operations, `docker.sock` mounts, and `SYS_ADMIN` capabilities are strictly prohibited[cite: 122].

## 🚀 Local Execution & Testing

[cite_start]To run or evaluate these tasks locally, the Snorkel CLI tool, **Harbor**, is required[cite: 139].

1. Install Harbor:
   ```bash
   pip install harbor
   ```
2. Run the Oracle solution to verify the environment:
   ```bash
   harbor run --agent oracle --path <path_to_task_folder>
   ```
3. Run programmatic Continuous Integration (CI) and LLM-as-Judge (LLMaJ) checks:
   ```bash
   harbor run -a terminus-2 -m openai/@openai-tbench/gpt-5 -p <path_to_task_folder>
   ```

## 📝 Submission Pipeline

Tasks are iterated upon locally until all Harbor static checks pass. [cite_start]For deployment, the raw contents of the task directory are compressed into a `.zip` file (excluding the parent folder itself) and uploaded to the Snorkel Expert Platform for final CI checks, Rubric generation, and human peer review[cite: 49, 110, 150].
