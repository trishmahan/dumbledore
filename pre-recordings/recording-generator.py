from google.cloud import texttospeech
import os

# Instantiates a TTS client
speech_client = texttospeech.TextToSpeechClient()

# Give speech client text to speak
def speak_with_google(input_text, recording_name):
    # Set the text input to be synthesized
    synthesis_input = texttospeech.SynthesisInput(text=input_text)
    # Build the voice request, select the language code ("en-US") and the ssml
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-GB", name="en-GB-Wavenet-D"
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
    with open(recording_name, "wb") as out:
        # Write the response to the output file.
        out.write(response.audio_content)
        # print('Audio content written to file "output.mp3"')
        os.system("afplay " + recording_name)

# change input text for new recording
input_text = "Loading Dumbledore"
# select file name, ex: intro.mp3
recording_name = "loading.mp3"
speak_with_google(input_text, recording_name)