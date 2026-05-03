import re
import subprocess
import unittest
from pathlib import Path


SOURCE_PATH = Path("/app/workspace/src/comicon_roster.cpp")
BINARY_PATH = Path("/tmp/comicon_roster")


def bucket_for(ticket_id: str) -> int:
    return sum(ord(character) for character in ticket_id) % 7


def collision_ids(target_bucket: int, count: int) -> list[str]:
    matches = []
    candidate = 100
    while len(matches) < count:
        ticket_id = f"T{candidate}"
        if bucket_for(ticket_id) == target_bucket:
            matches.append(ticket_id)
        candidate += 1
    return matches


class LinearLinkedListTaskTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        assert SOURCE_PATH.exists(), f"Missing required source file: {SOURCE_PATH}"
        compile_result = subprocess.run(
            [
                "bash",
                "-lc",
                "g++ -std=c++17 -Wall -Wextra -pedantic /app/workspace/src/*.cpp -o /tmp/comicon_roster",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        assert compile_result.returncode == 0, (
            "Compilation failed:\n"
            f"STDOUT:\n{compile_result.stdout}\n"
            f"STDERR:\n{compile_result.stderr}"
        )

    def run_program(self, commands: str) -> list[str]:
        process = subprocess.run(
            [str(BINARY_PATH)],
            input=commands,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(
            process.returncode,
            0,
            msg=(
                "Program exited non-zero.\n"
                f"STDOUT:\n{process.stdout}\n"
                f"STDERR:\n{process.stderr}"
            ),
        )
        return [line for line in process.stdout.splitlines() if line.strip()]

    def test_source_uses_linked_list_and_polymorphism(self) -> None:
        source = SOURCE_PATH.read_text(encoding="utf-8")

        self.assertIn("class Celebrity", source)
        self.assertIn("class Artist", source)
        self.assertIn("class VoiceActor", source)
        self.assertIn("class Singer", source)
        self.assertIn("class LiveActionActor", source)
        self.assertIn("virtual", source, "Need at least one virtual method in the hierarchy.")
        self.assertRegex(source, r"(Node|TicketNode)\s*\*\s*next", "Need a next pointer for the linear linked list.")
        self.assertTrue(
            "BUCKET_COUNT = 7" in source or re.search(r"\[\s*7\s*\]", source),
            "Need a 7-bucket array for the ticket database.",
        )
        self.assertIsNone(re.search(r"\bunordered_map\b|\bstd::map\b|\bmap\s*<", source))

    def test_add_lookup_and_bucket_collisions(self) -> None:
        target_bucket = 3
        ticket_one, ticket_two, ticket_three = collision_ids(target_bucket, 3)

        lines = self.run_program(
            "\n".join(
                [
                    "# collide three tickets into the same linked list bucket",
                    f"ADD_ARTIST|{ticket_one}|Ava Park|vip|Mike Mignola|Hellboy|175",
                    f"ADD_VOICE|{ticket_two}|Ben Ortiz|standard|Ashley Johnson|Ellie|union",
                    f"ADD_LIVE|{ticket_three}|Cara Moss|vip|Pedro Pascal|The Last of Us|yes",
                    f"LOOKUP|{ticket_two}",
                    "BUCKET_REPORT",
                ]
            )
            + "\n"
        )

        self.assertEqual(lines[0], f"ADDED {ticket_one} BUCKET {target_bucket}")
        self.assertEqual(lines[1], f"ADDED {ticket_two} BUCKET {target_bucket}")
        self.assertEqual(lines[2], f"ADDED {ticket_three} BUCKET {target_bucket}")
        self.assertEqual(
            lines[3],
            f"FOUND {ticket_two} | attendee=Ben Ortiz | pass=standard | type=VoiceActor | celebrity=Ashley Johnson | signature_role=Ellie | union_status=union",
        )

        bucket_lines = lines[4:]
        self.assertEqual(len(bucket_lines), 7)
        counts = {}
        for line in bucket_lines:
            match = re.fullmatch(r"BUCKET (\d)=(\d+)", line)
            self.assertIsNotNone(match, f"Unexpected bucket line: {line}")
            counts[int(match.group(1))] = int(match.group(2))
        self.assertEqual(sum(counts.values()), 3)
        self.assertEqual(counts[target_bucket], 3)

    def test_remove_duplicate_and_invalid_pass(self) -> None:
        target_bucket = 5
        ticket_one, ticket_two = collision_ids(target_bucket, 2)

        lines = self.run_program(
            "\n".join(
                [
                    f"ADD_SINGER|{ticket_one}|Drew Lane|vip|Aurora|pop|12",
                    f"ADD_ARTIST|{ticket_one}|Drew Lane|standard|Jen Bartel|Marvel|220",
                    f"ADD_VOICE|{ticket_two}|Mira Cole|backstage|Laura Bailey|Vex|union",
                    f"REMOVE|{ticket_one}",
                    f"LOOKUP|{ticket_one}",
                    "BUCKET_REPORT",
                ]
            )
            + "\n"
        )

        self.assertEqual(lines[0], f"ADDED {ticket_one} BUCKET {target_bucket}")
        self.assertEqual(lines[1], f"ERROR duplicate ticket {ticket_one}")
        self.assertEqual(lines[2], "ERROR invalid pass_type backstage")
        self.assertEqual(lines[3], f"REMOVED {ticket_one} BUCKET {target_bucket}")
        self.assertEqual(lines[4], f"MISSING {ticket_one}")

        bucket_lines = lines[5:]
        counts = {}
        for line in bucket_lines:
            match = re.fullmatch(r"BUCKET (\d)=(\d+)", line)
            self.assertIsNotNone(match)
            counts[int(match.group(1))] = int(match.group(2))
        self.assertEqual(sum(counts.values()), 0)

    def test_category_report_with_full_roster(self) -> None:
        lines = self.run_program(
            "\n".join(
                [
                    "ADD_ARTIST|T200|Ava Park|vip|Mike Mignola|Hellboy|175",
                    "ADD_ARTIST|T201|Ben Ortiz|standard|Mike Mignola|Hellboy|200",
                    "ADD_SINGER|T202|Cara Moss|vip|Aurora|pop|12",
                    "ADD_VOICE|T203|Drew Lane|standard|Ashley Johnson|Ellie|union",
                    "ADD_LIVE|T204|Elle Hart|vip|Pedro Pascal|The Last of Us|yes",
                    "CATEGORY_REPORT",
                ]
            )
            + "\n"
        )

        self.assertEqual(lines[-8:], [
            "TOTAL_TICKETS=5",
            "VIP_TICKETS=3",
            "ARTIST_COUNT=2 FAVORITE=Mike Mignola",
            "VOICE_ACTOR_COUNT=1 FAVORITE=Ashley Johnson",
            "SINGER_COUNT=1 FAVORITE=Aurora",
            "LIVE_ACTION_COUNT=1 FAVORITE=Pedro Pascal",
            "OVERALL_FAVORITE=Mike Mignola",
            "MISSING_CATEGORIES=NONE",
        ])

    def test_category_report_handles_ties_and_missing_categories(self) -> None:
        lines = self.run_program(
            "\n".join(
                [
                    "ADD_SINGER|T300|Noah Price|vip|Zola|soul|3",
                    "ADD_SINGER|T301|Piper Webb|standard|Aurora|pop|12",
                    "CATEGORY_REPORT",
                ]
            )
            + "\n"
        )

        self.assertEqual(lines[-8:], [
            "TOTAL_TICKETS=2",
            "VIP_TICKETS=1",
            "ARTIST_COUNT=0 FAVORITE=NONE",
            "VOICE_ACTOR_COUNT=0 FAVORITE=NONE",
            "SINGER_COUNT=2 FAVORITE=Aurora",
            "LIVE_ACTION_COUNT=0 FAVORITE=NONE",
            "OVERALL_FAVORITE=Aurora",
            "MISSING_CATEGORIES=Artist,VoiceActor,LiveActionActor",
        ])


if __name__ == "__main__":
    unittest.main(verbosity=2)
