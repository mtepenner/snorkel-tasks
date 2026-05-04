import os
import subprocess

SOURCE_FILE = "/app/workspace/src/moderna_banking.cpp"
EXECUTABLE = "/usr/local/bin/moderna-app"

def test_source_file_exists():
    """Verify the agent placed the source code in the correct absolute path."""
    assert os.path.exists(SOURCE_FILE), f"Source file {SOURCE_FILE} is missing."

def test_executable_exists():
    """Verify the agent compiled the code to the requested binary path."""
    assert os.path.exists(EXECUTABLE), f"Executable {EXECUTABLE} is missing."
    assert os.access(EXECUTABLE, os.X_OK), f"{EXECUTABLE} is not executable."

def test_data_structures_used():
    """Statically analyze the C++ file to ensure manual memory management was used."""
    with open(SOURCE_FILE, "r") as f:
        code = f.read().lower()
    
    # Check for pointers and node structures rather than standard library vectors
    assert "*" in code, "No pointers found. Must implement manual memory tracking."
    assert "next" in code, "Node 'next' pointer missing in implementation."
    assert "double account_balance" in code or "double amount" in code, "Missing required node properties."

def test_execution_output():
    """Run the compiled binary and check stdout for the hierarchical data."""
    result = subprocess.run([EXECUTABLE], capture_output=True, text=True)
    output = result.stdout.lower()
    
    # Verify hierarchical printing of region -> account -> transaction
    assert "seattle" in output, "Output missing region data."
    assert "john doe" in output, "Output missing account holder data."
    assert "grocery" in output, "Output missing transaction data."