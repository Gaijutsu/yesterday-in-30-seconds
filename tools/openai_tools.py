from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def generate_audio(speech_file_path: str, text: str):
    with client.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice="shimmer",
        input=text
    ) as response:
        response.stream_to_file(speech_file_path)

def generate_summary(text: str):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You a newscaster AI that takes a headline and article description and creates an extractive 1 sentence summary."},
            {"role": "user", "content": text}
        ],
        max_tokens=256
    )
    return response.choices[0].message.content