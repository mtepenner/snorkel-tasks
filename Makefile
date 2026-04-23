# Default branch target, falls back to master if main is unavailable
BRANCH := $(shell git branch --show-current)
TARGET_BRANCH := $(shell git show-ref --verify --quiet refs/heads/main && echo "main" || echo "master")

# Automatically detect the OS and set the correct root directory
ifeq ($(OS),Windows_NT)
  ROOT_DIR := C:/Users/mtepe/Scripts/snorkel-ai/tasks
else
  ROOT_DIR := $(HOME)/snorkel-tasks
endif

# Use wildcard to detect if a specific task was provided
ifdef TASK
  TASK_PATH := $(ROOT_DIR)/$(TASK)
  COMMIT_MSG := Automated update for task: $(TASK)
else
  TASK_PATH := $(ROOT_DIR)
  COMMIT_MSG := Automated bulk update for all tasks
endif

.PHONY: test_oracle test_ci upload pre_submit git_pull zip

# Helper: Pull latest changes
git_pull:
	@echo "Pulling latest changes from origin..."
	@git pull origin $(BRANCH)

# 1. Test the Oracle solution
test_oracle: git_pull
ifndef TASK
	$(error TASK is not set. Please specify a task folder, e.g., make test_oracle TASK=name-of-task)
endif
	@echo "Verifying Oracle solution for $(TASK)..."
	stb harbor run --agent oracle --path "$(TASK_PATH)"

# 2. Run programmatic CI/LLMaJ checks
test_ci: git_pull
ifndef TASK
	$(error TASK is not set. Please specify a task folder, e.g., make test_ci TASK=name-of-task)
endif
	@echo "Running programmatic CI and LLMaJ checks for $(TASK)..."
	stb harbor run -a terminus-2 -m openai/@openai-tbench/gpt-5 -p "$(TASK_PATH)"

# 3. Automated git upload (Bulk or Specific)
upload:
	@echo "Detected target branch: $(TARGET_BRANCH)"
	@git add "$(TASK_PATH)"
	@git commit -m "$(COMMIT_MSG)"
	@git push origin $(BRANCH):$(TARGET_BRANCH) || \
	(echo "Failed to push to $(TARGET_BRANCH), attempting fallback to master..." && git push origin $(BRANCH):master)

# 4. Helper to run everything before committing
pre_submit: test_oracle test_ci
	stb harbor view jobs

# 5. Zip a task
zip:
ifndef TASK
	$(error TASK is not set. Please specify a task folder, e.g., make zip TASK=name-of-task)
endif
	@echo "Zipping contents of $(TASK_PATH) into $(TASK_PATH)/$(TASK).zip..."
	@cd "$(TASK_PATH)" && zip -r "$(TASK).zip" . -x "*.git*" -x "$(TASK).zip"
	@echo "Success: $(TASK_PATH)/$(TASK).zip created."