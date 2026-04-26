# Detect the correct remote target branch using native git and strip any PowerShell ghost spaces
TARGET_BRANCH := $(strip $(shell git show-ref --verify --quiet refs/remotes/origin/main && echo main))

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
	stb harbor run -a terminus-2 -m "@openai/@openai/gpt-5.2" -p "$(TASK_PATH)"
	stb harbor run -a terminus-2 -m "@anthropic/claude-opus-4-6" -p "$(TASK_PATH)"
	

# 3. Automated git upload (Direct to target branch with built-in sync)
upload:
	@echo "Detected remote default branch: $(TARGET_BRANCH)"
	@git add "$(TASK_PATH)"
	@git commit -m $(COMMIT_MSG) || true
	@echo "Pulling any recent manual GitHub merges..."
	@git pull --rebase origin $(TARGET_BRANCH)
	@echo "Pushing directly to origin/$(TARGET_BRANCH) to bypass manual merge..."
	@git push origin HEAD:$(TARGET_BRANCH)

# 4. Helper to run everything before committing
pre_submit: test_oracle test_ci
	stb harbor view jobs

# 5. Zip a task
zip:
ifndef TASK
	$(error TASK is not set. Please specify a task folder, e.g., make zip TASK=name-of-task)
endif
	@echo "Zipping contents of $(TASK_PATH) into $(TASK_PATH)/$(TASK).zip..."
ifeq ($(OS),Windows_NT)
	@powershell -NoProfile -Command "$$ErrorActionPreference = 'Stop'; $$hasPyLauncher = Get-Command py -ErrorAction SilentlyContinue; $$hasPython = Get-Command python -ErrorAction SilentlyContinue; if (-not $$hasPyLauncher -and -not $$hasPython) { throw 'Python is required to build task zips on Windows.' }; $$env:TASK_ROOT = (Resolve-Path '$(TASK_PATH)').Path; $$env:TASK_ZIP = '$(TASK).zip'; $$tmp = Join-Path $$env:TEMP 'make_task_zip.py'; Set-Content -Path $$tmp -Value @('import os','import pathlib','import zipfile','root = pathlib.Path(os.environ[''TASK_ROOT''])','zip_name = os.environ[''TASK_ZIP'']','zip_path = root / zip_name','skip_dirs = {''.git'', ''__pycache__'', ''.pytest_cache'', ''node_modules''}','if zip_path.exists(): zip_path.unlink()','with zipfile.ZipFile(zip_path, ''w'', compression=zipfile.ZIP_DEFLATED) as archive:','    for current_root, dirnames, filenames in os.walk(root):','        dirnames[:] = [directory for directory in dirnames if directory not in skip_dirs]','        current_path = pathlib.Path(current_root)','        for filename in sorted(filenames):','            path = current_path / filename','            if path.is_symlink(): continue','            rel = path.relative_to(root).as_posix()','            if rel.endswith(''.zip''): continue','            archive.write(path, arcname=rel)'); if ($$hasPyLauncher) { & py -3 $$tmp } else { & python $$tmp }; if ($$LASTEXITCODE -ne 0) { Remove-Item $$tmp -ErrorAction SilentlyContinue; exit $$LASTEXITCODE }; Remove-Item $$tmp"
else
	@cd "$(TASK_PATH)" && zip -r "$(TASK).zip" . -x "*.git*" -x "*.zip" -x "*/node_modules/*" -x "*/__pycache__/*" -x "*/.pytest_cache/*"
endif
	@echo "Success: $(TASK_PATH)/$(TASK).zip created."