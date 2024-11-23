from typing import Generator

from PIL import Image, ImageOps, ImageChops

import subprocess

from pathlib import Path

import ffmpeg

import numpy as np
from numpy.typing import NDArray, ArrayLike

def video_to_array(path: Path) -> NDArray[np.uint8]:
    # Shamelessly stolen from here:
    # https://github.com/kkroening/ffmpeg-python/blob/master/examples/README.md#convert-video-to-numpy-array
    probe = ffmpeg.probe(path)
    video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
    width = int(video_stream['width'])
    height = int(video_stream['height'])

    out, _ = (
        ffmpeg
        .input(path)
        .output('pipe:', format='rawvideo', pix_fmt='rgb24')
        .run(capture_stdout=True)
    )
    video = (
        np
        .frombuffer(out, np.uint8)
        .reshape([-1, height, width, 3])
    )

    return video

def ffmpeg_video_to_frames(video: Path, output_dir: Path) -> Generator[Path, None, None]:
    rtn = subprocess.run(['ffmpeg', '-i', str(video.absolute()), str((output_dir / r'%04d.png').absolute())])
    rtn.check_returncode()

    return output_dir.glob('*.png')

def to_grayscale(im: Image) -> Image:
    return im.convert('L')

def change_transparency(im: Image, percent=0.5) -> Image:
    r, g, b, alpha = im.convert('RGBA').split()
    alpha.point(lambda a: a * percent)
    return Image.merge('RGBA', (r, g, b, alpha))

def invert(im: Image) -> Image:
    return ImageOps.invert(Image.convert('RGB'))

def diff(im1: Image, im2: Image) -> Image:
    return ImageChops.difference(im1, im2)