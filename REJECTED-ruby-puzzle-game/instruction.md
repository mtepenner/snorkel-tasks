# [GAME-102] Terminal Logic Puzzle Game (Ruby)

**Description:**
Hey, I need a terminal-based logic puzzle game written in Ruby. Need it done quickly.

**AC:**
* Main script MUST be exactly at `/app/workspace/src/puzzle_game.rb`.
* Config data must be pulled from `/app/workspace/environment/puzzles.json` wait no, actually the instructions say `/app/puzzles.json`.
* `puzzles.json` structure: array of objects. Each object = a puzzle (fields: `title`, array of `clues`, `items` grouped by category like "Pastries", and `solution` mapping a person's name to the item).
* Code must be strictly OOP. Clean global namespace. Entire loop goes inside a `LogicGame` class, instantiated and run at the bottom of the script.

**UI/Prompt Strings (MUST BE EXACT FOR TESTS):**
1. On start: Print `Welcome to the Logic Grid Puzzle!` then `Loaded: <puzzle_title>`.
2. Interactive loop prompt: `Action (hint/solve/quit): ` (Make sure there's a space at the end!). 
   * Ignore invalid inputs and just show the prompt again silently.

**Game Logic:**
* Player starts with 100 points.
* **Hint:** Deduct 10 pts. Print `Hint: <first_clue_from_json>`.
* **Solve:** Prompt `Who bought the <target_item>? ` (where target_item is the LAST pastry in the array).
  * If right: Print `Correct!`, end loop, print `Game Over! Score: <final_score>`.
  * If wrong: Print `Incorrect!`, minus 20 pts, return to action prompt.
* **Quit:** Terminate cleanly, but still print `Game Over! Score: <final_score>` right before closing.

Tests are super flaky with string matching so please double-check the exact strings above. Thx!
