"""
Configuration for Interview Voice Assistant

PRODUCTION SETTINGS - Optimized for latency and token efficiency.
"""
import os

# =============================================================================
# Audio Configuration
# =============================================================================

AUDIO_SAMPLE_RATE = 16000
AUDIO_CHANNELS = 1
AUDIO_CHUNK_DURATION_MS = 20  # Reduced for faster processing

# Voice Activity Detection
VAD_AGGRESSIVENESS = 1  # Less aggressive = faster processing
VAD_PADDING_MS = 800  # Increased padding to capture full sentences

# Recording limits
MAX_RECORDING_DURATION = 15.0  # Increased from 8.0s to allow full questions
MIN_AUDIO_LENGTH = 0.5

# =============================================================================
# Adaptive Silence Detection
# =============================================================================

SILENCE_DEFAULT = 1.2  # Reduced for faster response (balanced)
SILENCE_YOUTUBE = 1.0
SILENCE_MEET = 1.2
SILENCE_ZOOM = 1.2
SILENCE_TEAMS = 1.2

# =============================================================================
# Speech-to-Text (Whisper)
# =============================================================================

STT_MODEL = os.environ.get("STT_MODEL_OVERRIDE", "small.en")
STT_DEVICE = None

# =============================================================================
# LLM Configuration (Claude)
# =============================================================================

LLM_MODEL = os.environ.get("LLM_MODEL_OVERRIDE", "claude-sonnet-4-20250514")
LLM_MAX_TOKENS_INTERVIEW = 130  # 3-4 short bullet points, hard cap
LLM_MAX_TOKENS_CODING = 450
LLM_TEMPERATURE_INTERVIEW = 0.4  # Higher for more natural human-like speech
LLM_TEMPERATURE_CODING = 0.1
LLM_TIMEOUT = 10.0

# =============================================================================
# Timing & Latency
# =============================================================================

COOLDOWN_BASE = 0.5
COOLDOWN_PER_CHAR = 0.002
COOLDOWN_CODE_BONUS = 1.0
COOLDOWN_DURATION = 2.0
DEDUP_WINDOW = 5.0

TARGET_SIMPLE_QUESTION_MS = 2000
TARGET_COMPLEX_QUESTION_MS = 4000
TARGET_CACHE_HIT_MS = 500

# =============================================================================
# Answer Caching
# =============================================================================

ENABLE_CACHE = True
CACHE_MAX_SIZE = 1000

# =============================================================================
# Web UI
# =============================================================================

WEB_PORT = 8000
WEB_HOST = "0.0.0.0"

# =============================================================================
# Paths
# =============================================================================

RESUME_PATH = os.environ.get("RESUME_PATH", "resume.txt")
JD_PATH = "job_description.txt"
ANSWERS_DIR = "~/.interview_assistant"

# =============================================================================
# Debug (ALL OFF for production)
# =============================================================================

DEBUG = False
VERBOSE = True
LOG_TO_FILE = True
DEBUG_MODE = False
SAVE_DEBUG_AUDIO = False
