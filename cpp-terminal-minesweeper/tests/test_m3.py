import subprocess
import glob


def test_m3_imagemagick_metadata():
    # Milestone 3 must render PNG replay artifacts to the required directory.
    replays = glob.glob("/app/workspace/data/replays/*.png")
    assert len(replays) > 0, "No PNG replays found in /app/workspace/data/replays/"

    for replay in replays:
        # Ensure the file is a real board/replay image, not a trivial pixel.
        dimension_result = subprocess.run(
            ["identify", "-format", "%wx%h", replay],
            capture_output=True,
            text=True,
        )
        assert dimension_result.returncode == 0, f"Unable to inspect image dimensions: {replay}"
        width, height = [int(v) for v in dimension_result.stdout.strip().split("x")]
        assert width >= 16 and height >= 16, (
            f"Replay image is too small to represent a board: {replay} ({width}x{height})"
        )

        # Metadata must exist under the documented key and include useful fields.
        metadata_result = subprocess.run(
            ["identify", "-format", "%[Game-Metadata]", replay],
            capture_output=True,
            text=True,
        )
        metadata = metadata_result.stdout.strip()
        assert metadata != "", f"No metadata injected into {replay} under Game-Metadata"
        assert any(token in metadata.lower() for token in ["board", "move", "mine", "status"]), (
            f"Metadata is present but not informative for replay validation: {replay} => {metadata}"
        )
