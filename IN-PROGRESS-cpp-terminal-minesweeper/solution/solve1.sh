#!/bin/bash
cp /solution/client.cpp /app/workspace/src/client.cpp
g++ /app/workspace/src/client.cpp -o /app/workspace/client -lcurl `Magick++-config --cxxflags --libs`
echo -e "quit" | /app/workspace/client
