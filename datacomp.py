"""
Author: Tomas Dal Farra
Date: 18/04/2023
Description: Video encoder for live-streaming
"""
import ffmpeg
from dataget import VideoGather


class StreamEncode:
    """ Encoding video stream from rawvideo rgb24 to libx264 h264 and from stdin to url """
    standard_url = 'pipe:'

    def __init__(self, width, height, url):
        """
        Gets settings for a ffmpeg subprocess to encode from rawvideo rgb24 to h264 for live-streaming
        :param width: video data width length
        :param height: video data height length
        :param url: location of the encoded data destination
        """
        self.width = width
        self.height = height
        self.url = url
        self.process = None

    def run_encoder(self):
        """ Invokes the ffmpeg subprocess with self settings """
        self.process = (
            ffmpeg
            .input(
                StreamEncode.standard_url, format='rawvideo', pix_fmt='rgb24',
                s=f'{self.width}x{self.height}'
            )
            .output(
                self.url,                                                       # output to url
                codec='libx264', format='h264', pix_fmt='yuv420p',              # encoding format
                tune='zerolatency', preset='ultrafast', crf='23',               # quality and speed to encode
            )
            # if url is stdout so it opens the pipe
            .run_async(pipe_stdin=True, pipe_stdout=(StreamEncode.standard_url == self.url))
        )

    def write_stdin(self, data):
        """
         Writes data to stdin
        :param data: input data for stdin
        """
        self.process.stdin.write(data)

    def close(self):
        """ Closes the ffmpeg process """
        self.process.stdin.close()
        if self.url == StreamEncode.standard_url:
            self.process.stdout.close()
        self.process.kill()


class ScreenEncode(StreamEncode):
    """ Encoding screenshots stream from rawvideo rgb24 to libx264 h264 and from stdin to stdout """

    def __init__(self, url):
        """
        Set settings for a ffmpeg subprocess to encode from rawvideo rgb24 to h264 for live-streaming
        Specifically made for screen sharing
        :param url: location of the encoded frames destination
        """
        self.camera = VideoGather()
        width = self.camera.monitor['width']
        height = self.camera.monitor['height']
        super().__init__(width, height, url)

    def capture(self):
        """ Captures screen and sends it to ffmpeg through stdin """
        self.write_stdin(self.camera.get_frame())


class StreamDecode:
    """ Decoding video stream from libx264 h264 to rawvideo rgb24 and from url to stdout """
    pass


def main():
    socket_url = "udp://127.0.0.1:5010"
    # socket_url = "udp://172.16.11.198:5010"
    encode = ScreenEncode(socket_url)
    encode.run_encoder()
    try:
        while True:
            encode.capture()
    finally:
        encode.close()


if __name__ == "__main__":
    main()
