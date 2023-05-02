"""
Author: Tomas Dal Farra
Date: 18/04/2023
Description: Video encoder for live-streaming
"""
import ffmpeg

# use pipe stdin and output to socket
process = (
    ffmpeg
    .input('pipe:')
)


if __name__ == "__main__":
    pass
