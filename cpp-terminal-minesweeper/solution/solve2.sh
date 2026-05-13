#!/bin/bash

cp solution/client.cpp /app/workspace/src/client.cpp

g++ /app/workspace/src/client.cpp -o /app/workspace/client -lcurl `Magick++-config --cxxflags --libs`

# Milestone 2: deterministic scripted play path.
echo -e "reveal 0 0\nquit" | /app/workspace/client
