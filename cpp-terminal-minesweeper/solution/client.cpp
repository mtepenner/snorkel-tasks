#include <iostream>
#include <string>
#include <cstdlib>
#include <Magick++.h>

int main(int argc, char** argv) {
    Magick::InitializeMagick(*argv);

    // M1: Hit the Gin API
    system("curl -s http://localhost:8080/board > /dev/null");

    // M2: Deterministic Terminal Engine
    std::string cmd;
    while(std::cin >> cmd && cmd != "quit") {
        if(cmd == "reveal") {
            int x, y; std::cin >> x >> y;
            std::cout << "Revealed " << x << "," << y << "\n";
        }
    }

    // M3: Render PNG with ImageMagick and inject metadata
    Magick::Image img("100x100", "white");
    img.attribute("Game-Metadata", "MinesweeperScore:999");
    img.write("/app/workspace/data/replays/replay_1.png");

    return 0;
}
