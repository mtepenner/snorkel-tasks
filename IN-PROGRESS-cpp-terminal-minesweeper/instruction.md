Build a C++ client for a Minesweeper game that communicates with a local REST API backend. The backend handles game logic, so you'll focus purely on the client implementation: taking player input, calling the API, and generating replay files.

API Contract

- GET `http://localhost:8080/board` → Returns `{"status":"ok", "mines":10, "board_state":"hidden"}`
- POST `http://localhost:8080/move` → Accepts `{"x":integer, "y":integer, "action":"reveal"}` → Returns `{"status":"cleared"}`

Implementation Requirements

- Source file: Place your C++ client at `/app/workspace/src/client.cpp`
- Compiled binary: Must compile to `/app/workspace/client`
- Compilation flags: Include `-lcurl` for HTTP requests and ImageMagick (`Magick++`) for image generationW
- Input protocol: Read line-based stdin commands: `reveal X Y` and `quit`
- Output: Generate PNG replay files in `/app/workspace/data/replays/` (create if missing) with ImageMagick metadata key `Game-Metadata` containing game context
- Backend: Do not modify the backend API or game logic—it's off-limits
