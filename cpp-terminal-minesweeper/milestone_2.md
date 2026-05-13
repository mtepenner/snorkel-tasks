Milestone 2 is the terminal engine pass. Binary should be /app/workspace/client. Read commands from stdin line by line, not ncurses-only interactive input.

Required commands are reveal X Y and quit. It must handle scripted input like reveal 0 0 then quit, and print enough stdout so deterministic runs can be checked.
