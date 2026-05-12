#include <algorithm>
#include <array>
#include <cctype>
#include <iostream>
#include <memory>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

namespace {

std::string trim(const std::string& value) {
    std::size_t start = 0;
    while (start < value.size() && std::isspace(static_cast<unsigned char>(value[start]))) {
        ++start;
    }

    std::size_t end = value.size();
    while (end > start && std::isspace(static_cast<unsigned char>(value[end - 1]))) {
        --end;
    }

    return value.substr(start, end - start);
}

std::vector<std::string> split(const std::string& line, char delimiter) {
    std::vector<std::string> pieces;
    std::string current;
    std::istringstream stream(line);
    while (std::getline(stream, current, delimiter)) {
        pieces.push_back(trim(current));
    }
    if (!line.empty() && line.back() == delimiter) {
        pieces.emplace_back();
    }
    return pieces;
}

std::string toLower(std::string value) {
    std::transform(value.begin(), value.end(), value.begin(), [](unsigned char character) {
        return static_cast<char>(std::tolower(character));
    });
    return value;
}

bool parseInteger(const std::string& value, int& parsed) {
    try {
        std::size_t consumed = 0;
        int candidate = std::stoi(value, &consumed);
        if (consumed != value.size()) {
            return false;
        }
        parsed = candidate;
        return true;
    } catch (...) {
        return false;
    }
}

class Celebrity {
public:
    explicit Celebrity(std::string name) : name_(std::move(name)) {}
    virtual ~Celebrity() = default;

    const std::string& name() const {
        return name_;
    }

    virtual std::string typeLabel() const = 0;
    virtual std::string detailSummary() const = 0;

private:
    std::string name_;
};

class Artist : public Celebrity {
public:
    Artist(std::string name, std::string fandom, int commissionRate)
        : Celebrity(std::move(name)), fandom_(std::move(fandom)), commissionRate_(commissionRate) {}

    std::string typeLabel() const override {
        return "Artist";
    }

    std::string detailSummary() const override {
        std::ostringstream output;
        output << "fandom=" << fandom_ << " | commission_rate=" << commissionRate_;
        return output.str();
    }

private:
    std::string fandom_;
    int commissionRate_;
};

class VoiceActor : public Celebrity {
public:
    VoiceActor(std::string name, std::string signatureRole, std::string unionStatus)
        : Celebrity(std::move(name)), signatureRole_(std::move(signatureRole)), unionStatus_(std::move(unionStatus)) {}

    std::string typeLabel() const override {
        return "VoiceActor";
    }

    std::string detailSummary() const override {
        return "signature_role=" + signatureRole_ + " | union_status=" + unionStatus_;
    }

private:
    std::string signatureRole_;
    std::string unionStatus_;
};

class Singer : public Celebrity {
public:
    Singer(std::string name, std::string genre, int chartCount)
        : Celebrity(std::move(name)), genre_(std::move(genre)), chartCount_(chartCount) {}

    std::string typeLabel() const override {
        return "Singer";
    }

    std::string detailSummary() const override {
        std::ostringstream output;
        output << "genre=" << genre_ << " | chart_count=" << chartCount_;
        return output.str();
    }

private:
    std::string genre_;
    int chartCount_;
};

class LiveActionActor : public Celebrity {
public:
    LiveActionActor(std::string name, std::string franchise, std::string stuntTeam)
        : Celebrity(std::move(name)), franchise_(std::move(franchise)), stuntTeam_(std::move(stuntTeam)) {}

    std::string typeLabel() const override {
        return "LiveActionActor";
    }

    std::string detailSummary() const override {
        return "franchise=" + franchise_ + " | stunt_team=" + stuntTeam_;
    }

private:
    std::string franchise_;
    std::string stuntTeam_;
};

struct Ticket {
    std::string ticketId;
    std::string attendeeName;
    std::string passType;
    std::unique_ptr<Celebrity> celebrity;

    std::string lookupSummary() const {
        std::ostringstream output;
        output << "FOUND " << ticketId
               << " | attendee=" << attendeeName
               << " | pass=" << passType
               << " | type=" << celebrity->typeLabel()
               << " | celebrity=" << celebrity->name()
               << " | " << celebrity->detailSummary();
        return output.str();
    }
};

struct TicketNode {
    Ticket ticket;
    TicketNode* next;

    TicketNode(Ticket value, TicketNode* nextNode = nullptr)
        : ticket(std::move(value)), next(nextNode) {}
};

struct CategorySummary {
    int totalTickets = 0;
    int vipTickets = 0;
    int artistCount = 0;
    int voiceActorCount = 0;
    int singerCount = 0;
    int liveActionCount = 0;
    std::string artistFavorite = "NONE";
    std::string voiceActorFavorite = "NONE";
    std::string singerFavorite = "NONE";
    std::string liveActionFavorite = "NONE";
    std::string overallFavorite = "NONE";
    std::string missingCategories = "NONE";
};

void bumpNameCount(std::vector<std::pair<std::string, int>>& counts, const std::string& name) {
    for (auto& entry : counts) {
        if (entry.first == name) {
            ++entry.second;
            return;
        }
    }
    counts.emplace_back(name, 1);
}

std::string pickFavorite(const std::vector<std::pair<std::string, int>>& counts) {
    if (counts.empty()) {
        return "NONE";
    }

    std::string favorite = counts.front().first;
    int bestCount = counts.front().second;

    for (const auto& entry : counts) {
        if (entry.second > bestCount || (entry.second == bestCount && entry.first < favorite)) {
            favorite = entry.first;
            bestCount = entry.second;
        }
    }

    return favorite;
}

class TicketDatabase {
public:
    static constexpr std::size_t BUCKET_COUNT = 7;

    TicketDatabase() {
        buckets_.fill(nullptr);
    }

    ~TicketDatabase() {
        clear();
    }

    std::size_t hashTicket(const std::string& ticketId) const {
        unsigned int total = 0;
        for (unsigned char character : ticketId) {
            total += character;
        }
        return total % BUCKET_COUNT;
    }

    std::string addTicket(Ticket ticket) {
        const std::size_t bucket = hashTicket(ticket.ticketId);
        if (findNode(ticket.ticketId) != nullptr) {
            return "ERROR duplicate ticket " + ticket.ticketId;
        }

        if (ticket.passType == "vip") {
            ++vipTickets_;
        }

        buckets_[bucket] = new TicketNode(std::move(ticket), buckets_[bucket]);
        ++ticketCount_;

        std::ostringstream output;
        output << "ADDED " << buckets_[bucket]->ticket.ticketId << " BUCKET " << bucket;
        return output.str();
    }

    const Ticket* findTicket(const std::string& ticketId) const {
        TicketNode* match = findNode(ticketId);
        return match == nullptr ? nullptr : &match->ticket;
    }

    std::string removeTicket(const std::string& ticketId) {
        const std::size_t bucket = hashTicket(ticketId);
        TicketNode* current = buckets_[bucket];
        TicketNode* previous = nullptr;

        while (current != nullptr) {
            if (current->ticket.ticketId == ticketId) {
                if (previous == nullptr) {
                    buckets_[bucket] = current->next;
                } else {
                    previous->next = current->next;
                }

                if (current->ticket.passType == "vip") {
                    --vipTickets_;
                }
                --ticketCount_;
                delete current;

                std::ostringstream output;
                output << "REMOVED " << ticketId << " BUCKET " << bucket;
                return output.str();
            }

            previous = current;
            current = current->next;
        }

        return "MISSING " + ticketId;
    }

    std::array<int, BUCKET_COUNT> bucketCounts() const {
        std::array<int, BUCKET_COUNT> counts{};
        for (std::size_t bucket = 0; bucket < BUCKET_COUNT; ++bucket) {
            TicketNode* current = buckets_[bucket];
            while (current != nullptr) {
                ++counts[bucket];
                current = current->next;
            }
        }
        return counts;
    }

    CategorySummary categorySummary() const {
        CategorySummary summary;
        summary.totalTickets = ticketCount_;
        summary.vipTickets = vipTickets_;

        std::vector<std::pair<std::string, int>> overallCounts;
        std::vector<std::pair<std::string, int>> artistCounts;
        std::vector<std::pair<std::string, int>> voiceCounts;
        std::vector<std::pair<std::string, int>> singerCounts;
        std::vector<std::pair<std::string, int>> liveCounts;

        for (TicketNode* head : buckets_) {
            TicketNode* current = head;
            while (current != nullptr) {
                const Ticket& ticket = current->ticket;
                bumpNameCount(overallCounts, ticket.celebrity->name());

                const std::string type = ticket.celebrity->typeLabel();
                if (type == "Artist") {
                    ++summary.artistCount;
                    bumpNameCount(artistCounts, ticket.celebrity->name());
                } else if (type == "VoiceActor") {
                    ++summary.voiceActorCount;
                    bumpNameCount(voiceCounts, ticket.celebrity->name());
                } else if (type == "Singer") {
                    ++summary.singerCount;
                    bumpNameCount(singerCounts, ticket.celebrity->name());
                } else if (type == "LiveActionActor") {
                    ++summary.liveActionCount;
                    bumpNameCount(liveCounts, ticket.celebrity->name());
                }

                current = current->next;
            }
        }

        summary.artistFavorite = pickFavorite(artistCounts);
        summary.voiceActorFavorite = pickFavorite(voiceCounts);
        summary.singerFavorite = pickFavorite(singerCounts);
        summary.liveActionFavorite = pickFavorite(liveCounts);
        summary.overallFavorite = pickFavorite(overallCounts);

        std::vector<std::string> missing;
        if (summary.artistCount == 0) {
            missing.emplace_back("Artist");
        }
        if (summary.voiceActorCount == 0) {
            missing.emplace_back("VoiceActor");
        }
        if (summary.singerCount == 0) {
            missing.emplace_back("Singer");
        }
        if (summary.liveActionCount == 0) {
            missing.emplace_back("LiveActionActor");
        }

        if (!missing.empty()) {
            std::ostringstream output;
            for (std::size_t index = 0; index < missing.size(); ++index) {
                if (index > 0) {
                    output << ',';
                }
                output << missing[index];
            }
            summary.missingCategories = output.str();
        }

        return summary;
    }

private:
    std::array<TicketNode*, BUCKET_COUNT> buckets_{};
    int ticketCount_ = 0;
    int vipTickets_ = 0;

    TicketNode* findNode(const std::string& ticketId) const {
        const std::size_t bucket = hashTicket(ticketId);
        TicketNode* current = buckets_[bucket];
        while (current != nullptr) {
            if (current->ticket.ticketId == ticketId) {
                return current;
            }
            current = current->next;
        }
        return nullptr;
    }

    void clear() {
        for (TicketNode*& head : buckets_) {
            while (head != nullptr) {
                TicketNode* next = head->next;
                delete head;
                head = next;
            }
        }
    }
};

bool normalizePassType(const std::string& rawPassType, std::string& normalized) {
    normalized = toLower(trim(rawPassType));
    return normalized == "standard" || normalized == "vip";
}

void printBucketReport(const TicketDatabase& database) {
    const auto counts = database.bucketCounts();
    for (std::size_t index = 0; index < counts.size(); ++index) {
        std::cout << "BUCKET " << index << '=' << counts[index] << '\n';
    }
}

void printCategoryReport(const TicketDatabase& database) {
    const CategorySummary summary = database.categorySummary();
    std::cout << "TOTAL_TICKETS=" << summary.totalTickets << '\n';
    std::cout << "VIP_TICKETS=" << summary.vipTickets << '\n';
    std::cout << "ARTIST_COUNT=" << summary.artistCount << " FAVORITE=" << summary.artistFavorite << '\n';
    std::cout << "VOICE_ACTOR_COUNT=" << summary.voiceActorCount << " FAVORITE=" << summary.voiceActorFavorite << '\n';
    std::cout << "SINGER_COUNT=" << summary.singerCount << " FAVORITE=" << summary.singerFavorite << '\n';
    std::cout << "LIVE_ACTION_COUNT=" << summary.liveActionCount << " FAVORITE=" << summary.liveActionFavorite << '\n';
    std::cout << "OVERALL_FAVORITE=" << summary.overallFavorite << '\n';
    std::cout << "MISSING_CATEGORIES=" << summary.missingCategories << '\n';
}

} // namespace

int main() {
    TicketDatabase database;
    std::string line;

    while (std::getline(std::cin, line)) {
        line = trim(line);
        if (line.empty() || line[0] == '#') {
            continue;
        }

        std::vector<std::string> fields = split(line, '|');
        if (fields.empty()) {
            continue;
        }

        const std::string& command = fields[0];

        if (command == "QUIT") {
            break;
        }

        if (command == "BUCKET_REPORT") {
            printBucketReport(database);
            continue;
        }

        if (command == "CATEGORY_REPORT") {
            printCategoryReport(database);
            continue;
        }

        if (command == "LOOKUP") {
            if (fields.size() != 2) {
                std::cout << "ERROR malformed command LOOKUP" << '\n';
                continue;
            }
            const Ticket* ticket = database.findTicket(fields[1]);
            if (ticket == nullptr) {
                std::cout << "MISSING " << fields[1] << '\n';
            } else {
                std::cout << ticket->lookupSummary() << '\n';
            }
            continue;
        }

        if (command == "REMOVE") {
            if (fields.size() != 2) {
                std::cout << "ERROR malformed command REMOVE" << '\n';
                continue;
            }
            std::cout << database.removeTicket(fields[1]) << '\n';
            continue;
        }

        if (command == "ADD_ARTIST" || command == "ADD_VOICE" || command == "ADD_SINGER" || command == "ADD_LIVE") {
            if (fields.size() != 7) {
                std::cout << "ERROR malformed command " << command << '\n';
                continue;
            }

            std::string normalizedPassType;
            if (!normalizePassType(fields[3], normalizedPassType)) {
                std::cout << "ERROR invalid pass_type " << fields[3] << '\n';
                continue;
            }
            fields[3] = normalizedPassType;

            if (command == "ADD_ARTIST") {
                int commissionRate = 0;
                if (!parseInteger(fields[6], commissionRate)) {
                    std::cout << "ERROR malformed command ADD_ARTIST" << '\n';
                    continue;
                }
                std::cout << database.addTicket(
                    Ticket{fields[1], fields[2], fields[3], std::make_unique<Artist>(fields[4], fields[5], commissionRate)}
                ) << '\n';
                continue;
            }

            if (command == "ADD_VOICE") {
                std::cout << database.addTicket(
                    Ticket{fields[1], fields[2], fields[3], std::make_unique<VoiceActor>(fields[4], fields[5], fields[6])}
                ) << '\n';
                continue;
            }

            if (command == "ADD_SINGER") {
                int chartCount = 0;
                if (!parseInteger(fields[6], chartCount)) {
                    std::cout << "ERROR malformed command ADD_SINGER" << '\n';
                    continue;
                }
                std::cout << database.addTicket(
                    Ticket{fields[1], fields[2], fields[3], std::make_unique<Singer>(fields[4], fields[5], chartCount)}
                ) << '\n';
                continue;
            }

            std::cout << database.addTicket(
                Ticket{fields[1], fields[2], fields[3], std::make_unique<LiveActionActor>(fields[4], fields[5], fields[6])}
            ) << '\n';
            continue;
        }

        std::cout << "ERROR unknown command " << command << '\n';
    }

    return 0;
}