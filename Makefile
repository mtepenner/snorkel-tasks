# Detect the correct remote target branch (main vs master) to prevent GitHub PRs
TARGET_BRANCH := $(shell git branch -r | grep -q "origin/main" && echo "main" || echo "master")

# Automatically detect the OS and set the correct root directory
ifeq ($(OS),Windows_NT)
  ROOT_DIR := C:/Users/mtepe/Scripts/snorkel-ai/tasks
else
  ROOT_DIR := $(HOME)/snorkel-tasks
endif

# Use wildcard to detect if a specific task was provided
ifdef TASK
  TASK_PATH := $(ROOT_DIR)/$(TASK)
  COMMIT_MSG := "Automated update for task: $(TASK)"
else
  TASK_PATH := $(ROOT_DIR)
  COMMIT_MSG := "Automated bulk update for all tasks"
endif

.PHONY: test_oracle test_ci upload pre_submit git_pull zip

# Helper: Pull latest changes and rebase to prevent messy GitHub merges
git_pull:
	@echo "Syncing with remote $(TARGET_BRANCH) to avoid merge conflicts..."
	@git pull --rebase origin $(TARGET_BRANCH)

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

# 3. Automated git upload (Direct to target branch)
upload:
	@echo "Detected remote default branch: $(TARGET_BRANCH)"
	@git add "$(TASK_PATH)"
	@git commit -m $(COMMIT_MSG) || true
	@echo "Pushing directly to origin/$(TARGET_BRANCH) to bypass manual merge..."
	@git push origin HEAD:$(TARGET_BRANCH)

# 4. Helper to run everything before committing
pre_submit: test_oracle test_ci
	@echo "All tests passed for $(TASK_PATH). Ready to upload."

# 5. Zip a task
zip:
ifndef TASK
	$(error TASK is not set. Please specify a task folder, e.g., make zip TASK=name-of-task)
endif
	@echo "Zipping contents of $(TASK_PATH) into $(TASK_PATH)/$(TASK).zip..."
	@cd "$(TASK_PATH)" && zip -r "$(TASK).zip" . -x "*.git*" -x "$(TASK).zip"
	@echo "Success: $(TASK_PATH)/$(TASK).zip created."