#include <array>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <functional>
#include <iostream>
#include <regex>
#include <sstream>
#include <stdexcept>
#include <string>
#include <sys/wait.h>
#include <vector>

namespace {

namespace fs = std::filesystem;

const fs::path kSourcePath("/app/workspace/src/travel_groups.cpp");
const fs::path kBinaryPath("/tmp/travel_groups");

struct CommandResult {
    int exitCode = -1;
    std::string stdoutText;
    std::string stderrText;
};

struct TestCase {
    std::string name;
    std::function<void()> body;
};

[[noreturn]] void fail(const std::string& message) {
    throw std::runtime_error(message);
}

std::string trim(const std::string& value) {
    const std::string whitespace = " \t\r\n";
    const std::size_t start = value.find_first_not_of(whitespace);
    if (start == std::string::npos) {
        return "";
    }

    const std::size_t end = value.find_last_not_of(whitespace);
    return value.substr(start, end - start + 1);
}

std::string readFile(const fs::path& path) {
    std::ifstream input(path);
    if (!input) {
        fail("Unable to read file: " + path.string());
    }

    std::ostringstream content;
    content << input.rdbuf();
    return content.str();
}

void writeFile(const fs::path& path, const std::string& content) {
    std::ofstream output(path);
    if (!output) {
        fail("Unable to write file: " + path.string());
    }

    output << content;
}

std::string quotePath(const fs::path& path) {
    return "'" + path.string() + "'";
}

int normalizeExitCode(int status) {
    if (status == -1) {
        return -1;
    }

    if (WIFEXITED(status)) {
        return WEXITSTATUS(status);
    }

    if (WIFSIGNALED(status)) {
        return 128 + WTERMSIG(status);
    }

    return status;
}

CommandResult runShellCommand(const std::string& command, const std::string& label) {
    const fs::path stdoutPath = fs::temp_directory_path() / (label + "_stdout.txt");
    const fs::path stderrPath = fs::temp_directory_path() / (label + "_stderr.txt");
    const std::string wrapped = command + " >" + quotePath(stdoutPath) + " 2>" + quotePath(stderrPath);

    const int status = std::system(wrapped.c_str());
    return {normalizeExitCode(status), readFile(stdoutPath), readFile(stderrPath)};
}

std::vector<std::string> nonEmptyLines(const std::string& text) {
    std::vector<std::string> lines;
    std::istringstream stream(text);
    std::string line;
    while (std::getline(stream, line)) {
        if (!trim(line).empty()) {
            lines.push_back(line);
        }
    }
    return lines;
}

std::string debugLines(const std::vector<std::string>& lines) {
    std::ostringstream output;
    for (std::size_t index = 0; index < lines.size(); ++index) {
        output << "[" << index << "] " << lines[index];
        if (index + 1 < lines.size()) {
            output << '\n';
        }
    }
    return output.str();
}

void expectTrue(bool condition, const std::string& message) {
    if (!condition) {
        fail(message);
    }
}

void expectEqual(const std::string& actual, const std::string& expected, const std::string& message) {
    if (actual != expected) {
        fail(message + "\nExpected: " + expected + "\nActual:   " + actual);
    }
}

void expectEqual(int actual, int expected, const std::string& message) {
    if (actual != expected) {
        fail(message + "\nExpected: " + std::to_string(expected) + "\nActual:   " + std::to_string(actual));
    }
}

void expectLinesEqual(const std::vector<std::string>& actual, const std::vector<std::string>& expected, const std::string& message) {
    if (actual != expected) {
        fail(message + "\nExpected lines:\n" + debugLines(expected) + "\nActual lines:\n" + debugLines(actual));
    }
}

void expectRegex(const std::string& text, const std::string& pattern, const std::string& message) {
    if (!std::regex_search(text, std::regex(pattern))) {
        fail(message + "\nMissing pattern: " + pattern);
    }
}

void expectNotRegex(const std::string& text, const std::string& pattern, const std::string& message) {
    if (std::regex_search(text, std::regex(pattern))) {
        fail(message + "\nUnexpected pattern: " + pattern);
    }
}

void compileCandidate() {
    expectTrue(fs::exists(kSourcePath), "Missing required source file: " + kSourcePath.string());

    const CommandResult compileResult = runShellCommand(
        "g++ -std=c++17 -Wall -Wextra -pedantic /app/workspace/src/*.cpp -o /tmp/travel_groups",
        "circular_compile"
    );

    if (compileResult.exitCode != 0) {
        fail(
            "Compilation failed:\nSTDOUT:\n" + compileResult.stdoutText +
            "\nSTDERR:\n" + compileResult.stderrText
        );
    }

    expectTrue(
        trim(compileResult.stdoutText).empty() && trim(compileResult.stderrText).empty(),
        "Compilation emitted output. The task requires a warning-free build with:\n"
        "g++ -std=c++17 -Wall -Wextra -pedantic\n"
        "STDOUT:\n" + compileResult.stdoutText + "\nSTDERR:\n" + compileResult.stderrText
    );
}

std::vector<std::string> runProgram(const std::string& commands) {
    const fs::path inputPath = fs::temp_directory_path() / "circular_commands.txt";
    const fs::path stdoutPath = fs::temp_directory_path() / "circular_program_stdout.txt";
    const fs::path stderrPath = fs::temp_directory_path() / "circular_program_stderr.txt";

    writeFile(inputPath, commands);

    const std::string command = quotePath(kBinaryPath) + " <" + quotePath(inputPath) + " >" + quotePath(stdoutPath) + " 2>" + quotePath(stderrPath);
    const int status = std::system(command.c_str());
    const int exitCode = normalizeExitCode(status);
    const std::string stdoutText = readFile(stdoutPath);
    const std::string stderrText = readFile(stderrPath);

    expectEqual(
        exitCode,
        0,
        "Program exited non-zero.\nSTDOUT:\n" + stdoutText + "\nSTDERR:\n" + stderrText
    );

    return nonEmptyLines(stdoutText);
}

void testSourceUsesActualCircularListStructure() {
    const std::string source = readFile(kSourcePath);

    expectRegex(source, R"((Node|ItineraryNode)\s*\*\s*next)", "Need a next pointer for the circular linked list.");
    expectTrue(
        source.find("GROUP_COUNT = 3") != std::string::npos || source.find("GROUP_COUNT=3") != std::string::npos ||
            std::regex_search(source, std::regex(R"(\[\s*3\s*\])")),
        "Need an array of exactly three circular linked lists."
    );
    expectTrue(source.find("scotland") != std::string::npos, "Source must define the scotland slot.");
    expectTrue(source.find("hamburg") != std::string::npos, "Source must define the hamburg slot.");
    expectTrue(source.find("moscow") != std::string::npos, "Source must define the moscow slot.");
    expectRegex(source, R"(next\s*=\s*.*head|node->next\s*=\s*node|tail->next)", "Source should show circular next-pointer wiring.");
    expectNotRegex(source, R"(\bunordered_map\b|\bstd::map\b|\bmap\s*<)", "The task forbids std::map and std::unordered_map.");
    expectNotRegex(source, R"(std\s*::\s*vector\s*<[^;]+>\s*groups_?)", "The group ring must not be implemented with std::vector.");
}

void testBookingShowAndWrappedAdvance() {
    const std::vector<std::string> lines = runProgram(
        "BOOK|B100|Amelia Stone|scotland|5|flight\n"
        "BOOK|B101|Ben Kline|scotland|7|train\n"
        "BOOK|B102|Carla Mendez|scotland|4|ferry\n"
        "SHOW|B101\n"
        "ADVANCE|scotland|5\n"
        "GROUP_REPORT\n"
    );

    expectLinesEqual(
        lines,
        {
            "BOOKED B100 GROUP scotland",
            "BOOKED B101 GROUP scotland",
            "BOOKED B102 GROUP scotland",
            "FOUND B101 | traveler=Ben Kline | group=scotland | nights=7 | transport=train",
            "CURRENT scotland B102 Carla Mendez",
            "GROUP scotland=3 CURRENT=B102",
            "GROUP hamburg=0 CURRENT=EMPTY",
            "GROUP moscow=0 CURRENT=EMPTY",
        },
        "BOOK, SHOW, ADVANCE, and GROUP_REPORT should follow the documented wraparound behavior."
    );
}

void testCancelDuplicateAndInvalidInputPaths() {
    const std::vector<std::string> lines = runProgram(
        "BOOK|B200|Derek Hale|hamburg|3|train\n"
        "BOOK|B200|Eva Long|hamburg|4|flight\n"
        "BOOK|B201|Finn Ortega|berlin|2|train\n"
        "BOOK|B202|Gia Moss|moscow|0|ferry\n"
        "BOOK|B203|Hiro Tan|moscow|4|boat\n"
        "CANCEL|B200\n"
        "SHOW|B200\n"
        "ADVANCE|hamburg|2\n"
    );

    expectLinesEqual(
        lines,
        {
            "BOOKED B200 GROUP hamburg",
            "ERROR duplicate booking B200",
            "ERROR invalid group berlin",
            "ERROR invalid nights 0",
            "ERROR invalid transport boat",
            "CANCELLED B200 GROUP hamburg",
            "MISSING B200",
            "EMPTY hamburg",
        },
        "Invalid inputs and cancellations must match the exact error contract."
    );
}

void testTransportReportUsesAlphabeticalTiebreaks() {
    const std::vector<std::string> lines = runProgram(
        "BOOK|B300|Iris Vale|scotland|4|train\n"
        "BOOK|B301|Jon Park|scotland|6|flight\n"
        "BOOK|B302|Kira Moss|hamburg|2|ferry\n"
        "BOOK|B303|Luca Shaw|hamburg|3|ferry\n"
        "BOOK|B304|Mina Cole|moscow|5|train\n"
        "BOOK|B305|Nico Hart|moscow|5|flight\n"
        "TRANSPORT_REPORT\n"
    );

    expectLinesEqual(
        std::vector<std::string>(lines.end() - 5, lines.end()),
        {
            "TOTAL_BOOKINGS=6",
            "SCOTLAND_FAVORITE_TRANSPORT=flight",
            "HAMBURG_FAVORITE_TRANSPORT=ferry",
            "MOSCOW_FAVORITE_TRANSPORT=flight",
            "OVERALL_FAVORITE_TRANSPORT=ferry",
        },
        "TRANSPORT_REPORT should break favorite-transport ties alphabetically."
    );
}

void testRemovalPreservesRingAndCurrentPointer() {
    const std::vector<std::string> lines = runProgram(
        "BOOK|B400|Owen Pike|moscow|8|flight\n"
        "BOOK|B401|Pia Reed|moscow|3|train\n"
        "BOOK|B402|Quinn Frost|moscow|6|train\n"
        "ADVANCE|moscow|1\n"
        "CANCEL|B401\n"
        "ADVANCE|moscow|3\n"
        "GROUP_REPORT\n"
        "TRANSPORT_REPORT\n"
    );

    expectEqual(lines[3], "CURRENT moscow B401 Pia Reed", "The first advance should move current to B401.");
    expectEqual(lines[4], "CANCELLED B401 GROUP moscow", "Cancelling the current booking should succeed.");
    expectEqual(lines[5], "CURRENT moscow B402 Quinn Frost", "After removing current, the ring should still advance from the preserved current pointer.");
    expectLinesEqual(
        std::vector<std::string>(lines.begin() + 6, lines.begin() + 9),
        {
            "GROUP scotland=0 CURRENT=EMPTY",
            "GROUP hamburg=0 CURRENT=EMPTY",
            "GROUP moscow=2 CURRENT=B402",
        },
        "GROUP_REPORT should reflect the remaining ring and current pointer."
    );
    expectLinesEqual(
        std::vector<std::string>(lines.end() - 5, lines.end()),
        {
            "TOTAL_BOOKINGS=2",
            "SCOTLAND_FAVORITE_TRANSPORT=NONE",
            "HAMBURG_FAVORITE_TRANSPORT=NONE",
            "MOSCOW_FAVORITE_TRANSPORT=flight",
            "OVERALL_FAVORITE_TRANSPORT=flight",
        },
        "TRANSPORT_REPORT should reflect the two remaining bookings after cancellation."
    );
}

} // namespace

int main() {
    try {
        compileCandidate();
    } catch (const std::exception& error) {
        std::cerr << "[FAIL] compile_candidate\n" << error.what() << '\n';
        return 1;
    }

    const std::vector<TestCase> tests = {
        {"source_uses_actual_circular_list_structure", testSourceUsesActualCircularListStructure},
        {"booking_show_and_wrapped_advance", testBookingShowAndWrappedAdvance},
        {"cancel_duplicate_and_invalid_input_paths", testCancelDuplicateAndInvalidInputPaths},
        {"transport_report_uses_alphabetical_tiebreaks", testTransportReportUsesAlphabeticalTiebreaks},
        {"removal_preserves_ring_and_current_pointer", testRemovalPreservesRingAndCurrentPointer},
    };

    int failed = 0;
    for (const TestCase& test : tests) {
        try {
            test.body();
            std::cout << "[PASS] " << test.name << '\n';
        } catch (const std::exception& error) {
            ++failed;
            std::cerr << "[FAIL] " << test.name << '\n' << error.what() << '\n';
        }
    }

    std::cout << (tests.size() - static_cast<std::size_t>(failed)) << "/" << tests.size() << " verifier checks passed.\n";
    return failed == 0 ? 0 : 1;
}