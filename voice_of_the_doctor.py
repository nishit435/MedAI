"""Voice output utilities: gTTS & ElevenLabs with cross-platform playback.

Replaces the previous SoundPlayer-based Windows approach (which only supports WAV) with
MP3-capable strategies. Attempts ffplay/afplay where available; falls back to default app.
"""

from dotenv import load_dotenv
import os
import platform
import subprocess
from typing import Optional

from gtts import gTTS
import elevenlabs
from elevenlabs.client import ElevenLabs
from elevenlabs.core.api_error import ApiError as ElevenLabsApiError

load_dotenv()

ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
if not ELEVEN_API_KEY:
    raise RuntimeError("ELEVEN_API_KEY not set. Add it to your environment or .env file.")

DEFAULT_ELEVEN_VOICE = "Aria"
ELEVEN_FALLBACK_VOICE = "Rachel"


def _play_mp3(filepath: str) -> None:
    """Best-effort MP3 playback that works across OSes without requiring WAV conversion."""
    system = platform.system()
    try:
        if system == "Darwin":  # macOS
            subprocess.run(["afplay", filepath], check=False)
        elif system == "Linux":
            # Prefer ffplay if available (silent), else try mpg123/aplay
            for cmd in (["ffplay", "-nodisp", "-autoexit", "-v", "quiet", filepath], ["mpg123", filepath], ["aplay", filepath]):
                try:
                    subprocess.run(cmd, check=True)
                    break
                except FileNotFoundError:
                    continue
        elif system == "Windows":
            # Try ffplay first if present
            try:
                subprocess.run(["ffplay", "-nodisp", "-autoexit", "-v", "quiet", filepath], check=True)
            except FileNotFoundError:
                # Fallback: open with default associated app (non-blocking)
                subprocess.run(["powershell", "-c", f'Start-Process "{filepath}"'], check=False)
        else:
            print("Unsupported OS for automatic playback; file saved at", filepath)
    except Exception as e:  # noqa: BLE001 - broad for playback resiliency
        print(f"Playback failed ({e}); file saved at {filepath}")


def text_to_speech_with_gtts(input_text: str, output_filepath: str, *, language: str = "en") -> str:
    """Generate speech via gTTS and play it. Returns the output file path."""
    tts = gTTS(text=input_text, lang=language, slow=False)
    tts.save(output_filepath)
    _play_mp3(output_filepath)
    return output_filepath


def text_to_speech_with_elevenlabs(
    input_text: str,
    output_filepath: str,
    *,
    voice: Optional[str] = None,
    model: str = "eleven_turbo_v2",
) -> str:
    """Generate speech via ElevenLabs with fallback voice if permissions/voice issues occur.

    Returns the output file path.
    """
    chosen_voice = voice or DEFAULT_ELEVEN_VOICE
    client = ElevenLabs(api_key=ELEVEN_API_KEY)
    try:
        audio = client.generate(
            text=input_text,
            voice=chosen_voice,
            output_format="mp3_22050_32",
            model=model,
        )
    except ElevenLabsApiError as e:
        print(f"Primary voice '{chosen_voice}' failed ({e}); retrying with '{ELEVEN_FALLBACK_VOICE}'.")
        audio = client.generate(
            text=input_text,
            voice=ELEVEN_FALLBACK_VOICE,
            output_format="mp3_22050_32",
            model=model,
        )

    elevenlabs.save(audio, output_filepath)
    _play_mp3(output_filepath)
    return output_filepath
