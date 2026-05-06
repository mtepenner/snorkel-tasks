import os
import subprocess
import re

SOURCE_FILE = "/app/workspace/src/moderna_banking.cpp"
EXECUTABLE = "/usr/local/bin/moderna-app"

def test_source_file_exists():
    """Verify the agent placed the source code in the correct absolute path."""
    assert os.path.exists(SOURCE_FILE), f"Source file {SOURCE_FILE} is missing."

def test_source_code_structures():
    """Verify the source code uses appropriate data structures (struct/class) and circular concepts."""
    with open(SOURCE_FILE) as f:
        src = f.read().lower()
    assert "struct" in src or "class" in src, "No struct/class defined in the source code."
    
    assert re.search(r"(struct|class)\s+\w+\s*\{[^}]*\*\s*\w+", src, re.DOTALL), "No linked list node with pointer found."
    assert "new " in src or "malloc" in src, "No dynamic allocation found."
    assert re.search(r"->\s*\w+\s*=", src) or re.search(r"\.\s*\w+\s*=", src), "No linked list linking found."

    assert re.search(r"(struct|class)\s+\w*(account|profile)\w*\s*\{", src, re.IGNORECASE), "No Account struct/class found"
    assert re.search(r"(struct|class)\s+\w*(region|area)\w*\s*\{", src, re.IGNORECASE), "No Region struct/class found"
    
    assert re.search(r"while\s*\(.*(->\w+|!=)", src) or re.search(r"do\s*\{.*(->\w+|!=)", src) or re.search(r"for\s*\(.*(->\w+|!=)", src), "No traversal loop found in source."

    loop_match = re.search(r"(while|for|do)\s*[\({].*?(cout|printf|print)", src, re.DOTALL)
    assert loop_match, "Traversal loop must contain print statements"

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
    
    assert "balance" in output and "$" in output, "Account balance not displayed in output."
    
    assert "fico" in output or "750" in output, "Account FICO score not displayed in output."
    assert "membership" in output or "2023" in output, "Membership date not in output."
    assert "expir" in output or "2030" in output, "Expiration date not in output."
    
    assert "grocery" in output, "Output missing first transaction data (Grocery)."
    assert "50" in output, "First transaction amount $50.0 missing."
    
    assert "gas" in output, "Output missing second transaction data (Gas)."
    assert "20" in output, "Second transaction amount $20.0 missing."
    
    # Verify hierarchical printing of region -> account -> transaction
    lines = output.strip().split('\n')
    try:
        region_idx = next(i for i, line in enumerate(lines) if "seattle" in line)
        acct_idx = next(i for i, line in enumerate(lines) if "john doe" in line)
        txn_idx = next(i for i, line in enumerate(lines) if "grocery" in line)
        assert region_idx < acct_idx < txn_idx, "Output is not in the correct hierarchical order."
    except StopIteration:
        assert False, "Could not find all required hierarchical elements in output lines."

    # Verify circular nature by seeing if they printed transaction 1, then transaction 2, then transaction 1 again
    txn_lines = [line for line in lines if "transaction:" in line or "grocery" in line or "gas" in line]
    assert len(txn_lines) >= 3, "Output did not print at least 3 transactions to demonstrate the circular loop."
    
    txn_content = " ".join(txn_lines)
    assert re.search(r"\d{4}-\d{2}-\d{2}", txn_content), "Transaction dates not displayed in output."
    
    assert "grocery" in txn_lines[0], "First transaction printed was not Grocery."
    assert "gas" in txn_lines[1], "Second transaction printed was not Gas."
    assert "grocery" in txn_lines[2], "Third transaction printed was not Grocery (failed to demonstrate circular wrapper)."
