#include <iostream>
#include <string>
#include <sstream>

using namespace std;

class Member {
public:
    string name;
    int priority;
    Member(string n, int p) : name(n), priority(p) {}
    virtual ~Member() {}
    virtual string getTier() const = 0;
};

class Diamond : public Member {
public:
    Diamond(string n) : Member(n, 5) {}
    string getTier() const override { return "Diamond"; }
};

class Platinum : public Member {
public:
    Platinum(string n) : Member(n, 4) {}
    string getTier() const override { return "Platinum"; }
};

class Gold : public Member {
public:
    Gold(string n) : Member(n, 3) {}
    string getTier() const override { return "Gold"; }
};

class Silver : public Member {
public:
    Silver(string n) : Member(n, 2) {}
    string getTier() const override { return "Silver"; }
};

class Base : public Member {
public:
    Base(string n) : Member(n, 1) {}
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
    
    void print() const {
        Node* current = head;
        while(current) {
            cout << current->member->getTier() << " " << current->member->name << endl;
            current = current->next;
        }
    }
};

int main() {
    LinkedList vacationWeeks[100];
    
    string line;
    while (getline(cin, line)) {
        if (line.empty()) continue;
        stringstream ss(line);
        string cmd;
        ss >> cmd;
        
        if (cmd == "ADD") {
            int week;
            string tier, name;
            ss >> week >> tier >> name;
            
            Member* m = nullptr;
            if (tier == "Diamond") m = new Diamond(name);
            else if (tier == "Platinum") m = new Platinum(name);
            else if (tier == "Gold") m = new Gold(name);
            else if (tier == "Silver") m = new Silver(name);
            else if (tier == "Base") m = new Base(name);
            
            if (m && week >= 0 && week < 100) {
                vacationWeeks[week].insert(m);
            }
        }
        else if (cmd == "PRINT") {
            int week;
            ss >> week;
            cout << "Week " << week << " Boarding Order:" << endl;
            if (week >= 0 && week < 100) {
                vacationWeeks[week].print();
            }
        }
    }
    return 0;
}
