#include <algorithm>
#include <arpa/inet.h>
#include <cmath>
#include <csignal>
#include <cctype>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <map>
#include <netinet/in.h>
#include <sstream>
#include <stdexcept>
#include <string>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>
#include <utility>
#include <vector>

namespace {

constexpr int kPort = 8000;
const std::string kIndexPath = "/app/workspace/src/templates/index.html";
const std::string kStaticJsPath = "/app/workspace/src/static/js/app.js";

std::string trim(const std::string& input) {
    std::size_t start = 0;
    while (start < input.size() && std::isspace(static_cast<unsigned char>(input[start]))) {
        ++start;
    }

    std::size_t end = input.size();
    while (end > start && std::isspace(static_cast<unsigned char>(input[end - 1]))) {
        --end;
    }

    return input.substr(start, end - start);
}

std::string toLower(std::string value) {
    std::transform(value.begin(), value.end(), value.begin(), [](unsigned char character) {
        return static_cast<char>(std::tolower(character));
    });
    return value;
}

bool startsWith(const std::string& value, const std::string& prefix) {
    return value.rfind(prefix, 0) == 0;
}

bool parseDoubleStrict(const std::string& input, double& result) {
    if (input.empty()) {
        return false;
    }

    char* end = nullptr;
    const double parsed = std::strtod(input.c_str(), &end);
    if (end == input.c_str() || end == nullptr) {
        return false;
    }

    while (*end != '\0') {
        if (!std::isspace(static_cast<unsigned char>(*end))) {
            return false;
        }
        ++end;
    }

    result = parsed;
    return true;
}

std::string sanitizeToken(const std::string& token) {
    std::string sanitized;
    sanitized.reserve(token.size());
    for (unsigned char character : token) {
        if (std::isalnum(character)) {
            sanitized.push_back(static_cast<char>(std::tolower(character)));
        } else {
            sanitized.push_back('_');
        }
    }
    return sanitized;
}

struct JsonValue {
    enum class Type {
        Null,
        Boolean,
        Number,
        String,
        Array,
        Object,
    };

    Type type = Type::Null;
    bool bool_value = false;
    double number_value = 0.0;
    std::string string_value;
    std::vector<JsonValue> array_value;
    std::map<std::string, JsonValue> object_value;

    static JsonValue null() {
        return JsonValue{};
    }

    static JsonValue boolean(bool value) {
        JsonValue json;
        json.type = Type::Boolean;
        json.bool_value = value;
        return json;
    }

    static JsonValue number(double value) {
        JsonValue json;
        json.type = Type::Number;
        json.number_value = value;
        return json;
    }

    static JsonValue string(const std::string& value) {
        JsonValue json;
        json.type = Type::String;
        json.string_value = value;
        return json;
    }

    static JsonValue array(const std::vector<JsonValue>& value) {
        JsonValue json;
        json.type = Type::Array;
        json.array_value = value;
        return json;
    }

    static JsonValue object(const std::map<std::string, JsonValue>& value) {
        JsonValue json;
        json.type = Type::Object;
        json.object_value = value;
        return json;
    }
};

class JsonParser {
public:
    explicit JsonParser(const std::string& source) : source_(source) {}

    JsonValue parse() {
        skipWhitespace();
        JsonValue value = parseValue();
        skipWhitespace();
        if (position_ != source_.size()) {
            throw std::runtime_error("Unexpected trailing JSON content");
        }
        return value;
    }

private:
    const std::string& source_;
    std::size_t position_ = 0;

    void skipWhitespace() {
        while (position_ < source_.size() && std::isspace(static_cast<unsigned char>(source_[position_]))) {
            ++position_;
        }
    }

    char peek() const {
        if (position_ >= source_.size()) {
            throw std::runtime_error("Unexpected end of JSON input");
        }
        return source_[position_];
    }

    char consume() {
        const char character = peek();
        ++position_;
        return character;
    }

    void expect(char expected) {
        const char actual = consume();
        if (actual != expected) {
            throw std::runtime_error("Malformed JSON input");
        }
    }

    JsonValue parseValue() {
        skipWhitespace();
        switch (peek()) {
            case 'n':
                return parseNull();
            case 't':
            case 'f':
                return parseBoolean();
            case '"':
                return JsonValue::string(parseStringLiteral());
            case '[':
                return parseArray();
            case '{':
                return parseObject();
            default:
                return parseNumber();
        }
    }

    JsonValue parseNull() {
        if (source_.compare(position_, 4, "null") != 0) {
            throw std::runtime_error("Malformed JSON input");
        }
        position_ += 4;
        return JsonValue::null();
    }

    JsonValue parseBoolean() {
        if (source_.compare(position_, 4, "true") == 0) {
            position_ += 4;
            return JsonValue::boolean(true);
        }
        if (source_.compare(position_, 5, "false") == 0) {
            position_ += 5;
            return JsonValue::boolean(false);
        }
        throw std::runtime_error("Malformed JSON input");
    }

    std::string parseStringLiteral() {
        expect('"');
        std::string value;
        while (position_ < source_.size()) {
            const char character = consume();
            if (character == '"') {
                return value;
            }
            if (character == '\\') {
                if (position_ >= source_.size()) {
                    throw std::runtime_error("Malformed JSON string");
                }
                const char escaped = consume();
                switch (escaped) {
                    case '"':
                    case '\\':
                    case '/':
                        value.push_back(escaped);
                        break;
                    case 'b':
                        value.push_back('\b');
                        break;
                    case 'f':
                        value.push_back('\f');
                        break;
                    case 'n':
                        value.push_back('\n');
                        break;
                    case 'r':
                        value.push_back('\r');
                        break;
                    case 't':
                        value.push_back('\t');
                        break;
                    case 'u':
                        if (position_ + 4 > source_.size()) {
                            throw std::runtime_error("Malformed JSON unicode escape");
                        }
                        value.push_back('?');
                        position_ += 4;
                        break;
                    default:
                        throw std::runtime_error("Malformed JSON escape sequence");
                }
                continue;
            }
            value.push_back(character);
        }
        throw std::runtime_error("Unterminated JSON string");
    }

    JsonValue parseNumber() {
        const std::size_t start = position_;
        if (source_[position_] == '-') {
            ++position_;
        }

        if (position_ >= source_.size()) {
            throw std::runtime_error("Malformed JSON number");
        }

        if (source_[position_] == '0') {
            ++position_;
        } else if (std::isdigit(static_cast<unsigned char>(source_[position_]))) {
            while (position_ < source_.size() && std::isdigit(static_cast<unsigned char>(source_[position_]))) {
                ++position_;
            }
        } else {
            throw std::runtime_error("Malformed JSON number");
        }

        if (position_ < source_.size() && source_[position_] == '.') {
            ++position_;
            if (position_ >= source_.size() || !std::isdigit(static_cast<unsigned char>(source_[position_]))) {
                throw std::runtime_error("Malformed JSON number");
            }
            while (position_ < source_.size() && std::isdigit(static_cast<unsigned char>(source_[position_]))) {
                ++position_;
            }
        }

        if (position_ < source_.size() && (source_[position_] == 'e' || source_[position_] == 'E')) {
            ++position_;
            if (position_ < source_.size() && (source_[position_] == '+' || source_[position_] == '-')) {
                ++position_;
            }
            if (position_ >= source_.size() || !std::isdigit(static_cast<unsigned char>(source_[position_]))) {
                throw std::runtime_error("Malformed JSON number");
            }
            while (position_ < source_.size() && std::isdigit(static_cast<unsigned char>(source_[position_]))) {
                ++position_;
            }
        }

        return JsonValue::number(std::stod(source_.substr(start, position_ - start)));
    }

    JsonValue parseArray() {
        expect('[');
        skipWhitespace();
        std::vector<JsonValue> items;
        if (peek() == ']') {
            consume();
            return JsonValue::array(items);
        }

        while (true) {
            items.push_back(parseValue());
            skipWhitespace();
            const char separator = consume();
            if (separator == ']') {
                break;
            }
            if (separator != ',') {
                throw std::runtime_error("Malformed JSON array");
            }
            skipWhitespace();
        }
        return JsonValue::array(items);
    }

    JsonValue parseObject() {
        expect('{');
        skipWhitespace();
        std::map<std::string, JsonValue> items;
        if (peek() == '}') {
            consume();
            return JsonValue::object(items);
        }

        while (true) {
            skipWhitespace();
            if (peek() != '"') {
                throw std::runtime_error("JSON object keys must be strings");
            }
            const std::string key = parseStringLiteral();
            skipWhitespace();
            expect(':');
            skipWhitespace();
            items[key] = parseValue();
            skipWhitespace();
            const char separator = consume();
            if (separator == '}') {
                break;
            }
            if (separator != ',') {
                throw std::runtime_error("Malformed JSON object");
            }
        }

        return JsonValue::object(items);
    }
};

std::string jsonEscape(const std::string& input) {
    std::ostringstream escaped;
    for (unsigned char character : input) {
        switch (character) {
            case '\\':
                escaped << "\\\\";
                break;
            case '"':
                escaped << "\\\"";
                break;
            case '\b':
                escaped << "\\b";
                break;
            case '\f':
                escaped << "\\f";
                break;
            case '\n':
                escaped << "\\n";
                break;
            case '\r':
                escaped << "\\r";
                break;
            case '\t':
                escaped << "\\t";
                break;
            default:
                if (character < 0x20) {
                    escaped << "\\u" << std::hex << std::setw(4) << std::setfill('0')
                            << static_cast<int>(character) << std::dec;
                } else {
                    escaped << static_cast<char>(character);
                }
                break;
        }
    }
    return escaped.str();
}

std::string numberToJson(double value) {
    if (!std::isfinite(value)) {
        return "0";
    }

    std::ostringstream stream;
    stream << std::setprecision(15) << value;
    std::string output = stream.str();
    if (output.find('.') != std::string::npos) {
        while (!output.empty() && output.back() == '0') {
            output.pop_back();
        }
        if (!output.empty() && output.back() == '.') {
            output.pop_back();
        }
    }
    if (output == "-0") {
        output = "0";
    }
    return output.empty() ? "0" : output;
}

std::string jsonStringify(const JsonValue& value) {
    switch (value.type) {
        case JsonValue::Type::Null:
            return "null";
        case JsonValue::Type::Boolean:
            return value.bool_value ? "true" : "false";
        case JsonValue::Type::Number:
            return numberToJson(value.number_value);
        case JsonValue::Type::String:
            return "\"" + jsonEscape(value.string_value) + "\"";
        case JsonValue::Type::Array: {
            std::ostringstream array_stream;
            array_stream << '[';
            for (std::size_t index = 0; index < value.array_value.size(); ++index) {
                if (index > 0) {
                    array_stream << ',';
                }
                array_stream << jsonStringify(value.array_value[index]);
            }
            array_stream << ']';
            return array_stream.str();
        }
        case JsonValue::Type::Object: {
            std::ostringstream object_stream;
            object_stream << '{';
            bool first = true;
            for (const auto& [key, child] : value.object_value) {
                if (!first) {
                    object_stream << ',';
                }
                first = false;
                object_stream << '"' << jsonEscape(key) << '"' << ':' << jsonStringify(child);
            }
            object_stream << '}';
            return object_stream.str();
        }
    }
    return "null";
}

struct RawCell {
    enum class Type {
        Missing,
        Number,
        Text,
    };

    Type type = Type::Missing;
    double number_value = 0.0;
    std::string text_value;

    static RawCell missing() {
        return RawCell{};
    }

    static RawCell number(double value) {
        RawCell cell;
        cell.type = Type::Number;
        cell.number_value = value;
        return cell;
    }

    static RawCell text(const std::string& value) {
        RawCell cell;
        cell.type = Type::Text;
        cell.text_value = value;
        return cell;
    }
};

using RawRow = std::map<std::string, RawCell>;

std::vector<std::vector<std::string>> parseCsvRows(const std::string& payload) {
    std::vector<std::vector<std::string>> rows;
    std::vector<std::string> current_row;
    std::string current_cell;
    bool in_quotes = false;

    for (std::size_t index = 0; index < payload.size(); ++index) {
        const char character = payload[index];
        if (character == '"') {
            if (in_quotes && index + 1 < payload.size() && payload[index + 1] == '"') {
                current_cell.push_back('"');
                ++index;
            } else {
                in_quotes = !in_quotes;
            }
            continue;
        }

        if (!in_quotes && character == ',') {
            current_row.push_back(current_cell);
            current_cell.clear();
            continue;
        }

        if (!in_quotes && (character == '\n' || character == '\r')) {
            if (character == '\r' && index + 1 < payload.size() && payload[index + 1] == '\n') {
                ++index;
            }
            current_row.push_back(current_cell);
            current_cell.clear();
            if (!(current_row.size() == 1 && trim(current_row[0]).empty())) {
                rows.push_back(current_row);
            }
            current_row.clear();
            continue;
        }

        current_cell.push_back(character);
    }

    current_row.push_back(current_cell);
    if (!(current_row.size() == 1 && trim(current_row[0]).empty())) {
        rows.push_back(current_row);
    }

    return rows;
}

bool looksLikeHeaderlessCsv(const std::string& payload) {
    const auto rows = parseCsvRows(payload);
    if (rows.size() < 2 || rows[0].size() != rows[1].size()) {
        return false;
    }

    auto numericOrEmpty = [](const std::string& cell) {
        const std::string stripped = trim(cell);
        if (stripped.empty()) {
            return true;
        }
        double parsed = 0.0;
        return parseDoubleStrict(stripped, parsed);
    };

    auto numericOnly = [](const std::string& cell) {
        const std::string stripped = trim(cell);
        if (stripped.empty()) {
            return false;
        }
        double parsed = 0.0;
        return parseDoubleStrict(stripped, parsed);
    };

    return std::all_of(rows[0].begin(), rows[0].end(), numericOnly) &&
           std::all_of(rows[1].begin(), rows[1].end(), numericOrEmpty);
}

RawCell makeCellFromString(const std::string& raw_value) {
    const std::string stripped = trim(raw_value);
    if (stripped.empty()) {
        return RawCell::missing();
    }
    double number = 0.0;
    if (parseDoubleStrict(stripped, number)) {
        return RawCell::number(number);
    }
    return RawCell::text(stripped);
}

std::vector<RawRow> parseJsonPayload(const std::string& payload, std::vector<std::string>& columns) {
    const JsonValue root = JsonParser(payload).parse();
    if (root.type != JsonValue::Type::Array || root.array_value.empty()) {
        throw std::runtime_error("JSON body must be a non-empty array of records");
    }

    std::vector<RawRow> rows;
    for (const JsonValue& record : root.array_value) {
        if (record.type != JsonValue::Type::Object) {
            throw std::runtime_error("Each JSON record must be an object");
        }

        RawRow row;
        for (const auto& [key, value] : record.object_value) {
            if (std::find(columns.begin(), columns.end(), key) == columns.end()) {
                columns.push_back(key);
            }

            switch (value.type) {
                case JsonValue::Type::Null:
                    row[key] = RawCell::missing();
                    break;
                case JsonValue::Type::Number:
                    row[key] = RawCell::number(value.number_value);
                    break;
                case JsonValue::Type::String:
                    row[key] = value.string_value.empty() ? RawCell::missing() : RawCell::text(value.string_value);
                    break;
                case JsonValue::Type::Boolean:
                    row[key] = RawCell::text(value.bool_value ? "true" : "false");
                    break;
                default:
                    throw std::runtime_error("JSON records must contain only primitive values");
            }
        }
        rows.push_back(row);
    }

    if (columns.empty()) {
        throw std::runtime_error("JSON body must contain at least one column");
    }

    return rows;
}

std::vector<RawRow> parseCsvPayload(const std::string& payload, std::vector<std::string>& columns) {
    if (looksLikeHeaderlessCsv(payload)) {
        throw std::runtime_error("CSV input must include a header row");
    }

    const auto rows = parseCsvRows(payload);
    if (rows.size() <= 1) {
        throw std::runtime_error("CSV input must include a header row and at least one data row");
    }

    columns.clear();
    for (const std::string& header : rows.front()) {
        const std::string stripped = trim(header);
        if (stripped.empty()) {
            throw std::runtime_error("CSV header cells must be non-empty");
        }
        columns.push_back(stripped);
    }

    std::vector<RawRow> parsed_rows;
    for (std::size_t row_index = 1; row_index < rows.size(); ++row_index) {
        if (rows[row_index].size() != columns.size()) {
            throw std::runtime_error("CSV rows must have the same number of fields as the header");
        }

        RawRow row;
        for (std::size_t column_index = 0; column_index < columns.size(); ++column_index) {
            row[columns[column_index]] = makeCellFromString(rows[row_index][column_index]);
        }
        parsed_rows.push_back(row);
    }

    if (parsed_rows.empty()) {
        throw std::runtime_error("CSV input must include at least one record");
    }

    return parsed_rows;
}

JsonValue preprocessRows(const std::vector<RawRow>& rows, const std::vector<std::string>& columns) {
    std::vector<std::string> numeric_columns;
    std::vector<std::string> categorical_columns;

    for (const std::string& column : columns) {
        bool numeric = true;
        for (const RawRow& row : rows) {
            const auto iterator = row.find(column);
            if (iterator == row.end() || iterator->second.type == RawCell::Type::Missing) {
                continue;
            }
            if (iterator->second.type != RawCell::Type::Number) {
                numeric = false;
                break;
            }
        }
        if (numeric) {
            numeric_columns.push_back(column);
        } else {
            categorical_columns.push_back(column);
        }
    }

    struct NumericColumnStats {
        double mean = 0.0;
        double stddev = 0.0;
        std::vector<double> values;
    };

    std::map<std::string, NumericColumnStats> numeric_stats;
    for (const std::string& column : numeric_columns) {
        double sum = 0.0;
        std::size_t count = 0;
        for (const RawRow& row : rows) {
            const auto iterator = row.find(column);
            if (iterator != row.end() && iterator->second.type == RawCell::Type::Number) {
                sum += iterator->second.number_value;
                ++count;
            }
        }

        NumericColumnStats stats;
        stats.mean = count > 0 ? (sum / static_cast<double>(count)) : 0.0;
        stats.values.reserve(rows.size());
        for (const RawRow& row : rows) {
            const auto iterator = row.find(column);
            if (iterator != row.end() && iterator->second.type == RawCell::Type::Number) {
                stats.values.push_back(iterator->second.number_value);
            } else {
                stats.values.push_back(stats.mean);
            }
        }

        double variance = 0.0;
        for (double value : stats.values) {
            const double delta = value - stats.mean;
            variance += delta * delta;
        }
        variance = stats.values.empty() ? 0.0 : variance / static_cast<double>(stats.values.size());
        stats.stddev = std::sqrt(variance);
        if (stats.stddev < 1e-12) {
            stats.stddev = 0.0;
        }
        numeric_stats[column] = stats;
    }

    std::map<std::string, std::vector<std::string>> category_values;
    std::map<std::string, std::map<std::string, std::string>> category_column_names;
    for (const std::string& column : categorical_columns) {
        std::map<std::string, bool> seen;
        for (const RawRow& row : rows) {
            const auto iterator = row.find(column);
            if (iterator == row.end() || iterator->second.type != RawCell::Type::Text) {
                continue;
            }
            const std::string& value = iterator->second.text_value;
            if (!seen[value]) {
                seen[value] = true;
                category_values[column].push_back(value);
                category_column_names[column][value] = column + "_" + sanitizeToken(value);
            }
        }
    }

    std::vector<JsonValue> processed_rows;
    processed_rows.reserve(rows.size());
    for (std::size_t row_index = 0; row_index < rows.size(); ++row_index) {
        std::map<std::string, JsonValue> processed_row;
        for (const std::string& column : numeric_columns) {
            const NumericColumnStats& stats = numeric_stats[column];
            const double value = stats.values[row_index];
            const double scaled = stats.stddev == 0.0 ? 0.0 : (value - stats.mean) / stats.stddev;
            processed_row[column] = JsonValue::number(scaled);
        }

        for (const std::string& column : categorical_columns) {
            std::string current_value;
            const auto iterator = rows[row_index].find(column);
            if (iterator != rows[row_index].end() && iterator->second.type == RawCell::Type::Text) {
                current_value = iterator->second.text_value;
            }

            for (const std::string& value : category_values[column]) {
                const std::string& indicator_name = category_column_names[column][value];
                processed_row[indicator_name] = JsonValue::number(current_value == value ? 1.0 : 0.0);
            }
        }

        processed_rows.push_back(JsonValue::object(processed_row));
    }

    return JsonValue::array(processed_rows);
}

struct DatasetState {
    bool available = false;
    JsonValue processed_rows = JsonValue::array({});
};

DatasetState g_dataset;

struct HttpRequest {
    std::string method;
    std::string path;
    std::string body;
    std::map<std::string, std::string> headers;
};

struct HttpResponse {
    int status = 200;
    std::string content_type = "application/json";
    std::string body;
};

std::string readFile(const std::string& path) {
    std::ifstream stream(path, std::ios::binary);
    if (!stream) {
        return {};
    }
    std::ostringstream content;
    content << stream.rdbuf();
    return content.str();
}

HttpResponse makeJsonResponse(int status, const std::map<std::string, JsonValue>& payload) {
    HttpResponse response;
    response.status = status;
    response.content_type = "application/json";
    response.body = jsonStringify(JsonValue::object(payload));
    return response;
}

HttpResponse handleUpload(const HttpRequest& request) {
    const auto header_iterator = request.headers.find("content-type");
    const std::string content_type = header_iterator == request.headers.end() ? "" : toLower(trim(header_iterator->second));

    if (trim(request.body).empty()) {
        return makeJsonResponse(400, {{"error", JsonValue::string("Upload body must not be empty")}});
    }

    try {
        std::vector<std::string> columns;
        std::vector<RawRow> rows;
        if (startsWith(content_type, "application/json")) {
            rows = parseJsonPayload(request.body, columns);
        } else if (startsWith(content_type, "text/csv")) {
            rows = parseCsvPayload(request.body, columns);
        } else {
            return makeJsonResponse(415, {{"error", JsonValue::string("Unsupported media type")}});
        }

        g_dataset.processed_rows = preprocessRows(rows, columns);
        g_dataset.available = true;
        return makeJsonResponse(200, {
            {"message", JsonValue::string("Data processed successfully")},
            {"rows", JsonValue::number(static_cast<double>(rows.size()))}
        });
    } catch (const std::exception& error) {
        return makeJsonResponse(400, {{"error", JsonValue::string(error.what())}});
    }
}

HttpResponse handleProcessed() {
    if (!g_dataset.available) {
        return makeJsonResponse(404, {{"error", JsonValue::string("No processed data available yet")}});
    }

    HttpResponse response;
    response.status = 200;
    response.content_type = "application/json";
    response.body = jsonStringify(g_dataset.processed_rows);
    return response;
}

HttpResponse handlePredict(const HttpRequest& request) {
    try {
        const JsonValue body = JsonParser(request.body).parse();
        if (body.type != JsonValue::Type::Object) {
            throw std::runtime_error("Prediction payload must be an object");
        }

        const auto features_iterator = body.object_value.find("features");
        if (features_iterator == body.object_value.end() || features_iterator->second.type != JsonValue::Type::Array) {
            throw std::runtime_error("Prediction payload must include a features array");
        }

        double prediction = 0.0;
        for (std::size_t index = 0; index < features_iterator->second.array_value.size(); ++index) {
            const JsonValue& feature = features_iterator->second.array_value[index];
            if (feature.type != JsonValue::Type::Number) {
                throw std::runtime_error("features entries must be numeric");
            }
            prediction += static_cast<double>(index + 1) * feature.number_value;
        }

        return makeJsonResponse(200, {{"prediction", JsonValue::number(prediction)}});
    } catch (const std::exception& error) {
        return makeJsonResponse(400, {{"error", JsonValue::string(error.what())}});
    }
}

HttpResponse serveStaticFile(const std::string& path, const std::string& content_type) {
    const std::string content = readFile(path);
    if (content.empty()) {
        return makeJsonResponse(404, {{"error", JsonValue::string("File not found")}});
    }

    HttpResponse response;
    response.status = 200;
    response.content_type = content_type;
    response.body = content;
    return response;
}

HttpResponse routeRequest(const HttpRequest& request) {
    const std::string path = request.path;

    if (request.method == "GET" && path == "/") {
        return serveStaticFile(kIndexPath, "text/html; charset=utf-8");
    }
    if (request.method == "GET" && path == "/static/js/app.js") {
        return serveStaticFile(kStaticJsPath, "application/javascript; charset=utf-8");
    }
    if (path == "/api/v1/data/upload") {
        if (request.method != "POST") {
            return makeJsonResponse(405, {{"error", JsonValue::string("Method not allowed")}});
        }
        return handleUpload(request);
    }
    if (path == "/api/v1/data/processed") {
        if (request.method != "GET") {
            return makeJsonResponse(405, {{"error", JsonValue::string("Method not allowed")}});
        }
        return handleProcessed();
    }
    if (path == "/api/v1/predict") {
        if (request.method != "POST") {
            return makeJsonResponse(405, {{"error", JsonValue::string("Method not allowed")}});
        }
        return handlePredict(request);
    }

    return makeJsonResponse(404, {{"error", JsonValue::string("Not found")}});
}

std::string statusText(int status) {
    switch (status) {
        case 200:
            return "OK";
        case 400:
            return "Bad Request";
        case 404:
            return "Not Found";
        case 405:
            return "Method Not Allowed";
        case 415:
            return "Unsupported Media Type";
        default:
            return "Internal Server Error";
    }
}

std::size_t contentLengthFromHeaderBlock(const std::string& header_block) {
    std::istringstream stream(header_block);
    std::string line;
    std::getline(stream, line);
    while (std::getline(stream, line)) {
        if (!line.empty() && line.back() == '\r') {
            line.pop_back();
        }
        const std::size_t separator = line.find(':');
        if (separator == std::string::npos) {
            continue;
        }
        const std::string key = toLower(trim(line.substr(0, separator)));
        const std::string value = trim(line.substr(separator + 1));
        if (key == "content-length") {
            return static_cast<std::size_t>(std::stoul(value));
        }
    }
    return 0;
}

bool receiveRequest(int client_fd, HttpRequest& request) {
    std::string raw_request;
    std::size_t expected_size = 0;
    bool headers_complete = false;

    while (true) {
        char buffer[4096];
        const ssize_t bytes_read = recv(client_fd, buffer, sizeof(buffer), 0);
        if (bytes_read <= 0) {
            break;
        }
        raw_request.append(buffer, static_cast<std::size_t>(bytes_read));

        if (!headers_complete) {
            const std::size_t header_end = raw_request.find("\r\n\r\n");
            if (header_end != std::string::npos) {
                headers_complete = true;
                expected_size = header_end + 4 + contentLengthFromHeaderBlock(raw_request.substr(0, header_end + 2));
                if (raw_request.size() >= expected_size) {
                    break;
                }
            }
        } else if (raw_request.size() >= expected_size) {
            break;
        }
    }

    if (raw_request.empty()) {
        return false;
    }

    const std::size_t header_end = raw_request.find("\r\n\r\n");
    if (header_end == std::string::npos) {
        return false;
    }

    const std::string header_block = raw_request.substr(0, header_end);
    const std::string body = raw_request.substr(header_end + 4);
    if (body.size() < contentLengthFromHeaderBlock(header_block + "\r\n")) {
        return false;
    }

    std::istringstream stream(header_block);
    std::string request_line;
    if (!std::getline(stream, request_line)) {
        return false;
    }
    if (!request_line.empty() && request_line.back() == '\r') {
        request_line.pop_back();
    }

    std::istringstream request_line_stream(request_line);
    std::string version;
    request_line_stream >> request.method >> request.path >> version;
    if (request.method.empty() || request.path.empty()) {
        return false;
    }

    const std::size_t query_separator = request.path.find('?');
    if (query_separator != std::string::npos) {
        request.path = request.path.substr(0, query_separator);
    }

    std::string line;
    while (std::getline(stream, line)) {
        if (!line.empty() && line.back() == '\r') {
            line.pop_back();
        }
        const std::size_t separator = line.find(':');
        if (separator == std::string::npos) {
            continue;
        }
        request.headers[toLower(trim(line.substr(0, separator)))] = trim(line.substr(separator + 1));
    }

    request.body = body;
    return true;
}

void sendResponse(int client_fd, const HttpResponse& response) {
    std::ostringstream stream;
    stream << "HTTP/1.1 " << response.status << ' ' << statusText(response.status) << "\r\n";
    stream << "Content-Type: " << response.content_type << "\r\n";
    stream << "Content-Length: " << response.body.size() << "\r\n";
    stream << "Connection: close\r\n\r\n";
    stream << response.body;

    const std::string payload = stream.str();
    std::size_t offset = 0;
    while (offset < payload.size()) {
        const ssize_t bytes_sent = send(client_fd, payload.data() + offset, payload.size() - offset, 0);
        if (bytes_sent <= 0) {
            break;
        }
        offset += static_cast<std::size_t>(bytes_sent);
    }
}

}  // namespace

int main() {
    std::signal(SIGPIPE, SIG_IGN);

    const int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) {
        return 1;
    }

    int enable_reuse = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &enable_reuse, sizeof(enable_reuse));

    sockaddr_in address{};
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = htonl(INADDR_ANY);
    address.sin_port = htons(kPort);

    if (bind(server_fd, reinterpret_cast<sockaddr*>(&address), sizeof(address)) < 0) {
        close(server_fd);
        return 1;
    }

    if (listen(server_fd, 16) < 0) {
        close(server_fd);
        return 1;
    }

    while (true) {
        sockaddr_in client_address{};
        socklen_t client_length = sizeof(client_address);
        const int client_fd = accept(server_fd, reinterpret_cast<sockaddr*>(&client_address), &client_length);
        if (client_fd < 0) {
            continue;
        }

        HttpRequest request;
        if (receiveRequest(client_fd, request)) {
            const HttpResponse response = routeRequest(request);
            sendResponse(client_fd, response);
        }
        close(client_fd);
    }

    close(server_fd);
    return 0;
}