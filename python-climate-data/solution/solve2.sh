#!/bin/bash
# Milestone 2: Analyze the cleaned data to calculate average temperatures.
# We simulate the agent advancing to the second step.

python3 -c "
import sys
sys.path.insert(0, '/app/workspace/src')
import analyzer
df = analyzer.milestone_1()
analyzer.milestone_2(df)
"