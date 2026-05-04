Moderna Banking Networks is expanding into the Pacific Northwest and needs a new C++ backend service to manage regional accounts. The system must organize accounts efficiently by geographic region. Each account profile must track the account balance, holder's name, membership date, FICO score, and account expiration date.



Additionally, each account must maintain a continuous, looping history of transactions (transaction name, amount, and date) that can be easily traversed. The system needs a feature to output this data hierarchically to the terminal (e.g., Region -> Account -> Transactions) to verify regional groupings and transaction histories are properly linked.



To demonstrate the hierarchy works, the application should initialize with a sample Region ('Seattle'), Account ('John Doe'), and a $50.0 'Grocery' transaction. For integration with our CI pipeline, please implement the source code at `/app/workspace/src/moderna\_banking.cpp` and output the compiled executable to `/usr/local/bin/moderna-app` so our automated systems can run the report.

