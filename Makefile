# Default branch target, falls back to master if main is unavailable
BRANCH := $(shell git branch --show-current)
TARGET_BRANCH := $(shell git show-ref --verify --quiet refs/heads/main && echo "main" || echo "master")

# Define the root tasks directory
ROOT_DIR := ~/snorkel-tasks
# Usage: make test_oracle TASK=task-name
TASK_PATH := $(ROOT_DIR)/$(TASK)

.PHONY: test_oracle test_ci upload pre_submit

# 1. Test the Oracle solution
test_oracle:
	@echo "Verifying Oracle solution for $(TASK)..."
	stb run --agent oracle --path $(TASK_PATH)

# 2. Run programmatic CI/LLMaJ checks
test_ci:
	@echo "Running programmatic CI and LLMaJ checks for $(TASK)..."
	stb run -a terminus-2 -m openai/@openai-tbench/gpt-5 -p $(TASK_PATH)

# 3. Automated git upload with branch safety check
upload:
	@echo "Detected target branch: $(TARGET_BRANCH)"
	@git add $(TASK_PATH)
	@git commit -m "Automated update for task: $(TASK)"
	@git push origin $(BRANCH):$(TARGET_BRANCH) || \
	(echo "Failed to push to $(TARGET_BRANCH), attempting fallback to master..." && git push origin $(BRANCH):master)

# 4. Helper to run everything before committing
pre_submit: test_oracle test_ci
	@echo "All tests passed for $(TASK). Ready to upload."
