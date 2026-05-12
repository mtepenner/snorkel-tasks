# ComicCon Ticket Roster

Implement a standalone C++17 CLI at `/app/workspace/src/comicon_roster.cpp`. The harness compiles all `*.cpp` files in that directory, so you may add small helper files alongside it.

**Ticket store requirement:** use an array of exactly 7 linear linked lists. The bucket index for a ticket is computed as the sum of raw ASCII (unsigned char) values of `ticket_id` modulo 7. You must implement a real celebrity class hierarchy: `Celebrity` base class plus `Artist`, `VoiceActor`, `Singer`, and `LiveActionActor`. The base class needs at least one virtual method that is actually used when formatting output.

Read commands from `stdin`, one per line, using `|` as the separator. Ignore blank lines and lines starting with `#`. Every stored ticket tracks `ticket_id`, `attendee_name`, `pass_type`, and one celebrity object. `pass_type` can only be `standard` or `vip`.

The add commands all use the same seven-field layout: `ADD_<TYPE>|ticket_id|attendee_name|pass_type|celebrity_name|field_a|field_b`. For `ADD_ARTIST`, the last two values are `fandom` and integer `commission_rate`; for `ADD_VOICE`, they are `signature_role` and `union_status`; for `ADD_SINGER`, they are `genre` and integer `chart_count`; for `ADD_LIVE`, they are `franchise` and `stunt_team`. If the ticket id already exists, print `ERROR duplicate ticket <ticket_id>`. If the pass type is anything other than `standard` or `vip`, print `ERROR invalid pass_type <value>`. A successful insert must print `ADDED <ticket_id> BUCKET <bucket_index>`.

A `LOOKUP|ticket_id` request either prints `MISSING <ticket_id>` or returns one exact `FOUND` line in the form `FOUND <ticket_id> | attendee=<attendee_name> | pass=<pass_type> | type=<Artist|VoiceActor|Singer|LiveActionActor> | celebrity=<celebrity_name> | <detail_key_1>=<value> | <detail_key_2>=<value>`. The trailing keys depend on the subtype and must be exactly `fandom` and `commission_rate`, `signature_role` and `union_status`, `genre` and `chart_count`, or `franchise` and `stunt_team`.

`REMOVE|ticket_id` must return either `REMOVED <ticket_id> BUCKET <bucket_index>` or `MISSING <ticket_id>`. `BUCKET_REPORT` prints seven lines in bucket order from 0 through 6, each using the exact shape `BUCKET i=<count>`, so if bucket 0 currently holds three tickets the first line is `BUCKET 0=3`.

`CATEGORY_REPORT` prints eight lines in a fixed order. They are `TOTAL_TICKETS=<count>`, `VIP_TICKETS=<count>`, `ARTIST_COUNT=<count> FAVORITE=<celebrity_name_or_NONE>`, `VOICE_ACTOR_COUNT=<count> FAVORITE=<celebrity_name_or_NONE>`, `SINGER_COUNT=<count> FAVORITE=<celebrity_name_or_NONE>`, `LIVE_ACTION_COUNT=<count> FAVORITE=<celebrity_name_or_NONE>`, `OVERALL_FAVORITE=<celebrity_name_or_NONE>`, and `MISSING_CATEGORIES=<comma_separated_labels_or_NONE>`. Favorite celebrity means the most-selected celebrity in that scope with alphabetical tiebreaks, and the missing-category list must use `Artist,VoiceActor,Singer,LiveActionActor` order.

Compile cleanly with `g++ -std=c++17 -Wall -Wextra -pedantic`, do not use `std::map`/`std::unordered_map` or any database library for the ticket store, and do not fake the linked-list requirement with a vector pretending to be buckets. The provided starter code defines a `TicketNode` struct for you to use.
