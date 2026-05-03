# [VENUE-417] Portland comicon survey + ticket database is blocking roster planning

Need a standalone C++17 CLI under `/app/workspace/src/comicon_roster.cpp`. If you want tiny helper files in the same folder, fine, but the main deliverable has to stay there because the harness compiles `/app/workspace/src/*.cpp`.

This is not a `std::map` exercise. The real ticket store has to be an array of **exactly 7** linear linked lists, keyed by `ticket_id` with `sum of raw ASCII values in ticket_id % 7`. Also need a real celebrity hierarchy: `Celebrity` base class plus `Artist`, `VoiceActor`, `Singer`, and `LiveActionActor`. The base class needs at least one virtual method that is actually used when formatting output.

Read commands from `stdin`, one per line, using `|` as the separator. Ignore blank lines and lines starting with `#`. Every stored ticket tracks `ticket_id`, `attendee_name`, `pass_type`, and one celebrity object. `pass_type` can only be `standard` or `vip`.

## Command contract

- Add commands all use the same pattern: `ADD_<TYPE>|ticket_id|attendee_name|pass_type|celebrity_name|field_a|field_b`. The type-specific fields are `ARTIST => fandom|commission_rate`, `VOICE => signature_role|union_status`, `SINGER => genre|chart_count`, and `LIVE => franchise|stunt_team`. `commission_rate` and `chart_count` are integers.
- `LOOKUP|ticket_id` returns either a single `FOUND ...` line or `MISSING <ticket_id>`.
- `REMOVE|ticket_id` returns either `REMOVED <ticket_id> BUCKET <bucket_index>` or `MISSING <ticket_id>`.
- `BUCKET_REPORT` prints seven lines in order using the exact shape `BUCKET i=<count>` for `i = 0..6`.
- `CATEGORY_REPORT` prints the exact eight summary lines shown in the reference block below.

Duplicate IDs and invalid pass types are rejected with these exact strings:

```text
ERROR duplicate ticket <ticket_id>
ERROR invalid pass_type <value>
```

Successful adds use this exact string:

```text
ADDED <ticket_id> BUCKET <bucket_index>
```

Lookup output is always this shape, with the trailing key names determined by the celebrity subtype:

```text
FOUND <ticket_id> | attendee=<attendee_name> | pass=<pass_type> | type=<Artist|VoiceActor|Singer|LiveActionActor> | celebrity=<celebrity_name> | <detail_key_1>=<value> | <detail_key_2>=<value>
```

The subtype detail keys must be exactly `fandom` and `commission_rate`, `signature_role` and `union_status`, `genre` and `chart_count`, or `franchise` and `stunt_team`.

Category reporting must use the most-selected celebrity as the favorite in each scope, break ties alphabetically, and use `Artist,VoiceActor,Singer,LiveActionActor` order when listing missing categories. The exact output shape is:

```text
TOTAL_TICKETS=<count>
VIP_TICKETS=<count>
ARTIST_COUNT=<count> FAVORITE=<celebrity_name_or_NONE>
VOICE_ACTOR_COUNT=<count> FAVORITE=<celebrity_name_or_NONE>
SINGER_COUNT=<count> FAVORITE=<celebrity_name_or_NONE>
LIVE_ACTION_COUNT=<count> FAVORITE=<celebrity_name_or_NONE>
OVERALL_FAVORITE=<celebrity_name_or_NONE>
MISSING_CATEGORIES=<comma_separated_labels_or_NONE>
```

Compile cleanly with `g++ -std=c++17 -Wall -Wextra -pedantic`, do not use `std::map`/`std::unordered_map` or any database library for the ticket store, and do not fake the linked-list requirement with a vector pretending to be buckets.
