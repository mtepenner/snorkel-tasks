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

def test_execution_output():
    """Run the compiled binary and check stdout for the hierarchical data."""
    result = subprocess.run([EXECUTABLE], capture_output=True, text=True)
    output = result.stdout.lower()
    
    # Verify output data
    assert "seattle" in output, "Output missing region data."
    assert "john doe" in output, "Output missing account holder data."
    assert "grocery" in output, "Output missing transaction data."
    assert "50" in output, "Transaction amount $50.0 missing."
    
    # Verify hierarchical printing of region -> account -> transaction
    lines = output.strip().split('\n')
    try:
        region_idx = next(i for i, line in enumerate(lines) if "seattle" in line)
        acct_idx = next(i for i, line in enumerate(lines) if "john doe" in line)
        txn_idx = next(i for i, line in enumerate(lines) if "grocery" in line)
        assert region_idx < acct_idx < txn_idx, "Output is not in the correct hierarchical order."
    except StopIteration:
        assert False, "Could not find all required hierarchical elements in output lines."