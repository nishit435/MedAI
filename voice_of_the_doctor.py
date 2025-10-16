"""Voice output utilities: Google Text-to-Speech (gTTS) with cross-platform playback."""

import platform
import subprocess
from typing import Optional
from gtts import gTTS

def _play_mp3(filepath: str) -> None:
    """Best-effort MP3 playback that works across OSes without requiring WAV conversion."""
    system = platform.system()
    try:
        if system == "Darwin":  # macOS
            subprocess.run(["afplay", filepath], check=False)
        elif system == "Linux":
            for cmd in (["ffplay", "-nodisp", "-autoexit", "-v", "quiet", filepath], 
                       ["mpg123", filepath], ["aplay", filepath]):
                try:
                    subprocess.run(cmd, check=True)
                    break
                except FileNotFoundError:
                    continue
        elif system == "Windows":
            try:
                subprocess.run(["ffplay", "-nodisp", "-autoexit", "-v", "quiet", filepath], check=True)
            except FileNotFoundError:
                subprocess.run(["powershell", "-c", f'Start-Process "{filepath}"'], check=False)
        else:
            print("Unsupported OS for automatic playback; file saved at", filepath)
    except Exception as e:
        print(f"Playback failed ({e}); file saved at {filepath}")

def text_to_speech_with_gtts(input_text: str, output_filepath: str, *, language: str = "en") -> str:
    """Generate speech via gTTS and play it. Returns the output file path."""
    tts = gTTS(text=input_text, lang=language, slow=False)
    tts.save(output_filepath)
    _play_mp3(output_filepath)
    return output_filepath