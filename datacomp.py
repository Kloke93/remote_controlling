"""
Author: Tomas Dal Farra
Date: 18/04/2023
Description: Video encoder/decoder for live-streaming
"""
import ffmpeg
from dataget import VideoGather


class StreamEncode:
    """ Encoding video stream from rawvideo rgb24 to libx264 h264 and from stdin to url """
    standard_url = 'pipe:'          # standard url of the input for the subprocess

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
        camera = VideoGather()
        width = camera.monitor['width']
        height = camera.monitor['height']
        super().__init__(width, height, url)
        self.camera = camera

    def capture(self):
        """ Captures screen and sends it to ffmpeg through stdin """
        self.write_stdin(self.camera.get_frame())

    def close(self):
        """ Closes the ffmpeg process and mss clean up """
        super().close()
        self.camera.close()


class StreamDecode:
    """ Decoding video stream from libx264 h264 to rawvideo rgb24 and from url to stdout """
    standard_url = 'pipe:'  # standard url of the input for the subprocess

    def __init__(self, width, height, url):
        """
        Gets settings for a ffmpeg subprocess to decode from libx264 h264 to rawvideo rgb24 for live-streaming
        :param width: video data width length
        :param height: video data height length
        :param url: location of the encoded data source
        """
        self.width = width
        self.height = height
        self.url = url
        self.process = None

    def run_decoder(self):
        """ Invokes the ffmpeg subprocess with self settings """
        self.process = (
            ffmpeg
            .input(
                self.url, format='h264'
            )
            .output(
                'pipe:',  # output to stdout
                format='rawvideo', pix_fmt='rgb24',                 # decoding format
                tune='zerolatency', preset='ultrafast', crf='23',   # quality and speed to encode
                s=f'{self.width}x{self.height}'
            )
            # if url is stdout so it opens the pipe
            .run_async(pipe_stdin=(StreamDecode.standard_url == self.url), pipe_stdout=True)
        )

    def read_stdout(self):
        """
        Writes from stdout rgb width * height
        """
        return self.process.stdout.read(self.width * self.height * 3)

    def close(self):
        """ Closes the ffmpeg process """
        self.process.stdout.close()
        if self.url == StreamEncode.standard_url:
            self.process.stdin.close()
        self.process.kill()


def main():
    socket_url = "udp://127.0.0.1:5010"
    # socket_url = "udp://172.16.11.198:5010"
    encoder = ScreenEncode(socket_url)
    encoder.run_encoder()
    try:
        while True:
            encoder.capture()
    finally:
        encoder.close()


if __name__ == "__main__":
    main()
