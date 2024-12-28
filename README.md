# loadaudio

<!-- [![PyPI version](https://badge.fury.io/py/loadaudio.svg)](https://pypi.org/project/loadaudio/)
![Python Versions](https://img.shields.io/pypi/pyversions/loadaudio)
<!-- Add more badges here for build status, code coverage, etc. if applicable -->

<!-- **Load Audio Like a Pro!** -->

`loadaudio` is a Python library designed to effortlessly load audio from a variety of sources and convert it to your desired format. Whether you're working with local files, remote URLs, base64 encoded strings, NumPy arrays, or pydub AudioSegment objects, `loadaudio` provides a simple and consistent interface.

## Features

*   **Versatile Input:** Load audio from:
    *   Local file paths (`.wav`, `.mp3`, etc.)
    *   URLs pointing to audio files
    *   Base64 encoded audio strings
    *   Data URLs (base64 encoded audio embedded in strings)
    *   NumPy arrays representing audio samples
    *   `pydub.AudioSegment` objects
*   **Flexible Output:** Convert loaded audio to:
    *   `pydub.AudioSegment` objects
    *   NumPy arrays
    *   Local file paths (`.wav`, `.mp3`, etc.)
    *   Base64 encoded strings
    *   Data URLs
*   **Automatic Input Type Detection:**  In most cases, `loadaudio` can automatically determine the input type, simplifying your code.
*   **Handles Common Audio Formats:** Supports a wide range of audio formats compatible with `pydub`.

## Installation

```bash
pip install loadaudio
```

## Usage

```python
from loadaudio import load_audio
import numpy as np
from pydub import AudioSegment

# Load audio from a file path as a pydub AudioSegment
audio_segment = load_audio("audio.wav", output_type="pydub")

# Load audio from a URL as a NumPy array
audio_numpy = load_audio("https://example.com/audio.mp3", output_type="numpy")

# Load a base64 string or data URL and save as a wav
file_path = load_audio("data:audio/wav;base64,...", output_type="file", output_path="output.wav")

# Load a NumPy array as a base64 string
numpy_array = np.array([1, 2, 3], dtype=np.int16)  # Example data
base64_string = load_audio(numpy_array, output_type="base64")

# Load a pydub AudioSegment and get a data URL
pydub_segment = AudioSegment.from_file("another_audio.mp3")
data_url = load_audio(pydub_segment, output_type="dataUrl")

# Explicitly specify the input type (optional)
audio_from_base64 = load_audio("your_base64_string", output_type="pydub", input_type="base64")
```
