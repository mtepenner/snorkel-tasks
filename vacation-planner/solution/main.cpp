#include <iostream>
#include <string>

using namespace std;

// Base class
class Member {
public:
    string name;
    int priority;
    Member(string n, int p) : name(n), priority(p) {}
    virtual ~Member() {}
    virtual string getTier() const = 0;
};

// Derived classes
class DiamondMember : public Member {
public:
    DiamondMember(string n) : Member(n, 5) {}
    string getTier() const override { return "Diamond"; }
};

class PlatinumMember : public Member {
public:
    PlatinumMember(string n) : Member(n, 4) {}
    string getTier() const override { return "Platinum"; }
};

class GoldMember : public Member {
public:
    GoldMember(string n) : Member(n, 3) {}
    string getTier() const override { return "Gold"; }
};

class SilverMember : public Member {
public:
    SilverMember(string n) : Member(n, 2) {}
    string getTier() const override { return "Silver"; }
};

class BaseMember : public Member {
public:
    BaseMember(string n) : Member(n, 1) {}
    string getTier() const override { return "Base"; }
};

struct Node {
    Member* member;
    Node* next;
    Node(Member* m) : member(m), next(nullptr) {}
};

class LinkedList {
public:
    Node* head;
    LinkedList() : head(nullptr) {}
    
    void insert(Member* m) {
        Node* newNode = new Node(m);
        // Insert in descending order of priority
        if (!head || head->member->priority < m->priority) {
            newNode->next = head;
            head = newNode;
        } else {
            Node* current = head;
            while (current->next && current->next->member->priority >= m->priority) {
                current = current->next;
            }
            newNode->next = current->next;
            current->next = newNode;
        }
    }
    
    void print() {
        Node* current = head;
        while(current) {
            cout << current->member->name << " (" << current->member->getTier() << ")" << endl;
            current = current->next;
        }
    }
};

int main() {
    // Array of linear linked lists
    LinkedList vacationWeeks[2];
    
    vacationWeeks[0].insert(new GoldMember("Charlie"));
    vacationWeeks[0].insert(new DiamondMember("Bob"));
    vacationWeeks[0].insert(new BaseMember("Alice"));
    vacationWeeks[0].insert(new SilverMember("Eve"));
    vacationWeeks[0].insert(new PlatinumMember("Dave"));
    
    cout << "Week 1 Boarding List:" << endl;
    vacationWeeks[0].print();
    
    return 0;
}