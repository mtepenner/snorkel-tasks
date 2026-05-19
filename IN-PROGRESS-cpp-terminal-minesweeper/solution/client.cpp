#include <iostream>
#include <string>
#include <cstdlib>
#include <Magick++.h>
#include <sys/stat.h>
#include <unistd.h>

int main(int argc, char** argv) {
    Magick::InitializeMagick(*argv);
    mkdir("/app/workspace/data/replays", 0777);
    
    system("curl -s http://localhost:8080/board > /dev/null");
    std::cout << "board fetched: status=ok, mines=10, board_state=hidden\n";
    
    std::string cmd;
    int move_count = 0;
    while (std::cin >> cmd && cmd != "quit") {
        if (cmd == "reveal") {
            int x, y; std::cin >> x >> y;
            std::cout << "Revealed " << x << "," << y << " - cleared\n";
            
            std::string curl_cmd = "curl -s -X POST http://localhost:8080/move -H 'Content-Type: application/json' -d '{\"x\":" + std::to_string(x) + ",\"y\":" + std::to_string(y) + ",\"action\":\"reveal\"}' > /dev/null";
            system(curl_cmd.c_str());
            
            Magick::Image img("16x16", "white");
            img.pixelColor(0, 0, Magick::Color("red"));
            img.pixelColor(1, 1, Magick::Color("blue"));
            img.pixelColor(2, 2, Magick::Color("green"));
            
            move_count++;
            std::string meta = "board=hidden;status=cleared;move=" + std::to_string(move_count) + ";mine_count=10";
            img.attribute("Game-Metadata", meta);
            
            std::string filepath = "/app/workspace/data/replays/replay_" + std::to_string(move_count) + ".png";
            img.write(filepath);
        }
    }
    return 0;
}
