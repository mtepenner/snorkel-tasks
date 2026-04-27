#!/bin/bash
set -uo pipefail

ensure_uv() {
  if command -v uvx >/dev/null 2>&1; then
    return 0
  fi

  if command -v curl >/dev/null 2>&1; then
    export UV_UNMANAGED_INSTALL="/usr/local/bin"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    hash -r
  elif command -v wget >/dev/null 2>&1; then
    export UV_UNMANAGED_INSTALL="/usr/local/bin"
    wget -qO- https://astral.sh/uv/install.sh | sh
    hash -r
  else
    python3 -m pip install --no-cache-dir uv
    hash -r
  fi

  if ! command -v uvx >/dev/null 2>&1 && command -v uv >/dev/null 2>&1; then
    ln -sf "$(command -v uv)" /usr/local/bin/uvx 2>/dev/null || true
    hash -r
  fi

  command -v uvx >/dev/null 2>&1
}

if ! ensure_uv; then
  echo 0 > /logs/verifier/reward.txt
  exit 1
fi

if [ "$PWD" = "/" ]; then
    echo "Error: No working directory set."
    exit 1
fi

MILESTONE="all"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --milestone=*)
      MILESTONE="${1#*=}"
      shift
      ;;
    *)
      shift
      ;;
  esac
done

TEST_FILES=()
if [[ "$MILESTONE" == "all" ]]; then
  TEST_FILES=(/tests/test_m*.py)
else
  TEST_FILES=(/tests/test_m${MILESTONE}.py)
fi

uvx \
  -p 3.12 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  -w flask==3.0.0 \
  -w pandas==2.1.4 \
  -w numpy==1.26.4 \
  -w scikit-learn==1.3.2 \
  -w beautifulsoup4==4.12.3 \
  pytest --ctrf /logs/verifier/ctrf.json "${TEST_FILES[@]}" -rA

status=$?

if [ $status -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

exit $status
