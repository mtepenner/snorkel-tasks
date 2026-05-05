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

const fs::path kSourcePath("/app/workspace/src/comicon_roster.cpp");
const fs::path kBinaryPath("/tmp/comicon_roster");

struct CommandResult {
    int exitCode = -1;
    std::string stdoutText;
    std::string stderrText;
};

struct TestCase {
    std::string name;
    std::function<void()> body;
};

struct RegexCapture {
    std::regex pattern;
    int groupIndex;
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

std::vector<std::string> collectMatches(const std::string& source, const std::regex& pattern, int groupIndex) {
    std::vector<std::string> matches;
    for (std::sregex_iterator it(source.begin(), source.end(), pattern), end; it != end; ++it) {
        matches.push_back((*it)[groupIndex].str());
    }
    return matches;
}

bool usesCelebrityVirtualDispatch(const std::string& source) {
    std::vector<std::string> virtualMethodNames = collectMatches(
        source,
        std::regex(R"RE(virtual\s+[^;{}()]+\s+([A-Za-z_]\w*)\s*[(])RE"),
        1
    );

    const std::vector<std::string> overrideMethods = collectMatches(
        source,
        std::regex(R"RE(([A-Za-z_]\w*)\s*[(][^;{}]*[)]\s*(const\s*)?override\b)RE"),
        1
    );
    virtualMethodNames.insert(virtualMethodNames.end(), overrideMethods.begin(), overrideMethods.end());

    std::vector<std::string> celebrityHandles;
    const std::array<RegexCapture, 6> handlePatterns = {{
        {std::regex(R"((std::)?unique_ptr\s*<\s*Celebrity\s*>\s*([A-Za-z_]\w*))"), 2},
        {std::regex(R"((std::)?shared_ptr\s*<\s*Celebrity\s*>\s*([A-Za-z_]\w*))"), 2},
        {std::regex(R"((const\s+)?Celebrity\s*\*\s*([A-Za-z_]\w*))"), 2},
        {std::regex(R"((const\s+)?Celebrity\s*&\s*([A-Za-z_]\w*))"), 2},
        {std::regex(R"((std::)?unique_ptr\s*<\s*Celebrity\s*>\s*&\s*([A-Za-z_]\w*))"), 2},
        {std::regex(R"((std::)?shared_ptr\s*<\s*Celebrity\s*>\s*&\s*([A-Za-z_]\w*))"), 2}
    }};

    for (const auto& entry : handlePatterns) {
        const std::vector<std::string> matches = collectMatches(source, entry.pattern, entry.groupIndex);
        celebrityHandles.insert(celebrityHandles.end(), matches.begin(), matches.end());
    };

    for (const std::string& handle : celebrityHandles) {
        for (const std::string& methodName : virtualMethodNames) {
            const std::regex arrowCall("\\b" + handle + R"RE(\s*->\s*)RE" + methodName + R"RE(\s*[(])RE");
            const std::regex dotCall("\\b" + handle + R"RE(\s*\.\s*)RE" + methodName + R"RE(\s*[(])RE");
            const std::regex derefCall(R"RE([(]\s*\*\s*)RE" + handle + R"RE(\s*[)]\s*\.\s*)RE" + methodName + R"RE(\s*[(])RE");

            if (std::regex_search(source, arrowCall) || std::regex_search(source, dotCall) || std::regex_search(source, derefCall)) {
                return true;
            }
        }
    }

    return false;
}

int bucketFor(const std::string& ticketId) {
    int total = 0;
    for (unsigned char character : ticketId) {
        total += character;
    }
    return total % 7;
}

std::vector<std::string> collisionIds(int targetBucket, int count) {
    std::vector<std::string> matches;
    int candidate = 100;
    while (static_cast<int>(matches.size()) < count) {
        const std::string ticketId = "T" + std::to_string(candidate);
        if (bucketFor(ticketId) == targetBucket) {
            matches.push_back(ticketId);
        }
        ++candidate;
    }
    return matches;
}

void compileCandidate() {
    expectTrue(fs::exists(kSourcePath), "Missing required source file: " + kSourcePath.string());

    const CommandResult compileResult = runShellCommand(
        "g++ -std=c++17 -Wall -Wextra -pedantic /app/workspace/src/*.cpp -o /tmp/comicon_roster",
        "linear_compile"
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
    const fs::path inputPath = fs::temp_directory_path() / "linear_commands.txt";
    const fs::path stdoutPath = fs::temp_directory_path() / "linear_program_stdout.txt";
    const fs::path stderrPath = fs::temp_directory_path() / "linear_program_stderr.txt";

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

void testSourceUsesLinkedListsAndVirtualDispatch() {
    const std::string source = readFile(kSourcePath);
    expectRegex(source, R"(class\s+Celebrity\b)", "Must define a Celebrity base class.");
    expectRegex(source, R"(class\s+Artist\s*:\s*public\s+Celebrity)", "Must define Artist inheriting from Celebrity.");
    expectRegex(source, R"(class\s+VoiceActor\s*:\s*public\s+Celebrity)", "Must define VoiceActor inheriting from Celebrity.");
    expectRegex(source, R"(class\s+Singer\s*:\s*public\s+Celebrity)", "Must define Singer inheriting from Celebrity.");
    expectRegex(source, R"(class\s+LiveActionActor\s*:\s*public\s+Celebrity)", "Must define LiveActionActor inheriting from Celebrity.");
    expectRegex(source, R"(virtual\b)", "Celebrity must declare at least one virtual method.");
    expectTrue(
        usesCelebrityVirtualDispatch(source),
        "Source must use virtual dispatch when formatting LOOKUP output."
    );
    expectNotRegex(source, R"(std\s*::\s*(unordered_)?map\b)", "Ticket store must not use std::map or std::unordered_map.");
    expectNotRegex(source, R"(std\s*::\s*vector\s*<[^;]+>\s*buckets_?)", "Ticket buckets must not be implemented with std::vector.");
}

void testAddLookupAndBucketCollisions() {
    const int targetBucket = 3;
    const std::vector<std::string> ids = collisionIds(targetBucket, 3);
    const std::string& ticketOne = ids[0];
    const std::string& ticketTwo = ids[1];
    const std::string& ticketThree = ids[2];

    const std::vector<std::string> lines = runProgram(
        "# collide three tickets into the same linked list bucket\n"
        "ADD_ARTIST|" + ticketOne + "|Ava Park|vip|Mike Mignola|Hellboy|175\n"
        "ADD_VOICE|" + ticketTwo + "|Ben Ortiz|standard|Ashley Johnson|Ellie|union\n"
        "ADD_LIVE|" + ticketThree + "|Cara Moss|vip|Pedro Pascal|The Last of Us|yes\n"
        "LOOKUP|" + ticketTwo + "\n"
        "BUCKET_REPORT\n"
    );

    expectEqual(lines[0], "ADDED " + ticketOne + " BUCKET " + std::to_string(targetBucket), "First collision add should target the expected bucket.");
    expectEqual(lines[1], "ADDED " + ticketTwo + " BUCKET " + std::to_string(targetBucket), "Second collision add should target the expected bucket.");
    expectEqual(lines[2], "ADDED " + ticketThree + " BUCKET " + std::to_string(targetBucket), "Third collision add should target the expected bucket.");
    expectEqual(
        lines[3],
        "FOUND " + ticketTwo + " | attendee=Ben Ortiz | pass=standard | type=VoiceActor | celebrity=Ashley Johnson | signature_role=Ellie | union_status=union",
        "LOOKUP should return the stored VoiceActor details."
    );

    expectEqual(static_cast<int>(lines.size()), 11, "Expected add, lookup, and exactly seven bucket lines.");

    std::array<int, 7> counts{};
    const std::regex bucketLine(R"(^BUCKET (\d)=(\d+)$)");
    for (std::size_t index = 4; index < lines.size(); ++index) {
        std::smatch match;
        expectTrue(std::regex_match(lines[index], match, bucketLine), "Unexpected bucket line: " + lines[index]);
        counts[static_cast<std::size_t>(std::stoi(match[1]))] = std::stoi(match[2]);
    }

    int total = 0;
    for (int count : counts) {
        total += count;
    }
    expectEqual(total, 3, "Bucket counts should sum to the three inserted tickets.");
    expectEqual(counts[static_cast<std::size_t>(targetBucket)], 3, "All three tickets should land in the collision bucket.");
}

void testLookupReportsTypeSpecificDetailsForEachCelebrityType() {
    const std::vector<std::string> lines = runProgram(
        "ADD_ARTIST|T400|Ava Park|vip|Mike Mignola|Hellboy|175\n"
        "ADD_VOICE|T401|Ben Ortiz|standard|Ashley Johnson|Ellie|union\n"
        "ADD_SINGER|T402|Cara Moss|vip|Aurora|pop|12\n"
        "ADD_LIVE|T403|Drew Lane|standard|Pedro Pascal|The Last of Us|yes\n"
        "LOOKUP|T400\n"
        "LOOKUP|T401\n"
        "LOOKUP|T402\n"
        "LOOKUP|T403\n"
    );

    expectLinesEqual(
        std::vector<std::string>(lines.begin(), lines.begin() + 4),
        {
            "ADDED T400 BUCKET " + std::to_string(bucketFor("T400")),
            "ADDED T401 BUCKET " + std::to_string(bucketFor("T401")),
            "ADDED T402 BUCKET " + std::to_string(bucketFor("T402")),
            "ADDED T403 BUCKET " + std::to_string(bucketFor("T403")),
        },
        "Each add should report its computed bucket."
    );

    expectLinesEqual(
        std::vector<std::string>(lines.begin() + 4, lines.end()),
        {
            "FOUND T400 | attendee=Ava Park | pass=vip | type=Artist | celebrity=Mike Mignola | fandom=Hellboy | commission_rate=175",
            "FOUND T401 | attendee=Ben Ortiz | pass=standard | type=VoiceActor | celebrity=Ashley Johnson | signature_role=Ellie | union_status=union",
            "FOUND T402 | attendee=Cara Moss | pass=vip | type=Singer | celebrity=Aurora | genre=pop | chart_count=12",
            "FOUND T403 | attendee=Drew Lane | pass=standard | type=LiveActionActor | celebrity=Pedro Pascal | franchise=The Last of Us | stunt_team=yes",
        },
        "LOOKUP must format subtype-specific celebrity details exactly."
    );
}

void testRemoveDuplicateAndInvalidPass() {
    const int targetBucket = 5;
    const std::vector<std::string> ids = collisionIds(targetBucket, 2);
    const std::string& ticketOne = ids[0];
    const std::string& ticketTwo = ids[1];

    const std::vector<std::string> lines = runProgram(
        "ADD_SINGER|" + ticketOne + "|Drew Lane|vip|Aurora|pop|12\n"
        "ADD_ARTIST|" + ticketOne + "|Drew Lane|standard|Jen Bartel|Marvel|220\n"
        "ADD_VOICE|" + ticketTwo + "|Mira Cole|backstage|Laura Bailey|Vex|union\n"
        "REMOVE|" + ticketOne + "\n"
        "LOOKUP|" + ticketOne + "\n"
        "BUCKET_REPORT\n"
    );

    expectEqual(lines[0], "ADDED " + ticketOne + " BUCKET " + std::to_string(targetBucket), "Initial insert should succeed in the collision bucket.");
    expectEqual(lines[1], "ERROR duplicate ticket " + ticketOne, "Duplicate IDs must be rejected.");
    expectEqual(lines[2], "ERROR invalid pass_type backstage", "Invalid pass types must be rejected.");
    expectEqual(lines[3], "REMOVED " + ticketOne + " BUCKET " + std::to_string(targetBucket), "Removing the stored ticket should report the same bucket.");
    expectEqual(lines[4], "MISSING " + ticketOne, "Removed tickets should no longer be found.");

    std::array<int, 7> counts{};
    const std::regex bucketLine(R"(^BUCKET (\d)=(\d+)$)");
    for (std::size_t index = 5; index < lines.size(); ++index) {
        std::smatch match;
        expectTrue(std::regex_match(lines[index], match, bucketLine), "Unexpected bucket line: " + lines[index]);
        counts[static_cast<std::size_t>(std::stoi(match[1]))] = std::stoi(match[2]);
    }

    int total = 0;
    for (int count : counts) {
        total += count;
    }
    expectEqual(total, 0, "After removal, every bucket should be empty.");
}

void testRemoveMissingTicketReturnsMissing() {
    expectLinesEqual(
        runProgram("REMOVE|T999\n"),
        {"MISSING T999"},
        "Removing a missing ticket should report MISSING."
    );
}

void testCategoryReportWithFullRoster() {
    const std::vector<std::string> lines = runProgram(
        "ADD_ARTIST|T200|Ava Park|vip|Mike Mignola|Hellboy|175\n"
        "ADD_ARTIST|T201|Ben Ortiz|standard|Mike Mignola|Hellboy|200\n"
        "ADD_SINGER|T202|Cara Moss|vip|Aurora|pop|12\n"
        "ADD_VOICE|T203|Drew Lane|standard|Ashley Johnson|Ellie|union\n"
        "ADD_LIVE|T204|Elle Hart|vip|Pedro Pascal|The Last of Us|yes\n"
        "CATEGORY_REPORT\n"
    );

    expectLinesEqual(
        std::vector<std::string>(lines.end() - 8, lines.end()),
        {
            "TOTAL_TICKETS=5",
            "VIP_TICKETS=3",
            "ARTIST_COUNT=2 FAVORITE=Mike Mignola",
            "VOICE_ACTOR_COUNT=1 FAVORITE=Ashley Johnson",
            "SINGER_COUNT=1 FAVORITE=Aurora",
            "LIVE_ACTION_COUNT=1 FAVORITE=Pedro Pascal",
            "OVERALL_FAVORITE=Mike Mignola",
            "MISSING_CATEGORIES=NONE",
        },
        "CATEGORY_REPORT should summarize a complete roster exactly."
    );
}

void testCategoryReportHandlesTiesAndMissingCategories() {
    const std::vector<std::string> lines = runProgram(
        "ADD_SINGER|T300|Noah Price|vip|Zola|soul|3\n"
        "ADD_SINGER|T301|Piper Webb|standard|Aurora|pop|12\n"
        "CATEGORY_REPORT\n"
    );

    expectLinesEqual(
        std::vector<std::string>(lines.end() - 8, lines.end()),
        {
            "TOTAL_TICKETS=2",
            "VIP_TICKETS=1",
            "ARTIST_COUNT=0 FAVORITE=NONE",
            "VOICE_ACTOR_COUNT=0 FAVORITE=NONE",
            "SINGER_COUNT=2 FAVORITE=Aurora",
            "LIVE_ACTION_COUNT=0 FAVORITE=NONE",
            "OVERALL_FAVORITE=Aurora",
            "MISSING_CATEGORIES=Artist,VoiceActor,LiveActionActor",
        },
        "CATEGORY_REPORT must break ties alphabetically and list missing categories in the required order."
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
        {"source_uses_linked_lists_and_virtual_dispatch", testSourceUsesLinkedListsAndVirtualDispatch},
        {"add_lookup_and_bucket_collisions", testAddLookupAndBucketCollisions},
        {"lookup_reports_type_specific_details", testLookupReportsTypeSpecificDetailsForEachCelebrityType},
        {"remove_duplicate_and_invalid_pass", testRemoveDuplicateAndInvalidPass},
        {"remove_missing_ticket_returns_missing", testRemoveMissingTicketReturnsMissing},
        {"category_report_with_full_roster", testCategoryReportWithFullRoster},
        {"category_report_handles_ties_and_missing_categories", testCategoryReportHandlesTiesAndMissingCategories},
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