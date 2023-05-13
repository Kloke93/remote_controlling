"""
Author: Tomas Dal Farra
Date: 18/04/2023
Description: Video encoder for live-streaming
"""
import ffmpeg

# uses pipe stdin, codec is libx264 and outputs to socket
process = (
    ffmpeg
    .input('pipe:', codec='libx264')
    .output()
)


if __name__ == "__main__":
    pass
