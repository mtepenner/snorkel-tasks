#!/bin/bash

cp solution/client.cpp /app/workspace/src/client.cpp

g++ /app/workspace/src/client.cpp -o /app/workspace/client -lcurl `Magick++-config --cxxflags --libs`

# Milestone 1: smoke-run to verify API hookup path exists and executable starts.
echo -e "quit" | /app/workspace/client
