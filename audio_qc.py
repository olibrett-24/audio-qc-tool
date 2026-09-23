"""
Audio QC Tool
Scans a folder of audio files and checks each one for common problems:
clipping, DC offset, unexpected silence, and mono compatibility.
"""

import argparse
import os
import librosa
import numpy as np


def check_clipping(filepath, threshold=0.99):
    y, sr = librosa.load(filepath, sr=None)
    clipped_samples = np.sum(np.abs(y) >= threshold)
    clipped_percent = (clipped_samples / len(y)) * 100
    passed = clipped_samples == 0
    if passed:
        return True, "no clipping detected"
    return False, f"clipping detected ({clipped_samples} samples, {clipped_percent:.4f}%)"


def check_dc_offset(filepath, threshold=0.02):
    y, sr = librosa.load(filepath, sr=None)
    mean_level = np.mean(y)
    passed = abs(mean_level) <= threshold
    if passed:
        return True, f"mean level {mean_level:.4f}"
    return False, f"DC offset detected (mean level {mean_level:.4f})"


def check_silence(filepath, top_db=40, max_silence_seconds=2.0):
    y, sr = librosa.load(filepath, sr=None)
    non_silent_intervals = librosa.effects.split(y, top_db=top_db)

    if len(non_silent_intervals) == 0:
        return False, "entire file is silent"

    gaps = [non_silent_intervals[0][0]]
    for i in range(len(non_silent_intervals) - 1):
        gaps.append(non_silent_intervals[i + 1][0] - non_silent_intervals[i][1])
    gaps.append(len(y) - non_silent_intervals[-1][1])

    longest_gap_seconds = max(gaps) / sr
    passed = longest_gap_seconds <= max_silence_seconds
    if passed:
        return True, f"longest gap {longest_gap_seconds:.2f}s"
    return False, f"unexpected silence detected (longest gap {longest_gap_seconds:.2f}s)"


def check_mono_compatibility(filepath, threshold_db=6.0):
    y, sr = librosa.load(filepath, sr=None, mono=False)

    if y.ndim == 1:
        return True, "mono file, no stereo phase risk"

    left, right = y[0], y[1]
    mono_sum = (left + right) / 2

    rms_left = np.sqrt(np.mean(left ** 2))
    rms_right = np.sqrt(np.mean(right ** 2))
    rms_mono = np.sqrt(np.mean(mono_sum ** 2))

    loudest_channel = max(rms_left, rms_right, 1e-10)
    loss_db = 20 * np.log10(loudest_channel / max(rms_mono, 1e-10))

    passed = loss_db <= threshold_db
    if passed:
        return True, f"{loss_db:.1f}dB level change when summed to mono"
    return False, f"possible phase cancellation ({loss_db:.1f}dB level change when summed to mono)"


CHECKS = [
    ("Clipping", check_clipping),
    ("DC Offset", check_dc_offset),
    ("Silence", check_silence),
    ("Mono Compatibility", check_mono_compatibility),
]


def find_audio_files(folder):
    supported = (".wav", ".mp3", ".flac", ".aiff", ".aif")
    return sorted(
        os.path.join(folder, f) for f in os.listdir(folder)
        if f.lower().endswith(supported)
    )


def run_checks(folder):
    audio_files = find_audio_files(folder)

    if not audio_files:
        print(f"No audio files found in {folder}")
        return

    print(f"Found {len(audio_files)} audio file(s) in {folder}\n")

    total_checks = 0
    total_failures = 0

    for filepath in audio_files:
        print(f"--- {os.path.basename(filepath)} ---")

        for check_name, check_function in CHECKS:
            try:
                passed, message = check_function(filepath)
            except Exception as e:
                passed, message = False, f"check crashed: {e}"

            status = "PASS" if passed else "FAIL"
            print(f"  [{status}] {check_name}: {message}")

            total_checks += 1
            if not passed:
                total_failures += 1

        print()

    print(f"Summary: {total_checks} checks run, {total_failures} failed")


def main():
    parser = argparse.ArgumentParser(
        description="Scan a folder of audio files for common QC problems."
    )
    parser.add_argument("folder", help="Path to the folder of audio files to check")
    args = parser.parse_args()
    run_checks(args.folder)


if __name__ == "__main__":
    main()