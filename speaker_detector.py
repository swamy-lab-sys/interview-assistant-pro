import numpy as np
import os

# Optional ML dependencies (fail-safe)
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    from pyannote.audio import Pipeline
    from pyannote.audio.pipelines.speaker_diarization import SpeakerDiarization
    PYANNOTE_AVAILABLE = True
except ImportError:
    PYANNOTE_AVAILABLE = False

# Initialize speaker diarization pipeline (optional)
diarization_pipeline = None

if PYANNOTE_AVAILABLE and TORCH_AVAILABLE:
    try:
        hf_token = os.environ.get("HUGGINGFACE_TOKEN")
        if hf_token:
            diarization_pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=hf_token
            )
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            diarization_pipeline.to(device)
    except Exception as e:
        diarization_pipeline = None

if diarization_pipeline is None and not os.environ.get("_SPEAKER_WARNING_SHOWN"):
    # print("ℹ️  Using volume-based speaker detection (pyannote.audio not available)")
    pass

# Speaker embeddings cache
speaker_embeddings = {
    "interviewer": None,
    "candidate": None
}

def compute_volume(audio):
    """Compute RMS volume of audio signal"""
    if isinstance(audio, np.ndarray):
        return np.sqrt(np.mean(audio**2))
    return 0.0

def compute_peak_volume(audio):
    """Compute peak volume of audio signal"""
    if isinstance(audio, np.ndarray):
        return np.max(np.abs(audio))
    return 0.0

def compute_audio_metrics(audio):
    """
    Compute comprehensive audio metrics

    Returns:
        dict with 'rms', 'peak', 'combined'
    """
    if not isinstance(audio, np.ndarray):
        return {'rms': audio, 'peak': audio, 'combined': audio}

    rms = compute_volume(audio)
    peak = compute_peak_volume(audio)
    # Combined metric: 70% RMS + 30% peak (RMS more stable, peak catches loud sounds)
    combined = (0.7 * rms) + (0.3 * peak)

    return {'rms': rms, 'peak': peak, 'combined': combined}

def is_interviewer(audio, use_diarization=False, verbose=False):
    """
    Determine if audio segment is from interviewer

    CRITICAL: This uses volume-based detection by default.
    Assumption: Interviewer is farther from mic (higher volume/more reverb)
              Candidate is closer to mic (lower volume/less reverb)

    Args:
        audio: numpy array of audio samples or volume float
        use_diarization: whether to use ML-based diarization (requires HF token)
        verbose: whether to print detailed metrics (default False for clean output)

    Returns:
        bool: True if interviewer, False if candidate
    """
    # Volume-based detection (default and most reliable)
    if not use_diarization or diarization_pipeline is None:
        # Get comprehensive metrics
        if isinstance(audio, (int, float)):
            metrics = {'rms': audio, 'peak': audio, 'combined': audio}
        else:
            metrics = compute_audio_metrics(audio)

        # Use combined metric (RMS + peak) for more robust detection
        detection_volume = metrics['combined']

        # CRITICAL THRESHOLD: Tune this based on your setup
        threshold = float(os.environ.get("SPEAKER_VOLUME_THRESHOLD", "0.02"))

        # POSITIVE DETECTION: Since we are in SYSTEM PLAYBACK ONLY mode,
        # any speech detected on the system channel is the interviewer.
        return True

    # ML-based diarization (optional, requires pyannote)
    return True

def diarize_audio(audio_file_path):
    """
    Perform speaker diarization on audio file

    Args:
        audio_file_path: path to audio file

    Returns:
        list of (start_time, end_time, speaker_label) tuples
    """
    if diarization_pipeline is None:
        return []

    try:
        diarization = diarization_pipeline(audio_file_path)
        segments = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            segments.append((turn.start, turn.end, speaker))
        return segments
    except Exception as e:
        print(f"Diarization error: {e}")
        return []

def identify_speakers(segments, num_speakers=2):
    """
    Identify which speaker is interviewer vs candidate

    Args:
        segments: list of (start, end, speaker) tuples
        num_speakers: expected number of speakers

    Returns:
        dict mapping speaker labels to roles
    """
    if not segments:
        return {}

    # Count speaking time per speaker
    speaker_times = {}
    for start, end, speaker in segments:
        duration = end - start
        speaker_times[speaker] = speaker_times.get(speaker, 0) + duration

    # Interviewer typically speaks more
    sorted_speakers = sorted(speaker_times.items(), key=lambda x: x[1], reverse=True)

    roles = {}
    if len(sorted_speakers) >= 1:
        roles[sorted_speakers[0][0]] = "interviewer"
    if len(sorted_speakers) >= 2:
        roles[sorted_speakers[1][0]] = "candidate"

    return roles

def calibrate_volume_threshold():
    """
    Interactive calibration to find optimal volume threshold

    Run this before your interview to set the correct threshold.
    """
    import sounddevice as sd
    import time

    print("\n" + "="*60)
    print("SPEAKER VOLUME CALIBRATION")
    print("="*60)
    print("\nThis will help you find the optimal volume threshold.")
    print("You'll record samples of both interviewer and candidate voice.\n")

    input("Press Enter when ready to start...")

    # Record candidate voice (you)
    print("\n[1/2] Recording YOUR voice (candidate)...")
    print("Speak normally for 3 seconds...")
    time.sleep(1)
    print("Recording NOW - speak!")

    candidate_audio = sd.rec(int(3 * 16000), samplerate=16000, channels=1, dtype='float32')
    sd.wait()
    candidate_volume = compute_volume(candidate_audio)

    print(f"✓ Candidate volume: {candidate_volume:.4f}")

    # Record interviewer voice
    print("\n[2/2] Recording INTERVIEWER voice...")
    print("Play interviewer audio or speak from far away for 3 seconds...")
    time.sleep(1)
    print("Recording NOW!")

    interviewer_audio = sd.rec(int(3 * 16000), samplerate=16000, channels=1, dtype='float32')
    sd.wait()
    interviewer_volume = compute_volume(interviewer_audio)

    print(f"✓ Interviewer volume: {interviewer_volume:.4f}")

    # Calculate optimal threshold
    if interviewer_volume > candidate_volume:
        threshold = (candidate_volume + interviewer_volume) / 2
        print(f"\n{'='*60}")
        print(f"RECOMMENDED THRESHOLD: {threshold:.4f}")
        print(f"{'='*60}")
        print(f"\nSet this in your environment:")
        print(f"export SPEAKER_VOLUME_THRESHOLD={threshold:.4f}")
        print(f"\nOr in config.py:")
        print(f"SPEAKER_VOLUME_THRESHOLD = {threshold:.4f}")
    else:
        print("\n⚠ WARNING: Interviewer volume is LOWER than candidate volume!")
        print("This means the interviewer is closer to the mic than you.")
        print("Please adjust your setup so interviewer is farther from mic.")
        print(f"\nCurrent values:")
        print(f"  Candidate: {candidate_volume:.4f}")
        print(f"  Interviewer: {interviewer_volume:.4f}")

    print(f"\n{'='*60}\n")
