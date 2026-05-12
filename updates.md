## Linear Linked List

**Blocking Issues & Test Alignment**

* **Test Dependency Setup:** `pytest` is unpinned in `environment/Dockerfile` and `tests/test.sh` runs it directly.
* *Action:* Move verifier dependency installation into `tests/test.sh` with pinned versions, and remove unpinned test tooling from the image.


* **Test Alignment:** `test_source_code_structures` enforces a specific `->next` declaration style that the instruction does not require.
* *Action:* Relax that regex check so correct linked list implementations do not fail purely for styling.


* **Test Depth:** `BUCKET_REPORT` and `CATEGORY_REPORT` tests are too shallow and mostly check prefixes, allowing wrong counts to pass.
* *Action:* Strengthen assertions to verify the exact required values.



---

## Moderna Banking

**Status:** Needs Revision

1. **Dependency Installation Deviation:** `tests/test.sh` installs `pytest` with `pip3` after `apt-get python3-pip` instead of following the standard task skeleton (`curl` plus `uv` bootstrap and `uvx` with pinned `pytest` and `pytest-json-ctrf`). Because of this, it never writes `/logs/verifier/ctrf.json`. `test.sh` usually does not need to deviate from the task skeleton.
2. **Overly Strict Structural Checks:** `test_source_code_structures` requires the source to contain the substring `new` or `malloc`, and requires `struct` or `class` names matching `account` or `profile` and `region` or `area` substrings. The instructions only describe a continuous looping transaction history, sample hierarchy, and print order. They never require heap allocation spelling or those specific identifiers. Agents can pass runtime tests yet fail this structural test.
3. **Loose Execution Output Checks:** `test_execution_output` checks that the strings `50` and `20` appear *anywhere* in `stdout`. Since the same output already contains `750` (from FICO) and `2023` (from membership dates), these checks do not actually prove the grocery and gas dollar amounts were printed on the transaction lines.
4. **Gameable Static Checks:** The structural regex checks in `test_source_code_structures` are loose enough that counter loops using `!=` and print statements matched far apart under multiline rules can satisfy them. Three ordered grocery or gas lines alone cannot separate circular pointer walks from array index wrap, adding a gameable path on top of the stdout checks.
5. **Artifact Leakage:** The submission contains `tests/__pycache__` artifacts which should not ship.

---

## React Journal Analyzer

**AutoEval Execution Summary:**

* **Status:** FAILED
* **Build ID:** `CodeExecutionEnvironment:595ee66b-f82c-4f3e-9dd1-b77e9ee558b9`
* *Note:* This task is not tested with any agents as the Oracle solution failed. Please fix the Oracle solution and re-run the tests.

### Quality Check Results

| Status | Check | Description |
| --- | --- | --- |
| ✅ Pass | **Behavior in Task Description** | `instruction.md` clearly specifies all required behaviors: citation extraction via bracket regex `[N]`, word count using `/\b[\w'-]+\b/g`, keyword density for 'quantum' and 'entanglement', section summaries, exact dashboard section names, and the exact JSON schema fields in `<pre id="analysis-output">`. |
| ✅ Pass | **Behavior in Tests** | The Playwright E2E tests (`analyzer.spec.ts`) verify actual computed values across `.md`, `.markdown`, and `.pdf` files. Unit tests confirm structural requirements. Together they cover described behaviors. |
| ✅ Pass | **Informative Test Structure** | Tests are split into clearly named subdirectories (`tests/unit/` and `tests/e2e/`). The orchestrator runs them in sequence. `README.md` documents structure and commands. |
| ✅ Pass | **Anti-Cheating Measures** | Test fixtures are generated at runtime inside `test.sh` via inline script (never accessible to the agent). Dockerfile does not copy `tests/` or `solution/` into the image. E2E assertions check specific computed values. |
| ✅ Pass | **Structured Data Schema** | `instruction.md` explicitly defines the JSON output schema stored in `<pre id="analysis-output">` with exact field names and types. E2E tests validate against this. |
| ✅ Pass | **Pinned Dependencies** | Dockerfile downloads vendor assets at exact pinned versions. `tests/package.json` pins all test dependencies to exact semver versions. |
| ✅ Pass | **Typos** | No meaningful typos found across documentation, configuration, or test files. Terminology is consistent. |
| ✅ Pass | **Tests/Solution in Image** | Dockerfile only creates `/app/vendor` and downloads pinned JS files. It does not `COPY` or `ADD` the `tests/` or `solution/` directories into the image. |
| ❌ Fail | **Test Dependencies in Image** | Test dependencies are not pre-installed in the Docker image. `test.sh` runs `npm install` at execution time, requiring outbound network access, risking flakiness and adding latency. |
| ✅ Pass | **Hardcoded Solution** | `solve.sh` generates a fully implemented React app with real computational functions. No outputs are hardcoded; results are derived from uploaded file content. |
| ✅ Pass | **File Reference Mentioned** | `instruction.md` explicitly names `/app/index.html` as the target file. It is validated by unit tests and the Playwright webServer. |

### ❌ Critical Issues

**1. Unpinned Babel CDN URL Makes Builds Non-Reproducible**

* **Location:** `tbench-task/environment/Dockerfile` (line 6)
* **Problem:** The `@babel/standalone` download URL has no version pin. Every new Docker build fetches whatever "latest" version is live on unpkg.com, meaning a major Babel update could silently break the task.
* **Current Code:**
```bash
curl -sLo /app/vendor/babel.js \
  https://unpkg.com/@babel/standalone/babel.min.js

```


* **Required Fix:**

  ```bash
    curl -sLo /app/vendor/babel.js \
      https://unpkg.com/@babel/standalone@7.27.1/babel.min.js
    ```

### ⚠️ Warnings

**1. All Vendor Libraries Fetched from External CDNs at Build Time**
*   **Location:** `tbench-task/environment/Dockerfile` (lines 3–8)
*   **Problem:** Five vendor JS files are downloaded from CDNs during the docker build. A temporary outage makes the task impossible to build.
*   **Suggested Fix:** Pre-download the five files and commit them to `environment/vendor/`.
    ```bash
    # In Dockerfile:
    COPY vendor/ /app/vendor/
    ```

### 💡 Suggestions

**1. Agent Timeout May Be Tight for This Task's Complexity**
*   **Location:** `tbench-task/task.toml` (line 22)
*   **Problem:** `agent.timeout_sec = 600.0` (10 minutes) is very tight for a task requiring a complete React app, file picker, PDF extraction, algorithm writing, and JSON generation.
*   **Suggested Fix:** Increase to `1800.0` (30 mins) to match the `junior_time_estimate_min = 90` profile.

### Overall Assessment

This is a thoughtfully designed `ui_building` task with clear, exhaustive instructions and excellent test coverage. The dual test strategy (Vitest static checks + Playwright live browser E2E) is highly effective. 

**Recommendation: ❌ REQUIRES FIXES**
Pin the Babel CDN URL to a specific version before use. Optionally, pre-bundle all vendor files in `environment/vendor/` to make the build fully hermetic.

### Test Quality Review

*   **Status:** ✅ ROBUST
*   **Severity:** Minor

**Other Observations:**
1.  **Accept attribute regex enforces extension ordering not in the instruction:** `tests/unit/analyzer.spec.ts:18` requires `.md` to appear before `.markdown` before `.pdf`. The regex should be split to check each extension independently.
2.  **Status message test checks presence only:** `tests/e2e/analyzer.spec.ts` verifies visible text exists near the file input, but does not verify it updates or communicates anything meaningful about the upload state.

### Rubric 1

| Points | Criteria |
| :---: | :--- |
| **+5** | Agent writes `/app/index.html` as a single self-contained client-side HTML file loading React, ReactDOM, Babel, and a PDF library from CDNs with no server, API, or build tool. |
| **+2** | Agent includes a visible file picker accepting `.md`, `.markdown`, and `.pdf` files accompanied by a status message element that updates to reflect the current analysis state. |
| **+3** | Agent triggers document analysis automatically on file selection without requiring an extra submit or analyze button. |
| **+3** | Agent implements citation counting with bracket `[N]` regex, total words with `/\b[\w'-]+\b/g`, and keyword density for 'quantum' and 'entanglement'. |
| **+2** | Agent implements markdown section extraction from lines beginning with `#` and PDF section extraction from short standalone title-case lines. |
| **+3** | Agent renders specific sections ('Citation Frequency', 'Keyword Density', 'Section Summaries') inside a `.sections` container with bolded titles. |
| **+3** | Agent includes `<pre id='analysis-output'>` JSON mirror populated on each file load using the exact specified field names. |
| **+1** | Agent reads back or spot-checks the written HTML file after writing to confirm key structural elements are present before finishing. |
| **-3** | *Penalty:* Agent adds a server-side component, API endpoint, or extra analyze button beyond the file picker. |
| **-2** | *Penalty:* Agent uses a PDF library CDN version whose JavaScript global namespace export differs from the version assumed by the implementation. |

---

## ML Model Management

*   **Stale File Issue:** `solution/solve1.sh` still copies the stale Python `api.py` instead of the required C++ server file, breaking the Milestone 1 oracle path.
*   **Frontend Test Gaps:** The frontend tests rely on static keyword/proximity checks and do not verify that `GET/` serves the actual `index.html`.
*   **Boosted Output Failure:** The boosted output failed review and appears to modify an unrelated PDF/FastAPI task, failing to resolve the blockers.

---

## Circular Linked Lists

*   **Instruction vs. Test Misalignment:** `instruction.md:3` specifies *lowercase* transactional commands as the formal interface, but `tests/test_outputs.cpp` executes only *uppercase* variants. Pass/fail currently depends on handling an undocumented casing rule.
*   **Testing Framework Requirement:** Tests must be rewritten in Python following the `pytest` structure provided in the task skeleton.

---

## Java Fluid Dynamics API

*   **Testing Framework Requirement:** Java tests are not supported. Please rewrite them and use `pytest`.
*   **Dependency Management:** The environment downloads from Maven multiple times, which is not allowed. Pre-download the dependencies and copy them into the environment.
*   **Untested Stubs:** `/environment/src/PhysicsUtils.java` and `/environment/src/SimulationConfig.java` are stubs inside the environment that are never mentioned or tested, yet contain `TODO` comments.
*   **Instruction Clean-up:** Remove `# [SIM-88] Fluid Dynamics API (Java) — need this by EOD` from `instruction.md`. The instructions are heavily formatted and do not match the prompt style guide.


