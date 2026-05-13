need a c++ client for minesweeper that talks to our local gin api. gin already handles the sessions and leaderboard stuff so please refrain from touching it or modifying that component in any way and the backend. if you could just drop the client code in /app/workspace/src/client.cpp.

for the api contract, use GET http://localhost:8080/board which returns json with status, mines, and board_state, and POST http://localhost:8080/move with json body {"x": integer, "y": integer, "action": "reveal"} which returns {"status":"cleared"}. compile the client binary to /app/workspace/client.

for command input, support line-based stdin commands in this format: reveal X Y and quit. also write replay png files to /app/workspace/data/replays/ (create the directory if missing) and inject metadata using the exact imagemagick key Game-Metadata with useful game context in the value.
