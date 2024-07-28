"""
Classes representing a story feed, and the stories is contains.
"""

import requests
import tempfile
from io import BytesIO
from pathlib import Path
from typing import List
from PIL import Image
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip, ImageSequenceClip, CompositeVideoClip, CompositeAudioClip, transfx
from moviepy.video.VideoClip import VideoClip
from gtts import gTTS
from tools import pan_image, generate_audio, generate_summary, change_audio_speed, add_title
import concurrent.futures

WIPE_TIME = 1

class Entry:
    def __init__(self, title: str, text: str, image:str, url:str = None) -> None:
        """
        Create a new entry with a title, text, image, and optional URL.
        
        Args:
            title (str): The title of the entry.
            text (str): The text of the entry.
            image (str): The URL of the image for the entry.
            url (str): The URL of the entry.
        
        Returns:
            Entry: The new entry object
        """
        self.title: str = title
        self.text: str = text
        self.image: str = image
        self.url: str = url
        # The summary, generated from the text and the script of the video
        self.summary: str = None
        # The video file path
        self.video: str = None
        # self.categories: List[str] = categories
    
    def __str__(self):
        return f"{self.title}, {self.text}"

    def make_summary(self) -> str:
        """
        Generate a summary of the text.
        """
        self.summary = self.title + self.text
        return self.title + self.text
        # self.summary = generate_summary(self.text + self.title)
        return self.summary
    
    def generate_tts(self, dir: str) -> str:
        """
        Generate a text-to-speech audio file.
        """
        with tempfile.NamedTemporaryFile(dir=dir, suffix=".mp3", delete=False) as temp_file:
            speech_file_path = Path(temp_file.name)
            tts = gTTS(text=self.summary, lang='en')
            tts.save(speech_file_path)
            # generate_audio(speech_file_path, self.summary)
        return str(speech_file_path)
    
    def generate_visuals(self, duration: float, fps: int = 24) -> ImageClip:
        """
        Generate a visual representation of the text.
        """
        if self.image is None:
            raise ValueError("No image provided")
        img = Image.open(BytesIO(requests.get(self.image).content)).convert('RGB')
        frames = pan_image(img, duration=(duration + (WIPE_TIME * 2)), speed='slow', fps=fps)
        clip = ImageSequenceClip(frames, fps=fps)
        return clip
        return add_title(clip, self.title)

    def generate(self, dir: str, fps: int = 24) -> str:
        if self.summary is None:
            self.make_summary()
        if self.image is None:
            raise ValueError("No image provided")
        
        audio_path = self.generate_tts(dir)
        change_audio_speed(audio_path, 1.3)
        audio = AudioFileClip(audio_path)
        clip = self.generate_visuals(audio.duration)
        video = clip.set_audio(CompositeAudioClip([audio.set_start(WIPE_TIME)]))

        with tempfile.NamedTemporaryFile(dir="videos", suffix=".mp4", delete=False) as temp_file:
            video.write_videofile(
                temp_file.name, 
                codec='libx264', 
                fps=fps,
                preset="ultrafast",
            )
            self.video = temp_file.name

        return self.video

    def get_video(self, dir: str) -> ImageClip:
        if self.video is None:
            self.video = self.generate(dir)
        return self.video


class Feed:
    def __init__(self, title: str, entries: List[Entry] = []) -> None:
        self.title: str = title
        self.entries: List[Entry] = entries
    
    def __str__(self):
        return f"Feed: {self.title} with {len(self.entries)} entries\n\n" + "\n".join([str(entry) for entry in self.entries])
    
    def add_entry(self, entry: Entry) -> None:
        self.entries.append(entry)
    
    def get_videos(self) -> List[str]:
        """
        Get the video paths for all entries in the feed.
        
        Returns:
            List[str]: A list of video paths.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                clips = list(executor.map(lambda entry: entry.get_video(temp_dir), self.entries))
            return clips