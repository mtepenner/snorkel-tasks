# [TRAVEL-622] group itinerary desk is still doing this by hand and it is breaking assignments

Need a standalone C++17 CLI under `/app/workspace/src/travel_groups.cpp`. Tiny helper files in the same folder are fine, but the harness compiles `/app/workspace/src/*.cpp`, so keep the deliverable there.

The booking desk wants an array of **exactly 3** circular linked lists. The three array slots are fixed travel groups in this exact order: `scotland`, `hamburg`, `moscow`. Each node is one traveler itinerary. This is not a `std::map` exercise and it is not a vector pretending to be a ring.

Every itinerary stores `booking_id`, `traveler_name`, `group`, `nights`, and `transport`. Allowed transports are `flight`, `train`, and `ferry`. `nights` must be a positive integer.

Use `stdin` commands with `|` separators. Ignore blank lines and lines beginning with `#`.

## Command contract

- `BOOK|booking_id|traveler_name|group|nights|transport` inserts a traveler at the tail of that group's circular list.
- `SHOW|booking_id` returns one line describing the matching itinerary or `MISSING <booking_id>`.
- `ADVANCE|group|steps` moves that group's current pointer forward by `steps` around the circular list and prints the new current itinerary. Wraparound is required.
- `CANCEL|booking_id` removes the matching node from whatever group contains it.
- `GROUP_REPORT` prints one line for each group in array order.
- `TRANSPORT_REPORT` prints the aggregate transport summary block shown below.

Reject duplicates and bad inputs with these exact strings:

```text
ERROR duplicate booking <booking_id>
ERROR invalid group <value>
ERROR invalid nights <value>
ERROR invalid transport <value>
```

Successful inserts use this exact string:

```text
BOOKED <booking_id> GROUP <group>
```

`SHOW` must print this exact shape:

```text
FOUND <booking_id> | traveler=<traveler_name> | group=<group> | nights=<nights> | transport=<transport>
```

`ADVANCE` must print this exact shape when the group is non-empty:

```text
CURRENT <group> <booking_id> <traveler_name>
```

If `ADVANCE` is called on an empty group, print:

```text
EMPTY <group>
```

`CANCEL` must print either `CANCELLED <booking_id> GROUP <group>` or `MISSING <booking_id>`.

`GROUP_REPORT` prints these exact three lines in this order:

```text
GROUP scotland=<count> CURRENT=<booking_id_or_EMPTY>
GROUP hamburg=<count> CURRENT=<booking_id_or_EMPTY>
GROUP moscow=<count> CURRENT=<booking_id_or_EMPTY>
```

`TRANSPORT_REPORT` prints this exact five-line block:

```text
TOTAL_BOOKINGS=<count>
SCOTLAND_FAVORITE_TRANSPORT=<transport_or_NONE>
HAMBURG_FAVORITE_TRANSPORT=<transport_or_NONE>
MOSCOW_FAVORITE_TRANSPORT=<transport_or_NONE>
OVERALL_FAVORITE_TRANSPORT=<transport_or_NONE>
```

Favorite transport means the most-booked transport in that scope; ties break alphabetically.

Compile cleanly with `g++ -std=c++17 -Wall -Wextra -pedantic`. Use an actual circular linked-list structure with `next` pointers and wraparound behavior.
