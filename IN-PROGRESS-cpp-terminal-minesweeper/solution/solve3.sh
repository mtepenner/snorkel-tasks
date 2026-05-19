#!/bin/bash
cp /solution/client.cpp /app/workspace/src/client.cpp
g++ /app/workspace/src/client.cpp -o /app/workspace/client -lcurl `Magick++-config --cxxflags --libs`
echo -e "reveal 0 0\nreveal 2 2\nquit" | /app/workspace/client
ls /app/workspace/data/replays/*.png > /dev/null
