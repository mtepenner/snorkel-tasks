import os
import subprocess
import re
import pathlib
import pytest

SRC = pathlib.Path("/app/workspace/src")
BIN = pathlib.Path("/tmp/comicon_roster")
SOURCE_FILE = SRC / "comicon_roster.cpp"

@pytest.fixture(scope="session", autouse=True)
def compile_binary():
    """Compile the candidate source with strict flags."""
    os.makedirs("/tmp", exist_ok=True)
    cpp_files = list(SRC.glob("*.cpp"))
    assert len(cpp_files) > 0, f"No C++ files found in {SRC}."
    
    cmd = ["g++", "-std=c++17", "-Wall", "-Wextra", "-pedantic"] + [str(f) for f in cpp_files] + ["-o", str(BIN)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, f"Compilation failed:\n{result.stderr}"
    assert BIN.exists(), "Executable not produced."
    os.chmod(BIN, 0o755)

def run_commands(commands: str) -> list[str]:
    result = subprocess.run([str(BIN)], input=commands, capture_output=True, text=True)
    assert result.returncode == 0, f"Execution failed:\n{result.stderr}"
    return [line for line in result.stdout.splitlines() if line.strip()]

def test_add_and_lookup_artist():
    """ADD_ARTIST inserts at correct bucket; LOOKUP returns full line."""
    lines = run_commands("ADD_ARTIST|T400|Ava Park|vip|Mike Mignola|Hellboy|175\nLOOKUP|T400\n")
    assert any(l.startswith("ADDED T400 BUCKET") for l in lines)
    assert any(l == "FOUND T400 | attendee=Ava Park | pass=vip | type=Artist | celebrity=Mike Mignola | fandom=Hellboy | commission_rate=175" for l in lines)

def test_add_and_lookup_voice_actor():
    lines = run_commands("ADD_VOICE|T500|Bob Smith|standard|Tara Strong|Twilight Sparkle|SAG-AFTRA\nLOOKUP|T500\n")
    assert any(l.startswith("ADDED T500 BUCKET") for l in lines)
    assert any(l == "FOUND T500 | attendee=Bob Smith | pass=standard | type=VoiceActor | celebrity=Tara Strong | signature_role=Twilight Sparkle | union_status=SAG-AFTRA" for l in lines)

def test_add_and_lookup_singer():
    lines = run_commands("ADD_SINGER|T600|Eve|vip|Taylor Swift|Pop|10\nLOOKUP|T600\n")
    assert any(l.startswith("ADDED T600 BUCKET") for l in lines)
    assert any(l == "FOUND T600 | attendee=Eve | pass=vip | type=Singer | celebrity=Taylor Swift | genre=Pop | chart_count=10" for l in lines)

def test_add_and_lookup_live_action_actor():
    lines = run_commands("ADD_LIVE|T700|Charlie|standard|Keanu Reeves|John Wick|87Eleven\nLOOKUP|T700\n")
    assert any(l.startswith("ADDED T700 BUCKET") for l in lines)
    assert any(l == "FOUND T700 | attendee=Charlie | pass=standard | type=LiveActionActor | celebrity=Keanu Reeves | franchise=John Wick | stunt_team=87Eleven" for l in lines)

def test_remove():
    lines = run_commands("ADD_ARTIST|T400|Ava Park|vip|Mike Mignola|Hellboy|175\nREMOVE|T400\nLOOKUP|T400\n")
    assert any(l.startswith("REMOVED T400 BUCKET") for l in lines)
    assert any(l == "MISSING T400" for l in lines)

def test_errors():
    lines = run_commands("ADD_ARTIST|T400|Ava Park|vip|Mike Mignola|Hellboy|175\nADD_ARTIST|T400|Ava Park|vip|Mike Mignola|Hellboy|175\nADD_ARTIST|T401|Bob|invalid|Mike|Hellboy|175\n")
    assert any(l == "ERROR duplicate ticket T400" for l in lines)
    assert any(l == "ERROR invalid pass_type invalid" for l in lines)

def test_bucket_report():
    lines = run_commands("ADD_ARTIST|T400|Ava Park|vip|Mike Mignola|Hellboy|175\nBUCKET_REPORT\n")
    found_bucket = False
    for l in lines:
        if re.match(r"^BUCKET \d+=[0-9]+", l):
            found_bucket = True
    assert found_bucket, "BUCKET_REPORT missing output"

def test_category_report():
    lines = run_commands("ADD_ARTIST|T400|Ava Park|vip|Mike Mignola|Hellboy|175\nCATEGORY_REPORT\n")
    assert any(l.startswith("TOTAL_TICKETS=") for l in lines)
    assert any(l.startswith("VIP_TICKETS=") for l in lines)
    assert any(l.startswith("ARTIST_COUNT=") for l in lines)
    assert any(l.startswith("VOICE_ACTOR_COUNT=") for l in lines)
    assert any(l.startswith("SINGER_COUNT=") for l in lines)
    assert any(l.startswith("LIVE_ACTION_COUNT=") for l in lines)
    assert any(l.startswith("OVERALL_FAVORITE=") for l in lines)
    assert any(l.startswith("MISSING_CATEGORIES=") for l in lines)

def test_source_code_structures():
    """Verify the source code uses appropriate data structures and object-oriented practices."""
    assert SOURCE_FILE.exists(), "comicon_roster.cpp is missing."
    with SOURCE_FILE.open('r', encoding='utf-8') as f:
        src = f.read()

    assert re.search(r"class\s+Celebrity", src, re.IGNORECASE), "No base class Celebrity found"
    assert re.search(r"virtual\s+.*?(const\s*=\s*0|;|\{)", src, re.IGNORECASE), "No virtual function found in Celebrity base class"

    assert re.search(r"class\s+Artist\s*:\s*public\s+Celebrity", src, re.IGNORECASE), "Artist does not inherit from Celebrity publicly"
    assert re.search(r"class\s+VoiceActor\s*:\s*public\s+Celebrity", src, re.IGNORECASE), "VoiceActor does not inherit from Celebrity publicly"
    assert re.search(r"class\s+Singer\s*:\s*public\s+Celebrity", src, re.IGNORECASE), "Singer does not inherit from Celebrity publicly"
    assert re.search(r"class\s+LiveActionActor\s*:\s*public\s+Celebrity", src, re.IGNORECASE), "LiveActionActor does not inherit from Celebrity publicly"

    # Enforce traversal via next pointers
    assert re.search(r"TicketNode\s*\*\s*\w+\s*=.*->next", src, re.IGNORECASE), "Must traverse linked list nodes via next pointers."
    # Ban vector for bucket storage
    assert not re.search(r"vector\s*<\s*Ticket", src, re.IGNORECASE), "Ticket storage must not use std::vector."
    assert not re.search(r"vector\s*<\s*vector", src, re.IGNORECASE), "Ticket storage must not use std::vector of vectors."
    assert not re.search(r"std::map\s*<", src), "std::map usage is prohibited."
    assert not re.search(r"std::unordered_map\s*<", src), "std::unordered_map usage is prohibited."
