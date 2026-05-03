The travel desk is still tracking group itineraries by hand, and I need a small C++17 CLI to take that over.

Put the main program in `/app/workspace/src/travel_groups.cpp`. Small helper files in the same folder are fine, but the harness compiles `/app/workspace/src/*.cpp`, so anything that needs to build has to live there.

Use an array of exactly 3 circular linked lists. The slots are fixed in this order: `scotland`, `hamburg`, `moscow`. Each node is one itinerary with `booking_id`, `traveler_name`, `group`, `nights`, and `transport`.

Valid transports are `flight`, `train`, and `ferry`. `nights` must be a positive integer.

Please use a real circular linked-list structure with `next` pointers and wraparound behavior. Do not solve this with `std::map`, and do not fake the ring with a vector.

Read commands from `stdin`, split on `|`, and ignore blank lines or lines that start with `#`.

Commands:

- `BOOK|booking_id|traveler_name|group|nights|transport` appends a traveler to the tail of that group's circular list.
- `SHOW|booking_id` prints the matching itinerary or `MISSING <booking_id>`.
- `ADVANCE|group|steps` moves that group's current pointer forward by `steps` and prints the new current itinerary. Wraparound is required.
- `CANCEL|booking_id` removes the matching node from whichever group contains it.
- `GROUP_REPORT` prints one line per group in array order.
- `TRANSPORT_REPORT` prints the transport summary block.

Each group also has a current pointer, and the tests expect these rules:

- When a group gets its first booking, that new node becomes current.
- Later `BOOK` commands append at the tail and do not move current.
- `ADVANCE` starts from the current node and walks forward around the ring.
- If `CANCEL` removes a node that is not current, current stays where it was.
- If `CANCEL` removes the current node and the group still has other nodes, current moves to the previous node in the ring.
- If `CANCEL` removes the only node in the group, the group becomes empty and current becomes `EMPTY`.

Use these exact errors:

	ERROR duplicate booking <booking_id>
	ERROR invalid group <value>
	ERROR invalid nights <value>
	ERROR invalid transport <value>

A successful `BOOK` prints:

	BOOKED <booking_id> GROUP <group>

`SHOW` prints:

	FOUND <booking_id> | traveler=<traveler_name> | group=<group> | nights=<nights> | transport=<transport>

`ADVANCE` on a non-empty group prints:

	CURRENT <group> <booking_id> <traveler_name>

If `ADVANCE` is called on an empty group, print:

	EMPTY <group>

`CANCEL` prints either `CANCELLED <booking_id> GROUP <group>` or `MISSING <booking_id>`.

`GROUP_REPORT` must print exactly these three lines in this order:

	GROUP scotland=<count> CURRENT=<booking_id_or_EMPTY>
	GROUP hamburg=<count> CURRENT=<booking_id_or_EMPTY>
	GROUP moscow=<count> CURRENT=<booking_id_or_EMPTY>

`TRANSPORT_REPORT` must print exactly this five-line block:

	TOTAL_BOOKINGS=<count>
	SCOTLAND_FAVORITE_TRANSPORT=<transport_or_NONE>
	HAMBURG_FAVORITE_TRANSPORT=<transport_or_NONE>
	MOSCOW_FAVORITE_TRANSPORT=<transport_or_NONE>
	OVERALL_FAVORITE_TRANSPORT=<transport_or_NONE>

Favorite transport means the most-booked transport in that scope, with alphabetical tiebreaks.

Build it with `g++ -std=c++17 -Wall -Wextra -pedantic`, and it should compile with no warnings.
