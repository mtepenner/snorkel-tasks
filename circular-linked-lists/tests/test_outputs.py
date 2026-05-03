import re
import subprocess
import unittest
from pathlib import Path


SOURCE_PATH = Path("/app/workspace/src/travel_groups.cpp")
BINARY_PATH = Path("/tmp/travel_groups")


class CircularLinkedListTaskTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        assert SOURCE_PATH.exists(), f"Missing required source file: {SOURCE_PATH}"
        compile_result = subprocess.run(
            [
                "bash",
                "-lc",
                "g++ -std=c++17 -Wall -Wextra -pedantic /app/workspace/src/*.cpp -o /tmp/travel_groups",
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

    def test_source_uses_actual_circular_list_structure(self) -> None:
        source = SOURCE_PATH.read_text(encoding="utf-8")

        self.assertRegex(source, r"(Node|ItineraryNode)\s*\*\s*next", "Need a next pointer for the circular linked list.")
        self.assertTrue(
            "GROUP_COUNT = 3" in source or re.search(r"\[\s*3\s*\]", source),
            "Need an array of exactly three circular linked lists.",
        )
        self.assertIn("scotland", source.lower())
        self.assertIn("hamburg", source.lower())
        self.assertIn("moscow", source.lower())
        self.assertRegex(source, r"next\s*=\s*.*head|node->next\s*=\s*node|tail->next", "Source should show circular next-pointer wiring.")
        self.assertIsNone(re.search(r"\bunordered_map\b|\bstd::map\b|\bmap\s*<", source))

    def test_booking_show_and_wrapped_advance(self) -> None:
        lines = self.run_program(
            "\n".join(
                [
                    "BOOK|B100|Amelia Stone|scotland|5|flight",
                    "BOOK|B101|Ben Kline|scotland|7|train",
                    "BOOK|B102|Carla Mendez|scotland|4|ferry",
                    "SHOW|B101",
                    "ADVANCE|scotland|5",
                    "GROUP_REPORT",
                ]
            )
            + "\n"
        )

        self.assertEqual(lines[0], "BOOKED B100 GROUP scotland")
        self.assertEqual(lines[1], "BOOKED B101 GROUP scotland")
        self.assertEqual(lines[2], "BOOKED B102 GROUP scotland")
        self.assertEqual(lines[3], "FOUND B101 | traveler=Ben Kline | group=scotland | nights=7 | transport=train")
        self.assertEqual(lines[4], "CURRENT scotland B102 Carla Mendez")
        self.assertEqual(lines[5:], [
            "GROUP scotland=3 CURRENT=B102",
            "GROUP hamburg=0 CURRENT=EMPTY",
            "GROUP moscow=0 CURRENT=EMPTY",
        ])

    def test_cancel_duplicate_and_invalid_input_paths(self) -> None:
        lines = self.run_program(
            "\n".join(
                [
                    "BOOK|B200|Derek Hale|hamburg|3|train",
                    "BOOK|B200|Eva Long|hamburg|4|flight",
                    "BOOK|B201|Finn Ortega|berlin|2|train",
                    "BOOK|B202|Gia Moss|moscow|0|ferry",
                    "BOOK|B203|Hiro Tan|moscow|4|boat",
                    "CANCEL|B200",
                    "SHOW|B200",
                    "ADVANCE|hamburg|2",
                ]
            )
            + "\n"
        )

        self.assertEqual(lines[0], "BOOKED B200 GROUP hamburg")
        self.assertEqual(lines[1], "ERROR duplicate booking B200")
        self.assertEqual(lines[2], "ERROR invalid group berlin")
        self.assertEqual(lines[3], "ERROR invalid nights 0")
        self.assertEqual(lines[4], "ERROR invalid transport boat")
        self.assertEqual(lines[5], "CANCELLED B200 GROUP hamburg")
        self.assertEqual(lines[6], "MISSING B200")
        self.assertEqual(lines[7], "EMPTY hamburg")

    def test_transport_report_uses_alphabetical_tiebreaks(self) -> None:
        lines = self.run_program(
            "\n".join(
                [
                    "BOOK|B300|Iris Vale|scotland|4|train",
                    "BOOK|B301|Jon Park|scotland|6|flight",
                    "BOOK|B302|Kira Moss|hamburg|2|ferry",
                    "BOOK|B303|Luca Shaw|hamburg|3|ferry",
                    "BOOK|B304|Mina Cole|moscow|5|train",
                    "BOOK|B305|Nico Hart|moscow|5|flight",
                    "TRANSPORT_REPORT",
                ]
            )
            + "\n"
        )

        self.assertEqual(lines[-5:], [
            "TOTAL_BOOKINGS=6",
            "SCOTLAND_FAVORITE_TRANSPORT=flight",
            "HAMBURG_FAVORITE_TRANSPORT=ferry",
            "MOSCOW_FAVORITE_TRANSPORT=flight",
            "OVERALL_FAVORITE_TRANSPORT=ferry",
        ])

    def test_removal_preserves_ring_and_current_pointer(self) -> None:
        lines = self.run_program(
            "\n".join(
                [
                    "BOOK|B400|Owen Pike|moscow|8|flight",
                    "BOOK|B401|Pia Reed|moscow|3|train",
                    "BOOK|B402|Quinn Frost|moscow|6|train",
                    "ADVANCE|moscow|1",
                    "CANCEL|B401",
                    "ADVANCE|moscow|3",
                    "GROUP_REPORT",
                    "TRANSPORT_REPORT",
                ]
            )
            + "\n"
        )

        self.assertEqual(lines[3], "CURRENT moscow B401 Pia Reed")
        self.assertEqual(lines[4], "CANCELLED B401 GROUP moscow")
        self.assertEqual(lines[5], "CURRENT moscow B402 Quinn Frost")
        self.assertEqual(lines[6:9], [
            "GROUP scotland=0 CURRENT=EMPTY",
            "GROUP hamburg=0 CURRENT=EMPTY",
            "GROUP moscow=2 CURRENT=B402",
        ])
        self.assertEqual(lines[9:], [
            "TOTAL_BOOKINGS=2",
            "SCOTLAND_FAVORITE_TRANSPORT=NONE",
            "HAMBURG_FAVORITE_TRANSPORT=NONE",
            "MOSCOW_FAVORITE_TRANSPORT=flight",
            "OVERALL_FAVORITE_TRANSPORT=flight",
        ])


if __name__ == "__main__":
    unittest.main(verbosity=2)
