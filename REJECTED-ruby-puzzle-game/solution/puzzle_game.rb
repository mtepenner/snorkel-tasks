require 'json'

class LogicGame
  def initialize(config_path)
    @config_path = config_path
    @score = 100
  end

  def run
    puts "Welcome to the Logic Grid Puzzle!"
    
    begin
      file = File.read(@config_path)
      puzzles = JSON.parse(file)
    rescue Errno::ENOENT
      puts "Error: puzzles.json not found."
      return
    end

    # Load the first puzzle
    puzzle = puzzles.first
    puts "Loaded: #{puzzle['title']}"
    
    # Dynamically determine the question and answer from the JSON
    target_item = puzzle['items']['Pastries'].last
    correct_person = puzzle['solution'].key(target_item)
    
    loop do
      print "Action (hint/solve/quit): "
      STDOUT.flush 
      
      input = gets
      break if input.nil? # Handle EOF cleanly
      
      command = input.strip.downcase
      
      case command
      when "hint"
        @score -= 10
        puts "Hint: #{puzzle['clues'].first}"
        
      when "solve"
        print "Who bought the #{target_item}? "
        STDOUT.flush
        
        answer = gets&.strip
        if answer&.downcase == correct_person.downcase
          puts "Correct!"
          break
        else
          puts "Incorrect!"
          @score -= 20
        end
        
      when "quit"
        break
        
      else
        # Silently ignore unrecognised input; the loop will naturally re-prompt
      end
    end

    # This handles printing the score on both a 'solve' win and a 'quit'
    puts "Game Over! Score: #{@score}"
  end
end

# Instantiate and run at the very bottom, keeping the global namespace clean
if __FILE__ == $PROGRAM_NAME
  app = LogicGame.new("/app/puzzles.json")
  app.run
end
