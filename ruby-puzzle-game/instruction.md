Let’s build a logic puzzle interactive terminal game in Ruby revolving around solving a variety of logic grid puzzles. It needs to be set up in this exact directory: /app/workspace/src/puzzle_game.rb. The puzzle configs are from /app/puzzles.json.

- the game prints "Welcome to the Logic Grid Puzzle!"  
- the first puzzle should get loaded from the JSON and print out "Loaded: <title>" (e.g., "Loaded: The Bakery Mix-up").  
- an input prompt worded as "Action (hint/solve/quit):".  The user asking for hints will result in points getting deducted by 10 per hint request (initially at 100 points), and "Hint: <first_clue>" will print out.  
- The user typing in solve will prompt the user dynamically with the last pastry item in the JSON (e.g., "Who bought the Tart? ").  
- if the user answers correctly, the game will print "Correct!", the final score is printed as "Game Over! Score: <final_score>" with the loop being broken.  Otherwise, print "Incorrect!", subtract 20 points, and return the user to the action prompt.
- if the user types 'quit' then the game loop must be exited immediately and terminate the program cleanly, printing the final score ("Game Over! Score: <final_score>") before exiting.