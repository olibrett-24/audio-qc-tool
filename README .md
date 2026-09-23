# Audio QC Tool

A command-line tool that scans a folder of audio files and checks each one for common problems, the kind an audio QA pass would normally catch by ear or by spec-check before content ships.

## What it checks

- **Clipping** — flags samples sitting at or near full scale (0dBFS), a sign the signal was too loud when it was recorded or rendered.
- **DC offset** — flags files whose waveform isn't centred on zero, usually a hardware or recording fault.
- **Silence** — flags unexpected long stretches of near-silence, which can mean a broken render or a dropped track.
- **Mono compatibility** — sums left and right channels and checks for phase cancellation, the kind of issue that makes a file sound fine in stereo but lose energy or drop out on a mono speaker or phone.

## Requirements

- Python 3.10+
- librosa, numpy

## Installation

    python3 -m venv .venv
    source .venv/bin/activate
    pip install librosa numpy soundfile

## Usage

Run it against any folder of audio files:

    python audio_qc.py /path/to/audio/folder

It reports a PASS/FAIL line for every check against every file it finds, followed by a summary count.

## Example output

    Found 5 audio file(s) in ./test-files

    --- example.wav ---
      [PASS] Clipping: no clipping detected
      [PASS] DC Offset: mean level 0.0005
      [PASS] Silence: longest gap 0.00s
      [PASS] Mono Compatibility: 0.0dB level change when summed to mono

    Summary: 20 checks run, 4 failed

## Background

Built as a QA portfolio project, alongside a manual test-plan-driven QA pass on TDR Nova (a free dynamic EQ plugin). Where that project demonstrates a structured manual QA process, this one demonstrates the same QA thinking automated and applied at scale across a batch of files.

## Possible future additions

- Loudness (LUFS) consistency checks across a batch
- Sample rate / bit depth / channel count spec compliance
- Click/pop detection