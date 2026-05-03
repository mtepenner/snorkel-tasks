The travel desk is still tracking group itineraries by hand, and I need a small C++17 CLI to take that over.

Put the main program in `/app/workspace/src/travel_groups.cpp`. Small helper files in the same folder are fine, but the harness compiles `/app/workspace/src/*.cpp`, so anything that needs to build has to live there.

Use an array of exactly 3 circular linked lists. The slots are fixed in this order: `scotland`, `hamburg`, `moscow`. Each node is one itinerary with `booking_id`, `traveler_name`, `group`, `nights`, and `transport`.

Valid transports are `flight`, `train`, and `ferry`. `nights` must be a positive integer.

Please use a real circular linked-list structure with `next` pointers and wraparound behavior. Do not solve this with `std::map`, and do not fake the ring with a vector.

Read commands from `stdin`, split on `|`, and ignore blank lines or lines that start with `#`.

The input language is small. A booking request arrives as `BOOK|booking_id|traveler_name|group|nights|transport` and should append that itinerary to the tail of the named group's circular list. If the booking id already exists anywhere in the structure, print `ERROR duplicate booking <booking_id>`. If the group name is anything other than `scotland`, `hamburg`, or `moscow`, print `ERROR invalid group <value>`. If `nights` is not a positive integer, print `ERROR invalid nights <value>`, and if `transport` is not one of `flight`, `train`, or `ferry`, print `ERROR invalid transport <value>`. A successful booking must print `BOOKED <booking_id> GROUP <group>`.

Each group keeps a current pointer as well as the ring itself. When a group receives its first booking, that new node becomes current. Later `BOOK` commands still append at the tail, but they do not change current. An `ADVANCE|group|steps` request starts from the current node for that group, walks forward by `steps` with wraparound, and prints `CURRENT <group> <booking_id> <traveler_name>` for the new current node. If that group's ring is empty, the exact response is `EMPTY <group>`.

A `SHOW|booking_id` request either prints `MISSING <booking_id>` or returns one line in the exact form `FOUND <booking_id> | traveler=<traveler_name> | group=<group> | nights=<nights> | transport=<transport>`. A `CANCEL|booking_id` request removes the matching node from whichever group contains it and prints either `CANCELLED <booking_id> GROUP <group>` or `MISSING <booking_id>`. If the cancelled node is not current, current stays where it was. If the cancelled node is current and the group still has other nodes, current moves to the previous node in the ring. If the cancelled node was the only node, that group becomes empty and current becomes `EMPTY`.

`GROUP_REPORT` prints exactly three lines in array order, one for `scotland`, then one for `hamburg`, then one for `moscow`. Those lines must be `GROUP scotland=<count> CURRENT=<booking_id_or_EMPTY>`, `GROUP hamburg=<count> CURRENT=<booking_id_or_EMPTY>`, and `GROUP moscow=<count> CURRENT=<booking_id_or_EMPTY>`. `TRANSPORT_REPORT` prints a five-line summary in this exact order: `TOTAL_BOOKINGS=<count>`, `SCOTLAND_FAVORITE_TRANSPORT=<transport_or_NONE>`, `HAMBURG_FAVORITE_TRANSPORT=<transport_or_NONE>`, `MOSCOW_FAVORITE_TRANSPORT=<transport_or_NONE>`, and `OVERALL_FAVORITE_TRANSPORT=<transport_or_NONE>`. Favorite transport means the most-booked transport in that scope, with alphabetical tiebreaks.

Build it with `g++ -std=c++17 -Wall -Wextra -pedantic`, and it should compile with no warnings.
