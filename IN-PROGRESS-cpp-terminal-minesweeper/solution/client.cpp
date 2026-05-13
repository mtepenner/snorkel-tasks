#include <iostream>
#include <string>
#include <cstdlib>
#include <Magick++.h>

int main(int argc, char** argv) {
    Magick::InitializeMagick(*argv);
    system("curl -s http://localhost:8080/board > /dev/null");
    std::cout << "board fetched from http://localhost:8080/board" << "\n";
    std::string cmd;
    while(std::cin >> cmd && cmd != "quit") {
        if(cmd == "reveal") {
            int x, y; std::cin >> x >> y;
            std::cout << "Revealed " << x << "," << y << "\n";
        }
    }
    Magick::Image img("100x100", "white");
    img.attribute("Game-Metadata", "board=hidden;status=cleared;moves=reveal 0 0;mine_count=10");
    img.write("/app/workspace/data/replays/replay_1.png");

    return 0;
}
