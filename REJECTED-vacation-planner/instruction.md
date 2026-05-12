We need a C++ application that models a cruise-line member hierarchy using an array of linked lists. Each linked list represents a vacation week, and maintains members sorted by their tier priority.

### Requirements

1. **Data Structure**: Create an array (or container) of linear linked lists. Each array slot represents a distinct vacation week (e.g., weeks 1-52).
2. **Class Hierarchy**: Implement a base \Member\ class and 5 derived child classes representing the following tiers:
   - \Base\
   - \Silver\
   - \Gold\
   - \Platinum\
   - \Diamond\
3. **Priority Sorting**: When a member is inserted into a week's linked list, they must be sorted by tier priority. \Diamond\ members have the highest priority and should be at the front of the list to board early, followed by \Platinum\, \Gold\, \Silver\, and finally \Base\.

### Input and Output

Your program must read commands from standard input (\stdin\) line by line until EOF. It should support two commands:

1. \ADD <week_number> <tier> <name>\
   - Example: \ADD 1 Diamond Alice\
   - Adds a member to the specified vacation week.
2. \PRINT <week_number>\
   - Example: \PRINT 1\
   - Prints the boarding order for the specified week.

For each \PRINT\ command, the output format should sequentially list the members in descending priority order. For example:
\\\
Week 1 Boarding Order:
Diamond Alice
Platinum Bob
Gold Charlie
Silver Dave
Base Eve
\\\

- Write your C++ source code and place it under the directory \/app/workspace/\.
- Ensure your C++ program compiles and accurately implements the linked list concepts, tier array, and inheritance.
