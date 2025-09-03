import speech_recognition as sr
from pydub import AudioSegment

print("🎙️ Speak something... (5 seconds limit)")

recognizer = sr.Recognizer()
with sr.Microphone() as source:
    audio = recognizer.listen(source, phrase_time_limit=5)

# Save raw WAV to check microphone
with open("test.wav", "wb") as f:
    f.write(audio.get_wav_data())

print("✅ Recorded to test.wav")

# Convert to MP3 using pydub + ffmpeg
sound = AudioSegment.from_wav("test.wav")
sound.export("test.mp3", format="mp3")
print("✅ Converted to test.mp3")
