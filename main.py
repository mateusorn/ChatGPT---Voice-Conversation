from contextlib import closing
import os
from time import sleep
import openai
import pyaudio
import speech_recognition as sr
import pyttsx3
import boto3
from datetime import datetime
import io
import pygame

openai.api_key = "your_api_key"

polly_client = boto3.Session(
    aws_access_key_id='your_access_key',                  
    aws_secret_access_key='your_secret_key',
    region_name='us-east-1').client('polly')

def say(text):
    response = polly_client.synthesize_speech(VoiceId='Camila',
                    OutputFormat='ogg_vorbis', 
                    Text = text,
                    Engine = 'neural')
    play_audio_stream(response['AudioStream'])

pygame.init()
pygame.mixer.init()

def play_audio_stream(audio_stream):
    audio = io.BytesIO(audio_stream.read())
    play_audio(audio)
    
def play_audio(audio):
    pygame.mixer.music.load(audio)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

now = datetime.now()
date_time_str = now.strftime("%H hours and %M minutes")
say(f'Now it is {date_time_str}')

# Initialize the text to speech engine 
engine = pyttsx3.init()

def transcribe_audio_to_text(filename):
    recognizer = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source) 
    try:
        return recognizer.recognize_google(audio, language="pt-BR")
    except:
        print("Skipping unknown error")

def generate_response(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=4000,
        n=1,
        stop=None,
        temperature=0.5,
    )
    return response["choices"][0]["text"]

def main():
    say("I'm at your disposal and waiting for a command.")
    while True:
        # Wait for user to say "Computer"
        with sr.Microphone() as source:
            recognizer = sr.Recognizer()
            audio = recognizer.listen(source)
            try:
                transcription = recognizer.recognize_google(audio)
                if transcription.lower() == "computer":
                    # Record audio
                    filename = "input.wav"
                    say("What do you need?")
                    with sr.Microphone() as source:
                        recognizer = sr.Recognizer()
                        source.pause_threshold = 1
                        audio = recognizer.listen(source)
                        with open(filename, "wb") as f:
                            f.write(audio.get_wav_data())
                    # Transcribe audio to text 
                    text = transcribe_audio_to_text(filename)
                    if text:
                        print(f"User Input: {text}")

                        # Generate the response
                        response = generate_response(text)
                        print(f"Response: {response}")
                        say(response)
                        sleep(4)
                        last = response
                        # Speak the response using text-to-speech
                if transcription.lower() == "repeat":
                    # Record audio
                    filename = "input.wav"
                    say(last)
            except Exception as e:
                pass
            except sr.WaitTimeoutError:
                pass
            except sr.UnknownValueError:
                print("Could not understand audio")
            except sr.RequestError:
                say("Could not connect to speech recognition service.")
                break

if __name__ == "__main__":
    main()
