-------
5.12.26
-------

COMMENTS FOR linear-linked-list :

The main blocking issue is test dependency setup, because `pytest` is unpinned in `environment/Dockerfile` and `tests/test.sh` runs it directly. Move verifier dependency installation into `tests/test.sh` with pinned versions, and remove unpinned test tooling from the image. There is also a test alignment issue in `test_source_code_structures`, because one regex enforces a specific `->next` declaration style that the instruction does not require. Please relax that check so correct linked list implementations do not fail for style only. Also, `BUCKET_REPORT` and `CATEGORY_REPORT` tests are too shallow and mostly check prefixes, so wrong counts can still pass. Strengthen those assertions to verify exact required values.

COMMENTS FOR moderna-banking :

Needs Revision.

1) tests/test.sh installs pytest with pip3 after apt-get python3-pip instead of following the standard task skeleton curl plus uv bootstrap and uvx with pinned pytest and pytest-json-ctrf, so it never writes /logs/verifier/ctrf.json. test.sh usually does not need to deviate from the task skeleton.

2) test_source_code_structures requires the source to contain the substring new or malloc and requires struct or class names matching account or profile and region or area substrings, but the instructions only describe a continuous looping transaction history and the sample hierarchy and print order. They never require heap allocation spelling or those identifier shapes, and agent runs can pass the runtime tests yet fail only this structural test.

3) test_execution_output checks that the strings 50 and 20 appear anywhere in stdout while the same output already contains 750 from FICO and 2023 from membership dates, so those checks do not prove the grocery and gas dollar amounts were printed on the transaction lines.

4) The structural regex checks in test_source_code_structures are loose enough that counter loops using != and print statements matched far apart under multiline rules can satisfy them, and three ordered grocery or gas lines alone cannot separate circular pointer walks from array index wrap, so the static checks add a gameable path on top of the stdout checks.

5) The submission contains tests/__pycache__ artifacts which should not ship.

COMMENTS FOR react-journal-analyzer :

AutoEval Execution Summary: AutoEval execution failed. Build status: FAILED. Build ID: CodeExecutionEnvironment:595ee66b-f82c-4f3e-9dd1-b77e9ee558b9.

This task is not tested with any agents as the Oracle solution failed. Please fix the Oracle solution and re-run the tests.

## Quality Check Results
✅ pass - behavior_in_task_description: instruction.md clearly specifies all required behaviors: citation extraction via bracket regex [N], word count using /\b[\w'-]+\b/g, keyword density for 'quantum' and 'entanglement', section summaries as the longest sentence per section, exact dashboard section names ('Citation Frequency', 'Keyword Density', 'Section Summaries'), and the exact JSON schema fields in <pre id="analysis-output">.
✅ pass - behavior_in_tests: The Playwright E2E tests (analyzer.spec.ts) verify actual computed values — citation counts, keyword density figures, and section summary text — for all three file types (.md, .markdown, .pdf). The unit tests confirm structural requirements (vendor script tags, input accept attribute, pre#analysis-output, dashboard section titles). Together they cover the behaviors described in instruction.md.
✅ pass - informative_test_structure: Tests are split into clearly named subdirectories: tests/unit/ for structural/static checks via Vitest and tests/e2e/ for full interaction tests via Playwright. The test.sh orchestrator runs them in sequence and writes a reward signal. The README.md documents the structure and available commands.
✅ pass - anti_cheating_measures: Test fixtures (paper.md, paper.markdown, paper.pdf) are generated at runtime inside test.sh via an inline Node.js script, so they are never accessible to the agent during development. The Dockerfile does not copy tests/ or solution/ into the image. E2E assertions check specific computed values (citation counts, keyword density, section text), making it infeasible to pass by hardcoding.
✅ pass - structured_data_schema: instruction.md explicitly defines the JSON output schema stored in <pre id="analysis-output"> with exact field names: fileType (string), citations (array of {id, count}), totalWords (number), keywordDensity (object with quantum/entanglement keys), and sectionSummaries (array of {section, summary}). The E2E tests validate against this schema.
✅ pass - pinned_dependencies: The Dockerfile downloads vendor assets at exact pinned versions via CDN URLs (React 18.3.1, ReactDOM 18.3.1, Babel standalone, PDF.js 3.11.174 + worker). tests/package.json pins all test dependencies to exact semver versions: @playwright/test@1.49.0, vitest@2.1.6, happy-dom@15.11.7, serve@14.2.4.
✅ pass - typos: No meaningful typos were found across instruction.md, task.toml, Dockerfile, solve.sh, test files, or configuration files. Field names, section headings, and technical terms are spelled consistently throughout.
✅ pass - tests_or_solution_in_image: The Dockerfile only creates /app/vendor and downloads the pinned vendor JS files there. It does not COPY or ADD the tests/ or solution/ directories into the image, keeping the agent's workspace clean and uncontaminated.
❌ fail - test_deps_in_image: Test dependencies (vitest, @playwright/test, happy-dom, serve) are not pre-installed in the Docker image. test.sh runs npm install at test execution time, requiring outbound network access to the npm registry. This risks flakiness if the registry is unavailable and adds latency to every test run.
✅ pass - hardcoded_solution: solve.sh generates /app/index.html containing a fully implemented React app with real computational functions: countWords() applies the word regex, keywordStats() computes density, extractSummary() picks the longest sentence, and analyzeDocument() ties them together. No outputs are hardcoded; results are derived from the uploaded file's content.
✅ pass - file_reference_mentioned: instruction.md explicitly names /app/index.html as the file the agent must create. The path is referenced early in the instructions and is the target validated by both the unit test (checks file existence and content) and the Playwright webServer (serves /app on port 3000).

================================================================================
                         REVIEW REPORT: tbench-task
================================================================================

Status:        ❌ FAIL
Task Location: /root/harbor_tasks/tbench-task

--------------------------------------------------------------------------------
SUMMARY
--------------------------------------------------------------------------------

This ui_building task asks agents to create a single-file React application at
/app/index.html that analyzes scientific papers in Markdown or PDF format,
computing citation frequency, keyword density for "quantum" and "entanglement",
and section summaries. The solution delivers a complete JSX-based React app that
loads vendor libraries from a pre-built /app/vendor directory. The test suite
combines Vitest unit tests (static HTML contract checks) and Playwright E2E tests
(full browser interaction with generated fixtures), providing excellent behavior
coverage across .md, .markdown, and .pdf uploads.

================================================================================
                            CRITICAL ISSUES ❌
================================================================================

--------------------------------------------------------------------------------
1. Unpinned Babel CDN URL Makes Builds Non-Reproducible
--------------------------------------------------------------------------------

File:    tbench-task/environment/Dockerfile (line 6)
Problem: The @babel/standalone download URL has no version pin. Every new Docker
         build fetches whatever "latest" version is live on unpkg.com at that
         moment. A major Babel update could silently change JSX compilation
         semantics, breaking agents' solutions or the oracle itself without any
         code change in the task.

Current code:
┌─────────────────────────────────────────────────────────────────────────────┐
│  curl -sLo /app/vendor/babel.js \                                           │
│    https://unpkg.com/@babel/standalone/babel.min.js                         │
└─────────────────────────────────────────────────────────────────────────────┘

Required fix:
┌─────────────────────────────────────────────────────────────────────────────┐
│  curl -sLo /app/vendor/babel.js \                                           │
│    https://unpkg.com/@babel/standalone@7.27.1/babel.min.js                  │
└─────────────────────────────────────────────────────────────────────────────┘

Explanation: All other vendor downloads in the Dockerfile pin exact versions
(react@18.3.1, pdf.js/3.11.174). Babel must follow the same pattern. Pin to a
specific semver (e.g. 7.27.1) so every image build produces an identical vendor
directory regardless of when it is built.

================================================================================
                              WARNINGS ⚠️
================================================================================

--------------------------------------------------------------------------------
1. All Vendor Libraries Fetched from External CDNs at Build Time
--------------------------------------------------------------------------------

File:    tbench-task/environment/Dockerfile (lines 3–8)
Problem: All five vendor JS files are downloaded from unpkg.com and
         cdnjs.cloudflare.com during docker build. CDN availability is not
         guaranteed; a temporary outage makes the task impossible to build. The
         instruction itself reads "from the provided vendor directory," implying
         these files should be bundled with the task, not fetched on demand.

Current approach: Five curl downloads from external CDNs; image build fails if
                  either CDN is unreachable.

Suggested fix:
┌─────────────────────────────────────────────────────────────────────────────┐
│  # Pre-download the five files and commit them to environment/vendor/:       │
│  environment/vendor/react.js                                                │
│  environment/vendor/react-dom.js                                            │
│  environment/vendor/babel.js                                                │
│  environment/vendor/pdf.js                                                  │
│  environment/vendor/pdf.worker.js                                           │
│                                                                             │
│  # Then in Dockerfile:                                                      │
│  COPY vendor/ /app/vendor/                                                  │
└─────────────────────────────────────────────────────────────────────────────┘

Explanation: Committing the versioned vendor files into environment/ eliminates
the CDN dependency entirely and makes the build hermetic. The task already pins
exact CDN versions; pre-downloading is a small step that removes the network
risk.

================================================================================
                             SUGGESTIONS 💡
================================================================================

--------------------------------------------------------------------------------
1. Agent Timeout May Be Tight for This Task's Complexity
--------------------------------------------------------------------------------

File:    tbench-task/task.toml (line 22)

Current approach: agent.timeout_sec = 600.0 (10 minutes) for a task that
                  requires building a complete React app with a file picker, PDF
                  text extraction via pdf.js, Markdown section parsing, keyword
                  density computation, section summaries, and a JSON mirror — all
                  in a single HTML file.

Suggested improvement:
┌─────────────────────────────────────────────────────────────────────────────┐
│  [agent]                                                                    │
│  timeout_sec = 1800.0                                                       │
└─────────────────────────────────────────────────────────────────────────────┘

Rationale: The instruction is highly detailed (three dense paragraphs of exact
requirements), and agents commonly iterate on PDF extraction heuristics. 1800 s
(30 min) better matches the junior_time_estimate_min = 90 profile.

================================================================================
                            OVERALL ASSESSMENT
================================================================================

This is a thoughtfully designed ui_building task with clear, exhaustive
instructions and excellent test coverage: the Vitest unit suite validates static
HTML structure while the Playwright E2E suite drives a real browser through
Markdown (.md and .markdown) and PDF uploads, checking every required JSON field
and dashboard section. The one critical flaw — an unpinned Babel CDN URL — is a
one-line fix but matters for long-term reproducibility.

Key Strengths:
  ✓ Comprehensive behavior coverage across all instruction requirements
  ✓ Dual test strategy (Vitest static checks + Playwright live browser E2E)
  ✓ Precise JSON schema and DOM selectors defined in both instructions and tests

Key Weaknesses:
  ✗ Unpinned @babel/standalone CDN URL breaks build reproducibility
  ✗ All vendor libraries rely on external CDN availability at build time

Evaluates: Single-file React architecture, PDF text extraction via pdf.js,
           algorithmic text analysis (word counting, regex-based keyword density,
           section parsing), structured JSON output

================================================================================
  RECOMMENDATION: ❌ REQUIRES FIXES

  Pin the Babel CDN URL to a specific version (e.g. @babel/standalone@7.27.1)
  before use. Optionally pre-bundle all vendor files in environment/vendor/ to
  make the build fully hermetic.
================================================================================

================================================================================
                      TEST QUALITY REVIEW: tbench-task
================================================================================

Status:    ✅ ROBUST
Severity:  Minor

================================================================================
                         OVERALL ASSESSMENT
================================================================================

Recommendation: ACCEPT
The test suite provides strong end-to-end correctness assertions on all core
algorithmic constraints, test fixtures are generated at verification time
(inaccessible to the agent), and no shortcut solution exists.

Strengths:  Comprehensive Playwright e2e tests verify exact numerical outputs
(citations, word counts, keyword density) and exact section summaries for both
Markdown and PDF uploads, using a reference implementation that recomputes
expected values from fixture content the agent never sees.

Weaknesses: The unit test enforces a specific ordering of file extensions in the
accept attribute not mandated by the instruction; the status message test only
checks structural presence rather than meaningful content.

================================================================================
                                 SUMMARY
================================================================================

The test suite covers all core requirements through three e2e tests (Markdown
.md, Markdown .markdown, PDF) that upload fixture files, wait for analysis
output, and verify exact JSON field values including fileType, citations,
totalWords, keywordDensity, and sectionSummaries. A unit test validates the
static HTML structure. Fixtures are created by test.sh at verification time,
making them invisible to the agent. The only gaps are minor: an implicit
ordering constraint on the accept attribute and a structural-only check for
the status message.

================================================================================
                         OTHER OBSERVATIONS 💡
================================================================================

--------------------------------------------------------------------------------
1. Accept attribute regex enforces extension ordering not in the instruction
--------------------------------------------------------------------------------

Where:   tests/unit/analyzer.spec.ts:18
Problem: The regex requires `.md` to appear before `.markdown` before `.pdf`
in the accept attribute value. The instruction merely lists the three formats
without specifying their order in the HTML attribute.

Current test:
┌─────────────────────────────────────────────────────────────────────────────┐
│  expect(htmlContent).toMatch(                                              │
│    /accept=["'][^"']*\.md[^"']*\.markdown[^"']*\.pdf[^"']*["']/i          │
│  );                                                                        │
└─────────────────────────────────────────────────────────────────────────────┘

Required fix:
┌─────────────────────────────────────────────────────────────────────────────┐
│  // Check each extension is present independently:                          │
│  expect(htmlContent).toMatch(/accept=["'][^"']*\.md\b/i);                  │
│  expect(htmlContent).toMatch(/accept=["'][^"']*\.markdown/i);              │
│  expect(htmlContent).toMatch(/accept=["'][^"']*\.pdf/i);                   │
└─────────────────────────────────────────────────────────────────────────────┘

Explanation: This is a phantom spec — a correct implementation using
`accept=".pdf,.markdown,.md"` would fail the regex despite satisfying the
instruction. In practice, most agents will follow the instruction's listing
order, so impact is low.

--------------------------------------------------------------------------------
2. Status message test checks presence only, not meaningful content
--------------------------------------------------------------------------------

Where:   tests/e2e/analyzer.spec.ts:21-65
Problem: The `expectUploadStatusMessage` helper verifies that some visible
text of 8+ characters exists near the file input, but does not verify it
communicates anything meaningful about upload state (e.g., "ready",
"processing", or a file name).

Current test:
┌─────────────────────────────────────────────────────────────────────────────┐
│  // Finds any visible sibling text >= 8 chars near the file input          │
│  return messages;  // just checks .not.toHaveLength(0)                     │
└─────────────────────────────────────────────────────────────────────────────┘

Required fix:
┌─────────────────────────────────────────────────────────────────────────────┐
│  // Optionally verify the message updates after upload:                     │
│  const msgBefore = await getStatusMessage(page);                           │
│  await page.setInputFiles('input[type="file"]', fixture);                  │
│  const msgAfter = await getStatusMessage(page);                            │
│  expect(msgAfter).not.toBe(msgBefore);                                     │
└─────────────────────────────────────────────────────────────────────────────┘

Explanation: The instruction says "accompanied by a status message" which
implies dynamic feedback. A static placeholder like "Document Analyzer App"
(which is >= 8 chars) would satisfy the current test. This is a secondary
constraint, so it does not affect the overall ROBUST verdict.

================================================================================

# Rubric 1
Agent writes /app/index.html as a single self-contained client-side HTML file loading React, ReactDOM, Babel, and a PDF library from CDNs with no server, API, or build tool, +5
Agent includes a visible file picker accepting .md, .markdown, and .pdf files accompanied by a status message element that updates to reflect the current analysis state, +2
Agent triggers document analysis automatically on file selection without requiring an extra submit or analyze button, +3
Agent implements citation counting with bracket [N] regex, totalWords with /\b[\w'-]+\b/g, and keywordDensity for 'quantum' and 'entanglement' each with count and density (count/totalWords rounded to 3 decimals), +3
Agent implements markdown section extraction from lines beginning with # and PDF section extraction from short standalone title-case lines (1–4 words), +2
Agent renders sections titled exactly 'Citation Frequency', 'Keyword Density', and 'Section Summaries' with summaries inside a .sections container and each section title wrapped in a <strong> element, +3
Agent includes <pre id='analysis-output'> JSON mirror that is populated on each file load using the exact field names fileType, citations, totalWords, keywordDensity, and sectionSummaries, +3
Agent reads back or spot-checks the written HTML file after writing to confirm key structural elements are present before finishing, +1
Agent adds a server-side component, API endpoint, or extra analyze button beyond the file picker, -3
Agent uses a PDF library CDN version whose JavaScript global namespace export differs from the version assumed by the implementation, without verifying compatibility, -2

COMMENTS FOR ml-model-mgmt :

The solution/solve1.sh still copies the stale Python api.py instead of the required C++ server file, so the milestone 1 oracle path is broken. The frontend tests also rely on static keyword/proximity checks and don’t verify that GET/ serves the actual index.html. The boosted output failed review and appears to modify an unrelated PDF/FastAPI task, so it does not resolve these blockers.

COMMENTS FOR circular-linked-lists :

- `instruction.md:3` specifies lowercase transactional commands as the formal interface. `tests/test_outputs.cpp:219–223,245–252,273–279,297–302` executes only uppercase variants for those same commands. Because pass/fail depends on handling a casing rule not documented in the instructions, the spec and tests are not aligned.

- Tests must be written in python following the pytest structure provided in the task skeleton.


COMMENTS FOR java-fluid-dynamics-api :

java test are not supported please rewrite them and use pytest

you download from maven multiple times but this isnt allowed, predownload and copy them into the environment

/environment/src/PhysicsUtils.java and /environment/src/SimulationConfig.java are stubs inside the env but are never mentioned or tested but have todo comments

remove # [SIM-88] Fluid Dynamics API (Java) — need this by EOD from the instruction.md

instructions are heavily formatted and does not match the prompt style guide


