#include <algorithm>
#include <array>
#include <cctype>
#include <iostream>
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

bool parsePositiveInt(const std::string& value, int& parsed) {
    try {
        std::size_t consumed = 0;
        int candidate = std::stoi(value, &consumed);
        if (consumed != value.size() || candidate <= 0) {
            return false;
        }
        parsed = candidate;
        return true;
    } catch (...) {
        return false;
    }
}

void bumpCount(std::vector<std::pair<std::string, int>>& counts, const std::string& key) {
    for (auto& entry : counts) {
        if (entry.first == key) {
            ++entry.second;
            return;
        }
    }
    counts.emplace_back(key, 1);
}

std::string favoriteValue(const std::vector<std::pair<std::string, int>>& counts) {
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

struct Itinerary {
    std::string bookingId;
    std::string travelerName;
    std::string group;
    int nights = 0;
    std::string transport;
};

struct ItineraryNode {
    Itinerary itinerary;
    ItineraryNode* next;

    explicit ItineraryNode(Itinerary value) : itinerary(std::move(value)), next(nullptr) {}
};

struct GroupCircle {
    std::string name;
    ItineraryNode* tail = nullptr;
    ItineraryNode* current = nullptr;
    int size = 0;

    bool empty() const {
        return tail == nullptr;
    }

    ItineraryNode* head() const {
        return empty() ? nullptr : tail->next;
    }
};

class TravelDesk {
public:
    static constexpr std::size_t GROUP_COUNT = 3;

    TravelDesk() {
        groups_[0].name = "scotland";
        groups_[1].name = "hamburg";
        groups_[2].name = "moscow";
    }

    ~TravelDesk() {
        clear();
    }

    bool bookingExists(const std::string& bookingId) const {
        for (const GroupCircle& group : groups_) {
            if (findInGroup(group, bookingId) != nullptr) {
                return true;
            }
        }
        return false;
    }

    GroupCircle* findGroup(const std::string& groupName) {
        for (GroupCircle& group : groups_) {
            if (group.name == groupName) {
                return &group;
            }
        }
        return nullptr;
    }

    const Itinerary* findBooking(const std::string& bookingId) const {
        for (const GroupCircle& group : groups_) {
            ItineraryNode* node = findInGroup(group, bookingId);
            if (node != nullptr) {
                return &node->itinerary;
            }
        }
        return nullptr;
    }

    std::string book(Itinerary itinerary) {
        GroupCircle* group = findGroup(itinerary.group);
        ItineraryNode* node = new ItineraryNode(std::move(itinerary));

        if (group->empty()) {
            node->next = node;
            group->tail = node;
            group->current = node;
        } else {
            node->next = group->tail->next;
            group->tail->next = node;
            group->tail = node;
        }

        ++group->size;
        ++totalBookings_;
        return "BOOKED " + group->tail->itinerary.bookingId + " GROUP " + group->name;
    }

    std::string show(const std::string& bookingId) const {
        const Itinerary* itinerary = findBooking(bookingId);
        if (itinerary == nullptr) {
            return "MISSING " + bookingId;
        }

        std::ostringstream output;
        output << "FOUND " << itinerary->bookingId
               << " | traveler=" << itinerary->travelerName
               << " | group=" << itinerary->group
               << " | nights=" << itinerary->nights
               << " | transport=" << itinerary->transport;
        return output.str();
    }

    std::string advance(const std::string& groupName, int steps) {
        GroupCircle* group = findGroup(groupName);
        if (group->empty()) {
            return "EMPTY " + group->name;
        }

        int moves = steps % group->size;
        for (int index = 0; index < moves; ++index) {
            group->current = group->current->next;
        }

        std::ostringstream output;
        output << "CURRENT " << group->name << ' ' << group->current->itinerary.bookingId << ' ' << group->current->itinerary.travelerName;
        return output.str();
    }

    std::string cancel(std::string bookingId) {
        for (GroupCircle& group : groups_) {
            if (group.empty()) {
                continue;
            }

            ItineraryNode* previous = group.tail;
            ItineraryNode* node = group.tail->next;
            for (int index = 0; index < group.size; ++index) {
                if (node->itinerary.bookingId == bookingId) {
                    if (group.size == 1) {
                        delete node;
                        group.tail = nullptr;
                        group.current = nullptr;
                    } else {
                        previous->next = node->next;
                        if (node == group.tail) {
                            group.tail = previous;
                        }
                        if (node == group.current) {
                            group.current = previous;
                        }
                        delete node;
                    }

                    --group.size;
                    --totalBookings_;
                    return "CANCELLED " + bookingId + " GROUP " + group.name;
                }

                previous = node;
                node = node->next;
            }
        }

        return "MISSING " + bookingId;
    }

    void printGroupReport() const {
        for (const GroupCircle& group : groups_) {
            std::cout << "GROUP " << group.name << '=' << group.size << " CURRENT=";
            if (group.current == nullptr) {
                std::cout << "EMPTY";
            } else {
                std::cout << group.current->itinerary.bookingId;
            }
            std::cout << '\n';
        }
    }

    void printTransportReport() const {
        std::cout << "TOTAL_BOOKINGS=" << totalBookings_ << '\n';
        std::cout << "SCOTLAND_FAVORITE_TRANSPORT=" << favoriteTransport(groups_[0]) << '\n';
        std::cout << "HAMBURG_FAVORITE_TRANSPORT=" << favoriteTransport(groups_[1]) << '\n';
        std::cout << "MOSCOW_FAVORITE_TRANSPORT=" << favoriteTransport(groups_[2]) << '\n';
        std::cout << "OVERALL_FAVORITE_TRANSPORT=" << overallFavoriteTransport() << '\n';
    }

private:
    std::array<GroupCircle, GROUP_COUNT> groups_{};
    int totalBookings_ = 0;

    static ItineraryNode* findInGroup(const GroupCircle& group, const std::string& bookingId) {
        if (group.empty()) {
            return nullptr;
        }

        ItineraryNode* node = group.tail->next;
        for (int index = 0; index < group.size; ++index) {
            if (node->itinerary.bookingId == bookingId) {
                return node;
            }
            node = node->next;
        }
        return nullptr;
    }

    static std::string favoriteTransport(const GroupCircle& group) {
        if (group.empty()) {
            return "NONE";
        }

        std::vector<std::pair<std::string, int>> counts;
        ItineraryNode* node = group.tail->next;
        for (int index = 0; index < group.size; ++index) {
            bumpCount(counts, node->itinerary.transport);
            node = node->next;
        }
        return favoriteValue(counts);
    }

    std::string overallFavoriteTransport() const {
        std::vector<std::pair<std::string, int>> counts;
        for (const GroupCircle& group : groups_) {
            if (group.empty()) {
                continue;
            }
            ItineraryNode* node = group.tail->next;
            for (int index = 0; index < group.size; ++index) {
                bumpCount(counts, node->itinerary.transport);
                node = node->next;
            }
        }
        return favoriteValue(counts);
    }

    void clear() {
        for (GroupCircle& group : groups_) {
            while (!group.empty()) {
                cancel(group.tail->next->itinerary.bookingId);
            }
        }
    }
};

bool isValidTransport(const std::string& transport) {
    return transport == "flight" || transport == "train" || transport == "ferry";
}

} // namespace

int main() {
    TravelDesk desk;
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

        const std::string command = fields[0];

        if (command == "QUIT") {
            break;
        }

        if (command == "BOOK") {
            if (fields.size() != 6) {
                std::cout << "ERROR malformed command BOOK" << '\n';
                continue;
            }

            const std::string group = toLower(fields[3]);
            int nights = 0;
            const std::string transport = toLower(fields[5]);

            if (desk.bookingExists(fields[1])) {
                std::cout << "ERROR duplicate booking " << fields[1] << '\n';
                continue;
            }

            if (desk.findGroup(group) == nullptr) {
                std::cout << "ERROR invalid group " << fields[3] << '\n';
                continue;
            }

            if (!parsePositiveInt(fields[4], nights)) {
                std::cout << "ERROR invalid nights " << fields[4] << '\n';
                continue;
            }

            if (!isValidTransport(transport)) {
                std::cout << "ERROR invalid transport " << fields[5] << '\n';
                continue;
            }

            Itinerary itinerary{fields[1], fields[2], group, nights, transport};
            std::cout << desk.book(std::move(itinerary)) << '\n';
            continue;
        }

        if (command == "SHOW") {
            if (fields.size() != 2) {
                std::cout << "ERROR malformed command SHOW" << '\n';
                continue;
            }
            std::cout << desk.show(fields[1]) << '\n';
            continue;
        }

        if (command == "ADVANCE") {
            if (fields.size() != 3) {
                std::cout << "ERROR malformed command ADVANCE" << '\n';
                continue;
            }

            const std::string group = toLower(fields[1]);
            int steps = 0;
            if (desk.findGroup(group) == nullptr) {
                std::cout << "ERROR invalid group " << fields[1] << '\n';
                continue;
            }
            if (!parsePositiveInt(fields[2], steps)) {
                std::cout << "ERROR invalid nights " << fields[2] << '\n';
                continue;
            }
            std::cout << desk.advance(group, steps) << '\n';
            continue;
        }

        if (command == "CANCEL") {
            if (fields.size() != 2) {
                std::cout << "ERROR malformed command CANCEL" << '\n';
                continue;
            }
            std::cout << desk.cancel(fields[1]) << '\n';
            continue;
        }

        if (command == "GROUP_REPORT") {
            desk.printGroupReport();
            continue;
        }

        if (command == "TRANSPORT_REPORT") {
            desk.printTransportReport();
            continue;
        }

        std::cout << "ERROR unknown command " << command << '\n';
    }

    return 0;
}