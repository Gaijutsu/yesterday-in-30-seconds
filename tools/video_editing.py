from PIL import Image
from typing import List
import numpy as np
import ffmpeg
import tempfile
import os
from moviepy.editor import TextClip, CompositeVideoClip, VideoClip
from moviepy.config import change_settings

change_settings({"IMAGEMAGICK_BINARY": r"./magick"})

def pan_image(image, output_width: int = 1080, output_height: int = 1920, duration: float = 10, speed = 'slow', fps: int = 24) -> List[np.array]:
    """
    Pan an image horizontally to create a video effect.
    
    Args:
        image (PIL.Image): The input image to pan.
        output_width (int): The width of the output frames.
        output_height (int): The height of the output frames.
        duration (float): The duration of the panning effect in seconds.
        speed (str): The speed of the panning effect ('slow', 'medium', 'fast').
        fps (int): The frames per second of the output video.
    """
    # Resize the image to maintain aspect ratio and match the desired height
    new_height = int((output_height / image.height) * image.height)
    new_width = int((output_height / image.height) * image.width)
    
    image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Calculate the total number of frames based on duration and fps
    num_frames = int(duration * fps)
    
    # Calculate the total width that needs to be panned. Pan starts 1/3 into the image and ends 2/3 into the image
    total_width_to_pan = (new_width - output_width) * (1/3)
    
    # Calculate the maximum pixel shift per frame to finish exactly at the end of the duration
    if total_width_to_pan > 0:
        max_pixel_shift_per_frame = total_width_to_pan / num_frames
    else:
        max_pixel_shift_per_frame = 0  # No panning needed if the image is not wide enough
    
    # Define speeds as multipliers of the maximum shift
    speed_multipliers = {'slow': 0.5, 'medium': 0.75, 'fast': 1.0}
    multiplier = speed_multipliers.get(speed, 0.5)
    pixel_shift_per_frame = max(1, int(max_pixel_shift_per_frame * multiplier))

    frames = []
    current_x = (new_width - output_width) / 3  # Start 1/3 into the image
    for _ in range(num_frames):
        if current_x + output_width > new_width:
            # Stop if panning goes beyond the image width
            break
        crop_area = (current_x, 0, current_x + output_width, output_height)
        cropped_img = image.crop(crop_area)
        frames.append(cropped_img)
        current_x += pixel_shift_per_frame  # Move the crop area to the right each frame

    return [np.array(frame) for frame in frames]

def add_title(clip: VideoClip, title: str, fontsize: int = 50, color: str = 'white') -> CompositeVideoClip:
    """
    Add a title overlay to a video clip.
    
    Args:
        clip (ImageClip): The input video clip.
        title (str): The title text to display.
        font (str): The font to use for the title.
        fontsize (int): The font size for the title.
        color (str): The color of the title text.
        position (str): The position of the title ('top' or 'bottom').
    """
    txt_clip = TextClip(title, fontsize=fontsize, font="DejaVu-Sans-Mono-Oblique", color=color)
    # Set the position of the text outside the left side of the image initially
    txt_clip = txt_clip.set_position(('left', 'bottom'))
    # Set the duration of the text animation (you can adjust the duration as needed)
    txt_clip = txt_clip.set_duration(clip.duration)

    return CompositeVideoClip([clip, txt_clip.set_start(0)])

def change_audio_speed(audio_path, speed):
    """
    Changes the playback speed of an audio file.

    Args:
        input_file (str): Path to the input MP3 file.
        output_file (str): Path to the output MP3 file.
        speed (float): Speed factor where >1 is faster and <1 is slower.
    """
    # Define the filter for audio tempo change
    audio_filter = ffmpeg.input(audio_path).audio.filter('atempo', speed)
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
        # Output configuration, can overwrite the file
        ffmpeg.output(audio_filter, temp_file.name, acodec='libmp3lame').overwrite_output().run()
        os.replace(temp_file.name, audio_path)