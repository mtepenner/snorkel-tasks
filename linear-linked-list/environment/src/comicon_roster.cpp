#include <iostream>

class Celebrity {
public:
    virtual ~Celebrity() = default;
};

class Artist : public Celebrity {};
class VoiceActor : public Celebrity {};
class Singer : public Celebrity {};
class LiveActionActor : public Celebrity {};

struct TicketNode {
    TicketNode* next = nullptr;
};

int main() {
    // TODO: Replace this placeholder with a real comicon ticket database.
    // Requirements are in instruction.md:
    // - array of 7 linear linked lists
    // - celebrity class hierarchy with virtual dispatch
    // - stdin command processing for add/lookup/remove/report operations
    std::cout << "TODO" << std::endl;
    return 0;
}