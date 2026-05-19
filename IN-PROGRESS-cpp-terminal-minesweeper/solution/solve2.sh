#!/bin/bash
cp /solution/client.cpp /app/workspace/src/client.cpp
g++ /app/workspace/src/client.cpp -o /app/workspace/client -lcurl `Magick++-config --cxxflags --libs`
echo -e "reveal 0 0\nreveal 1 1\nquit" | /app/workspace/client
