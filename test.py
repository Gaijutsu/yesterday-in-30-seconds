import feedparser
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip
from PIL import Image
import requests
from io import BytesIO
from pathlib import Path
from openai import OpenAI

from api_secrets import API_KEY

client = OpenAI(api_key=API_KEY)

# Step 1: Fetch the RSS feed
def fetch_feed(url):
    return feedparser.parse(url)

# Step 2: Extract summary and images
def extract_content(entries):
    contents = []
    for entry in entries:
        title = entry.title
        summary = entry.summary#.split(".")[0] + "."  # Simple summary extraction
        image_url = entry.media_content[0]['url'] if 'media_content' in entry else None
        contents.append((title + "\n" + summary, image_url))
    return contents

# Step 3: Download images and resize
def download_image(url):
    if url:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        img = img.convert('RGB')  # Convert to RGB mode
        img = img.resize((1920, 1080))  # Resize for video standard
        return img

# Step 4: Convert summary to speech
def text_to_speech(text, lang='en'):
    speech_file_path = Path(__file__).parent / f"{text[:5]}.mp3"
    with client.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice="shimmer",
        input=text,
    ) as response:
        response.stream_to_file(speech_file_path)
    return str(speech_file_path)

# Step 5: Create video clip
def create_video_clip(image, audio, duration=6):
    audio_clip = AudioFileClip(audio)#.set_duration(duration)
    clip = ImageClip(image).set_duration(audio_clip.duration)
    clip = clip.set_audio(audio_clip)
    return clip

# Main function to orchestrate the video creation
def main():
    url = 'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml'
    feed = fetch_feed(url)
    contents = extract_content(feed.entries[:5])  # Process only the first 5 entries for brevity

    clips = []
    for summary, image_url in contents:
        img = download_image(image_url)
        if img:
            img.save("temp.jpg")
            audio_file = text_to_speech(summary)
            clip = create_video_clip("temp.jpg", audio_file)
            clips.append(clip)

    final_clip = concatenate_videoclips(clips, method='compose')
    final_clip.write_videofile("final_video.mp4", codec='libx264', fps=30)

if __name__ == "__main__":
    main()
