# tool box
import speech_recognition as sr
import pyttsx3
import datetime
import wikipedia
import webbrowser
import os
import time
import subprocess
# from ecapture import ecapture as ec
import wolframalpha
import json
import requests
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from numpy import random
from google.cloud import texttospeech
## -- load weather api key
from dotenv import load_dotenv
from pathlib import Path  # Python 3.6+ only
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
load_dotenv()
weather_key = os.getenv("WEATHER")
## -- need to create through google cloud services
google_env = os.getenv("GOOGLE")
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = google_env

# Instantiates a TTS client
speech_client = texttospeech.TextToSpeechClient()

#### BUILD "OPEN {Application}" SKILLS INDEX ####
d = '/Applications'
records = []
apps = os.listdir(d)
for app in apps:
    record = {}
    record['voice_command'] = 'open ' + app.split('.app')[0]
    record['sys_command'] = 'open ' + d +'/%s' %app.replace(' ','\ ')
    records.append(record)
es = Elasticsearch(['localhost:9200'])
bulk(es, records, index='mac_apps', raise_on_error=True) #doc_type='text', 
def search_index(query):
    res = es.search(index="mac_apps", body={    #doc_type='text',                   
    "query" :{
        "match": {
            "voice_command": {
                "query": query,
                "fuzziness": 2
            }
            }
        },
    })
    return res['hits']['hits'][0]['_source']['sys_command']

# Give speech client text to speak
def speak_with_google(input_text):
    # Set the text input to be synthesized
    synthesis_input = texttospeech.SynthesisInput(text=input_text)
    # Build the voice request, select the language code ("en-US") and the ssml
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-GB", name="en-GB-Wavenet-D"#, ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )
    # Select the type of audio file you want returned
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = speech_client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    # The response's audio_content is binary.
    with open("output.mp3", "wb") as out:
        # Write the response to the output file.
        out.write(response.audio_content)
        # print('Audio content written to file "output.mp3"')
        os.system("afplay output.mp3")

#### TODO - LIMIT API CALLS with pre-recordings
# def speak_with_recording(recording_name):
#     os.system("afplay " + recording_name)

### BAD VOICE
# print("Loading your AI personal assistant Dumbledore")
# # create voice engine
# engine = pyttsx3.init()
# rate = engine.getProperty('rate')
# engine.setProperty('rate', 160)
# voices = engine.getProperty('voices')
# engine.setProperty('voice', voices[7].id)

dumbledoreQuotes = ["It does not do... to dwell on dreams... and forget to live", 
        "Happiness can be found, even in the darkest of times, if one only remembers to turn on the light.",  
        "We must all face the choice between... what is right... and what is easy", 
        "It is our choices that show what we truly are, far more than our abilities", 
        "Words are, in my not-so-humble opinion, our most inexhaustible source of magic, capable of both inflicting injury and remedying it", 
        "Do not pity the dead, Harry, pity the living, and above all, those who live without love", 
        "It matter not what someone is born but what they grow to be", 
        "For in dreams, we enter a world that is entirely our own, let them swim in the deepest ocean, or glide over the highest cloud", 
        "It is the unknown we fear when we look upon death and darkness. Nothing more",
        "After all, to the well organized mind, death is but the next great adventure",
        "It takes a great deal of bravery to stand up to our enemies, but just as much to stand up to our friends"]

## time of day greeting of user
def greetUser(name):
    hour = datetime.datetime.now().hour
    greeting = "Hello, " + name + "."
    if hour >= 0 and hour < 12:
        greeting += " Good Morning"
    elif hour >= 12 and hour < 18:
        greeting += " Good Afternoon"
    else:
         greeting += " Good Evening"
    greeting += ", how can I help you"
    speak_with_google(greeting)

## listener
def takeCommand(pause):
    if pause == 0:
        pause == 5
    r = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        r.adjust_for_ambient_noise(source)
        print("Listening...")
        audio = r.listen(source)#, timeout=5, phrase_time_limit=6)
        try:
            statement = r.recognize_google(audio)
            print("user said: " + statement)
            return statement
        except LookupError:
            speak_with_google("Excuse me, will you please repeat that?")
            return "None"
        return statement

## kelvin to farenheit... cause openweathermap
def convertKtoF(temp):
    temp = temp * 9 / 5
    temp = temp - 459.67
    temp = round(temp, 1)
    return str(temp)

## warm up voice
speak_with_google("Loading Dumbledore")

## begin "program"
if __name__ == '__main__':
    name = ""
    ## ask for name in order to greet
    while name == "":
        speak_with_google("Hello, what is your name")
        name = takeCommand(5).lower()
        greetUser(name)
    ## command loop
    while True:
        statement = takeCommand(3).lower()
        if statement == 0:
            continue
        if "good bye" in statement or "ok bye" in statement or "stop" in statement:
            speak_with_google("Shutting down now, Good bye!")
            break
    ###### SKILLS SECTION ######
        if "tell me something" in statement or "say something" in statement or "i don't know" in statement:
            speak_with_google(dumbledoreQuotes[random.randint(len(dumbledoreQuotes))])
        elif "wikipedia" in statement:
            speak_with_google('Searching Wikipedia...')
            statement = statement.replace("wikipedia", "")
            if statement != "":
                results = wikipedia.summary(statement, sentences = 3)
                speak_with_google("According to Wikipedia...")
                print(results)
                #### TODO Parse Results Better...
                speak_with_google(results)
            else: speak_with_google("I'm sorry, could you repeat that?")
        elif "time" in statement:
            time_str = datetime.datetime.now().strftime("%H:%M")
            response = "the time is " + time_str
            speak_with_google(response)
        elif "who made you" in statement or "who created you" in statement:
            print(name)
            if name == "trish":
                speak_with_google("Well, my parents are Percival and Kendra. My hard work and practice made me the wizard I was. My defeat of Grindelwald made me famous. And, you, programmed me into this MacBook")
            else:
                speak_with_google("Well, my parents are Percival and Kendra. My hard work and practice made me the wizard I was. My defeat of Grindelwald made me famous. And Trish programmed me into this MacBook")
        ### want to migrate this list later, and key some of these conditionals off of
        elif "what can I say" in statement or "what commands" in statement:
            commands = "Current commands include good bye, say something, wikipedia, time, who made you, and weather."
        elif "weather" in statement:
            ### TODO: get users location or ask user for weather stats
            base_url = "http://api.openweathermap.org/data/2.5/weather?"
            city_name = "4752255"
            complete_url = base_url + "appid=" + weather_key + "&id=" + city_name
            response = requests.get(complete_url)
            response_json = response.json()
            if response_json["cod"] == "404":
                txt_response = "The weather for " + city_name + " could not be found."
                speak_with_google(txt_response)
            else:
                y = response_json["main"]
                current_temp = y["temp"]
                current_temp = convertKtoF(current_temp)
                feels_like = y["feels_like"]
                feels_like = convertKtoF(feels_like)
                txt_response = "The temperature is " + str(current_temp) + ", though it feels like " + str(feels_like)
                speak_with_google(txt_response)
        elif "open" in statement:
            sys_command = search_index(statement)
            os.system(sys_command)
        else:
            speak_with_google("I'm sorry, could you repeat that?")
time.sleep(5)