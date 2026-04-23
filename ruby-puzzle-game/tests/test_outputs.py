import pexpect
import os
import json
import shutil

def test_full_playthrough_with_errors():
    """Tests the hint system, incorrect answers, and final score deductions."""
    target_file = "/app/workspace/src/puzzle_game.rb"
    assert os.path.exists(target_file), f"FAIL: {target_file} not found."

    try:
        child = pexpect.spawn(f'ruby {target_file}', encoding='utf-8', timeout=5)
        
        child.expect("Welcome to the Logic Grid Puzzle!", timeout=2)
        child.expect("Loaded: The Bakery Mix-up", timeout=2)
        
        child.expect(r"Action \(hint/solve/quit\): ")
        child.sendline("hint")
        child.expect("Hint: Alice did not buy the Croissant.")
        
        child.expect(r"Action \(hint/solve/quit\): ")
        child.sendline("solve")
        child.expect(r"Who bought the Tart\? ")
        child.sendline("Bob")
        child.expect("Incorrect!")
        
        child.expect(r"Action \(hint/solve/quit\): ")
        child.sendline("solve")
        child.expect(r"Who bought the Tart\? ")
        child.sendline("Charlie")
        
        child.expect("Correct!")
        child.expect("Game Over! Score: 70")
        child.expect(pexpect.EOF, timeout=2)
        
    except pexpect.TIMEOUT:
        assert False, "FAIL: Game did not output expected text or loop failed."
    except pexpect.EOF:
        assert False, "FAIL: Game crashed or exited unexpectedly."

def test_quit_command():
    """Verifies the quit command successfully breaks the loop and prints the score."""
    target_file = "/app/workspace/src/puzzle_game.rb"
    assert os.path.exists(target_file), f"FAIL: {target_file} not found."
    
    try:
        child = pexpect.spawn(f'ruby {target_file}', encoding='utf-8', timeout=5)
        child.expect("Welcome to the Logic Grid Puzzle!", timeout=2)
        child.expect("Loaded: The Bakery Mix-up", timeout=2)
        
        child.expect(r"Action \(hint/solve/quit\): ")
        child.sendline("quit")
        
        child.expect("Game Over! Score: 100", timeout=2)
        child.expect(pexpect.EOF, timeout=2)
    except Exception as e:
        assert False, f"FAIL: Quit command did not exit properly. {e}"

def test_dynamic_json_loading():
    """Verifies the game reads dynamically from puzzles.json to prevent hardcoding."""
    target_file = "/app/workspace/src/puzzle_game.rb"
    json_path = "/app/puzzles.json"
    backup_path = "/app/puzzles_backup.json"
    
    assert os.path.exists(target_file), f"FAIL: {target_file} not found."
    
    try:
        shutil.copy(json_path, backup_path)
        dummy_data = [{
            "id": 99,
            "title": "The Anti-Cheat Test",
            "categories": ["People", "Pastries"],
            "items": {"People": ["X", "Y"], "Pastries": ["Widget", "Gadget"]},
            "clues": ["Dummy clue"],
            "solution": {"X": "Widget", "Y": "Gadget"}
        }]
        with open(json_path, 'w') as f:
            json.dump(dummy_data, f)
            
        child = pexpect.spawn(f'ruby {target_file}', encoding='utf-8', timeout=5)
        child.expect("Welcome to the Logic Grid Puzzle!", timeout=2)
        child.expect("Loaded: The Anti-Cheat Test", timeout=2)
        
        child.expect(r"Action \(hint/solve/quit\): ")
        child.sendline("solve")
        
        child.expect(r"Who bought the Gadget\? ", timeout=2)
        child.sendline("Y")
        
        child.expect("Correct!", timeout=2)
        child.expect("Game Over! Score: 100", timeout=2)
        child.expect(pexpect.EOF, timeout=2)
        
    except pexpect.TIMEOUT:
        assert False, "FAIL: The agent hardcoded the outputs instead of reading from JSON."
    finally:
        if os.path.exists(backup_path):
            shutil.move(backup_path, json_path)

def test_unrecognized_input_ignored():
    """Verify unknown commands are silently ignored and prompt is redisplayed without extra output."""
    target_file = "/app/workspace/src/puzzle_game.rb"
    assert os.path.exists(target_file), f"FAIL: {target_file} not found."
    
    try:
        child = pexpect.spawn(f'ruby {target_file}', encoding='utf-8', timeout=5)
        child.expect("Welcome to the Logic Grid Puzzle!", timeout=2)
        child.expect("Loaded: The Bakery Mix-up", timeout=2)
        
        child.expect(r"Action \(hint/solve/quit\): ")
        
        # Send gibberish
        child.sendline("foobar")
        
        # Prompt must reappear with no extra output in between
        child.expect(r"Action \(hint/solve/quit\): ", timeout=2)
        
        # Exit cleanly
        child.sendline("quit")
        child.expect("Game Over! Score: 100", timeout=2)
        child.expect(pexpect.EOF, timeout=2)
        
    except pexpect.TIMEOUT:
        assert False, "FAIL: Agent did not silently ignore input or failed to redisplay prompt."
    except Exception as e:
        assert False, f"FAIL: Unexpected error: {e}"