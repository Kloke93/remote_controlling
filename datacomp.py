"""
Author: Tomas Dal Farra
Date: 18/04/2023
Description: Video encoder for live-streaming
"""
import ffmpeg
from dataget import VideoGather

# socket_url = "udp://127.0.0.1:5010"
socket_url = "udp://172.16.11.198:5010"


class StreamEncode:
    """ Encoding video stream from rawvideo rgb24 to libx264 h264 and from stdin to stdout """
    def __init__(self, width, height):
        """
        Gets settings for a ffmpeg subprocess to encode from rawvideo rgb24 to h264 for live-streaming
        :param width: video data width length
        :param height: video data height length
        """
        self.width = width
        self.height = height
        self.process = None

    def run_encoder(self):
        """ Invokes the ffmpeg subprocess with self settings """
        self.process = (
            ffmpeg
            .input(
                'pipe:', format='rawvideo', pix_fmt='rgb24',
                s=f'{self.width}x{self.height}'
            )
            .output(
                'pipe:',                                                        # output to stdout
                codec='libx264', format='h264', pix_fmt='yuv420p',              # encoding format
                tune='zerolatency', preset='ultrafast', crf='23',               # quality and speed to encode
            )
            .run_async(pipe_stdin=True, pipe_stdout=True)
        )


class ScreenEncode(StreamEncode):
    """ Encoding screenshots stream from rawvideo rgb24 to libx264 h264 and from stdin to stdout """

    def __init__(self):
        """
        Set settings for a ffmpeg subprocess to encode from rawvideo rgb24 to h264 for live-streaming
        Specifically made for screen sharing
        """
        self.camera = VideoGather()
        width = self.camera.monitor['width']
        height = self.camera.monitor['height']
        super().__init__(width, height)


def main():
    encode = ScreenEncode()
    encode.run_encoder()
    try:
        while True:
            process.stdin.write(
                camera.get_frame()
            )
    finally:
        process.stdin.close()


if __name__ == "__main__":
    main()
