import pexpect
import os

def test_full_playthrough_with_errors():
    """Tests the hint system, incorrect answers, and final score deductions."""
    target_file = "/app/workspace/src/puzzle_game.rb"
    assert os.path.exists(target_file), f"FAIL: {target_file} not found."

    try:
        child = pexpect.spawn(f'ruby {target_file}', encoding='utf-8', timeout=5)
        
        # 1. Startup
        child.expect("Welcome to the Logic Grid Puzzle!", timeout=2)
        child.expect("Loaded: The Bakery Mix-up", timeout=2)
        
        # 2. Hint (-10 points)
        child.expect(r"Action \(hint/solve/quit\): ")
        child.sendline("hint")
        child.expect("Hint: Alice did not buy the Croissant.")
        
        # 3. Incorrect Solve (-20 points) -> proves the loop works
        child.expect(r"Action \(hint/solve/quit\): ")
        child.sendline("solve")
        child.expect(r"Who bought the Tart\? ")
        child.sendline("Bob")
        child.expect("Incorrect!")
        
        # 4. Correct Solve (Score should be 100 - 10 - 20 = 70)
        child.expect(r"Action \(hint/solve/quit\): ")
        child.sendline("solve")
        child.expect(r"Who bought the Tart\? ")
        child.sendline("Charlie")
        
        child.expect("Correct!")
        child.expect("Game Over! Score: 70")
        
    except pexpect.TIMEOUT:
        assert False, "FAIL: Game did not output expected text or loop failed."
    except pexpect.EOF:
        assert False, "FAIL: Game crashed or exited unexpectedly."

def test_quit_command():
    """Verifies the quit command successfully breaks the loop."""
    target_file = "/app/workspace/src/puzzle_game.rb"
    
    # --- ADDED THIS LINE TO FIX THE WARNING ---
    assert os.path.exists(target_file), f"FAIL: {target_file} not found."
    
    try:
        child = pexpect.spawn(f'ruby {target_file}', encoding='utf-8', timeout=5)
        child.expect(r"Action \(hint/solve/quit\): ")
        child.sendline("quit")
        
        # Expect EOF meaning the process closed gracefully
        child.expect(pexpect.EOF, timeout=2)
    except Exception as e:
        assert False, f"FAIL: Quit command did not exit properly. {e}"