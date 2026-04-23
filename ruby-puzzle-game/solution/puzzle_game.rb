require 'json'

def main
  puts "Welcome to the Logic Grid Puzzle!"
  
  begin
    file = File.read("/app/puzzles.json")
    puzzles = JSON.parse(file)
  rescue Errno::ENOENT
    puts "Error: puzzles.json not found."
    exit(1)
  end

  puzzle = puzzles[0]
  puts "Loaded: #{puzzle['title']}"
  
  score = 100
  
  # Dynamically determine the question and answer from JSON
  pastries = puzzle['items']['Pastries']
  target_item = pastries.last
  target_person = puzzle['solution'].key(target_item)
  
  loop do
    print "Action (hint/solve/quit): "
    STDOUT.flush 
    
    cmd = gets&.strip&.downcase
    break if cmd == "quit" || cmd.nil?
    
    if cmd == "hint"
      puts "Hint: #{puzzle['clues'][0]}"
      score -= 10
    elsif cmd == "solve"
      print "Who bought the #{target_item}? "
      STDOUT.flush
      
      ans = gets&.strip
      if ans&.downcase == target_person.downcase
        puts "Correct!"
        break
      else
        puts "Incorrect!"
        score -= 20
      end
    end
  end

  puts "Game Over! Score: #{score}"
end

main if __FILE__ == $PROGRAM_NAME