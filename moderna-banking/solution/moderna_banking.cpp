#include <iostream>
#include <string>

using namespace std;

// Circular Linked List Node
struct TransactionNode {
    string transaction_name;
    double amount;
    string date;
    TransactionNode* next;
};

// Linear Linked List Node
struct AccountNode {
    double account_balance;
    string holder_name;
    string membership_date;
    int fico_score;
    string account_expiration_date;
    
    TransactionNode* transactions_head;
    AccountNode* next;
};

// Array Element
struct Region {
    string region_name;
    AccountNode* accounts_head;
};

int main() {
    // 1. Create Array of Regions
    Region pacific_nw[3];
    pacific_nw[0].region_name = "Seattle";
    pacific_nw[0].accounts_head = nullptr;
    
    // 2. Create an Account (Linear Linked List Node)
    AccountNode* acc1 = new AccountNode();
    acc1->account_balance = 15000.50;
    acc1->holder_name = "John Doe";
    acc1->membership_date = "2023-01-01";
    acc1->fico_score = 750;
    acc1->account_expiration_date = "2030-01-01";
    acc1->transactions_head = nullptr;
    acc1->next = nullptr;
    
    pacific_nw[0].accounts_head = acc1;
    
    // 3. Create a Transaction (Circular Linked List Node)
    TransactionNode* t1 = new TransactionNode();
    t1->transaction_name = "Grocery";
    t1->amount = 50.0;
    t1->date = "2026-05-04";

    TransactionNode* t2 = new TransactionNode();
    t2->transaction_name = "Gas";
    t2->amount = 20.0;
    t2->date = "2026-05-05";
    
    // Make it circular
    t1->next = t2;
    t2->next = t1;
    acc1->transactions_head = t1;
    
    // 4. Display the Hierarchy
    cout << "Region: " << pacific_nw[0].region_name << endl;
    AccountNode* curr_acc = pacific_nw[0].accounts_head;
    while(curr_acc != nullptr) {
        cout << "  Account Holder: " << curr_acc->holder_name << " | FICO: " << curr_acc->fico_score 
             << " | Membership: " << curr_acc->membership_date << " | Expires: " << curr_acc->account_expiration_date
             << " | Balance: $" << curr_acc->account_balance << endl;
        
        TransactionNode* curr_trans = curr_acc->transactions_head;
        if (curr_trans != nullptr) {
            // Print 3 transactions to demonstrate circular loop
            for (int i = 0; i < 3; i++) {
                cout << "    Transaction: " << curr_trans->transaction_name << " | Amount: $" << curr_trans->amount << " | Date: " << curr_trans->date << endl;
                curr_trans = curr_trans->next;
            }
        }
        curr_acc = curr_acc->next;
    }
    
    return 0;
}