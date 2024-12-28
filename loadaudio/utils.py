from typing import Union, Any, Literal, Optional
from io import BytesIO
import os
import requests
import base64
import re
import uuid
from pydub import AudioSegment
import numpy as np
import tempfile

class AudioLoadingError(Exception):
    """Custom exception for audio loading related errors."""
    pass

def is_base64(sb: Union[str, bytes]) -> bool:
    """Checks if the input object is base64 encoded."""
    try:
        if isinstance(sb, str):
            sb = re.sub(r"^data:audio\/[a-zA-Z0-9]+;base64,", "", sb)
            sb_bytes = bytes(sb, "ascii")
        elif isinstance(sb, bytes):
            sb_bytes = sb
        else:
            return False  # Not a string or bytes, cannot be base64
        return base64.b64encode(base64.b64decode(sb_bytes)) == sb_bytes
    except Exception:
        return False

def _download_audio(url: str) -> Optional[AudioSegment]:
    """Downloads an audio file from a URL."""
    try:
        response = requests.get(url, timeout=10)  # Increased timeout
        response.raise_for_status()
        with BytesIO(response.content) as buffer:
            return AudioSegment.from_file(buffer)
    except requests.exceptions.RequestException as e:
        print(f"Error downloading audio from {url}: {e}")
        return None

def _load_from_base64(audio: str) -> AudioSegment:
    """Loads audio from a base64 string."""
    try:
        audio = re.sub(r"^data:audio\/[a-zA-Z0-9]+;base64,", "", audio)
        audio_bytes = base64.b64decode(audio)
        return AudioSegment.from_file(BytesIO(audio_bytes))
    except Exception as e:
        raise AudioLoadingError(f"Error loading audio from base64: {e}")

def _load_from_file(file_path: str) -> tuple[AudioSegment, str]:
    """Loads audio from a file path."""
    original_name = os.path.basename(file_path)
    try:
        with open(file_path, "rb") as f:
            file_content = f.read()
            if is_base64(file_content):
                audio_bytes = base64.b64decode(file_content)
                return AudioSegment.from_file(BytesIO(audio_bytes)), original_name
            elif original_name.endswith(".npy"):
                numpy_array = np.load(BytesIO(file_content))
                return AudioSegment(
                    data=numpy_array.tobytes(),
                    frame_rate=44100,  # Provide a default or try to infer
                    sample_width=2,
                    channels=1 if len(numpy_array.shape) == 1 else 2
                ), original_name
            # Removed pickle loading for security and clarity, consider adding back with caution
            else:
                return AudioSegment.from_file(BytesIO(file_content)), original_name
    except Exception as e:
        raise AudioLoadingError(f"Error loading audio from file {file_path}: {e}")

def _load_from_url(url: str) -> tuple[AudioSegment, str]:
    """Loads audio from a URL."""
    audio_segment = _download_audio(url)
    if audio_segment:
        original_name = os.path.basename(url.split("?")[0])
        return audio_segment, original_name
    else:
        raise AudioLoadingError(f"Could not load audio from URL: {url}")

def _load_from_numpy(audio_array: np.ndarray) -> AudioSegment:
    """Loads audio from a NumPy array."""
    try:
        return AudioSegment(
            data=audio_array.tobytes(),
            frame_rate=44100,  # Provide a default or require this info
            sample_width=2,
            channels=1 if len(audio_array.shape) == 1 else 2
        )
    except Exception as e:
        raise AudioLoadingError(f"Error loading audio from NumPy array: {e}")

def _load(audio: Union[str, bytes, np.ndarray, AudioSegment], input_type: Literal["auto", "base64", "file", "url", "numpy", "pydub", "dataUrl"]) -> tuple[AudioSegment, Optional[str]]:
    """Internal function to load audio and determine its original name."""
    original_name = None

    if input_type == "auto":
        if isinstance(audio, AudioSegment):
            return audio, None
        elif isinstance(audio, np.ndarray):
            return _load_from_numpy(audio), None
        elif isinstance(audio, str):
            if audio.startswith("data:audio/"):
                input_type = "dataUrl"
            elif os.path.isfile(audio):
                input_type = "file"
            elif re.match(r'^(?:http|ftp)s?://', audio):
                input_type = "url"
            elif is_base64(audio):
                input_type = "base64"
            else:
                raise AudioLoadingError(f"Could not determine input type for string: '{audio[:50]}...'")
        elif isinstance(audio, bytes) and is_base64(audio):
            input_type = "base64"
        else:
            raise AudioLoadingError(f"Invalid input type for auto-detection: {type(audio)}")

    if input_type == "base64" or input_type == "dataUrl":
        return _load_from_base64(audio if isinstance(audio, str) else audio.decode('utf-8')), None
    elif input_type == "file":
        return _load_from_file(audio)
    elif input_type == "url":
        return _load_from_url(audio)
    elif input_type == "numpy":
        return _load_from_numpy(audio), None
    elif input_type == "pydub":
        return audio, None
    else:
        raise ValueError(f"Invalid input type: {input_type}")

def load_audio(
    audio: Union[str, bytes, np.ndarray, AudioSegment],
    output_type: Literal["pydub", "numpy", "base64", "dataUrl", "file"] = "pydub",
    input_type: Literal["auto", "base64", "file", "url", "numpy", "pydub", "dataUrl"] = "auto",
    output_path: Optional[str] = None,
    output_format: Optional[str] = "mp3",
) -> Any:
    """Loads an audio file from various sources and returns it in a specified format.

    Args:
        audio: The input audio.
        output_type: The desired output type.
        input_type: The type of the input audio.

    Returns:
        The loaded audio in the specified output type.

    Raises:
        ValueError: If the input or output type is invalid.
        AudioLoadingError: If there's an issue loading the audio.
    """
    audio_segment, original_name = _load(audio, input_type)
    if output_type == "pydub":
        return audio_segment
    elif output_type == "file":
        if output_path is None:
            if original_name and "." in original_name:
                output_path = f'{original_name.split(".")[0]}.{output_format}'
            else:
                output_path = f"loadaudio_{uuid.uuid4()}.{output_format}"
        else:
            output_format = output_path.split(".")[-1].lower()
        audio_segment.export(output_path, format=output_format)
        return
    elif output_type == "numpy":
        return np.array(audio_segment.get_array_of_samples())
    elif output_type in ["base64", "dataUrl"]:
        audio_type = "wav"  # Default type
        if original_name and "." in original_name:
            audio_type = original_name.split(".")[-1].lower()

        with BytesIO() as buffer:
            try:
                audio_segment.export(buffer, format=audio_type)
                audio_bytes = buffer.getvalue()
                audio_str = base64.b64encode(audio_bytes).decode("utf-8")
            except Exception as e:
                raise AudioLoadingError(f"Error encoding audio to base64: {e}")

        if output_type == "base64":
            return audio_str
        elif output_type == "dataUrl":
            return f"data:audio/{audio_type};base64,{audio_str}"
    else:
        raise ValueError(f"Invalid output type: {output_type}")

if __name__ == "__main__":
    # wave to mp3
    load_audio("audio.wav", output_type="file", output_path="output.mp3")
    # # base64 file to wav (assuming output.txt contains base64)
    try:
        load_audio("output.txt", output_type="file")
    except FileNotFoundError:
        print("output.txt not found, skipping base64 file test.")
    # url to base64
    try:
        base64_output = load_audio("https://github.com/KingNish24/assets/raw/refs/heads/ui-enhancement/wrong.mp3", output_type="base64")
        print(base64_output[:100])
    except Exception as e:
        print(f"Error loading from URL: {e}")
    # numpy array to dataUrl
    numpy_array = np.array([1000, 2000, 3000], dtype=np.int16) # Ensure appropriate dtype
    print(load_audio(numpy_array, output_type="dataUrl"))
    # Done
    # wav to file
    load_audio(audio="audio.wav", output_type="file")
    # mp3 to wav
    load_audio(audio="output.mp3", output_type="file", output_path="test.wav")
    base64_output = load_audio("https://github.com/KingNish24/assets/raw/refs/heads/ui-enhancement/wrong.mp3", output_type="file", output_format="ogg")


    print("Done")