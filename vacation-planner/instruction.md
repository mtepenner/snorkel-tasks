# Vacation Planner Cruise Backend

We need a C++ application that models a cruise-line member hierarchy using an array of linked lists. Each linked list represents a vacation week, and maintains members sorted by their tier priority.

## Objectives
1. **Data Structure**: Create an array (or container) of linear linked lists. Each array slot represents a distinct vacation week.
2. **Class Hierarchy**: Implement a base `Member` class and 5 derived child classes representing the following tiers:
   - `Base`
   - `Silver`
   - `Gold`
   - `Platinum`
   - `Diamond`
3. **Priority Sorting**: When a member is inserted into a week's linked list, they must be sorted by tier priority. `Diamond` members have the highest priority and should be at the front of the list to board early, followed by `Platinum`, `Gold`, `Silver`, and finally `Base`.

## Success Criteria
- Write your C++ source code and place it under the directory `/app/workspace/`.
- Ensure your C++ program compiles and accurately implements the linked list concepts, tier array, and inheritance.
- The compiled program must execute and print to standard output (`stdout`) demonstrating the priority list for at least one week containing all 5 tiers.
- The output format should sequentially list the tiers in descending priority order (Diamond to Base), for example:
  ```
  Week 1 Boarding Order:
  Diamond Member
  Platinum Member
  Gold Member
  Silver Member
  Base Member
  ```
