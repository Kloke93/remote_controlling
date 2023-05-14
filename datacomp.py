"""
Author: Tomas Dal Farra
Date: 18/04/2023
Description: Video encoder for live-streaming
"""
import ffmpeg
from dataget import VideoGather


socket_url = "udp://127.0.0.1:5010"

# uses pipe stdin, codec is libx264 and outputs to socket
process = (
    ffmpeg
    .input('pipe:', format='rawvideo', pix_fmt='rgb24', s='1080x1920')
    .output(
        socket_url,
        codec='libx264',
        format='h264'
    )
    .run_async(pipe_stdin=True)
)


camera = VideoGather()
try:
    while True:
        process.stdin.write(
            camera.get_frame()
        )
finally:
    process.stdin.close()
