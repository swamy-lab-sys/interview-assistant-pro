"""
Configuration for Interview Voice Assistant

PRODUCTION SETTINGS - Optimized for latency and reliability.

DESIGN PRINCIPLES:
- Fast responses (< 4s target)
- No microphone blocking
- Graceful degradation
- Single-shot LLM (no streaming)
"""

# =============================================================================
# Audio Configuration
# =============================================================================

AUDIO_SAMPLE_RATE = 16000  # Hz (required for Whisper)
AUDIO_CHANNELS = 1          # Mono
AUDIO_CHUNK_DURATION_MS = 30  # VAD frame size (10, 20, or 30)

# Voice Activity Detection
# Voice Activity Detection
VAD_AGGRESSIVENESS = 2      # 0-3, lowered for better continuity
VAD_PADDING_MS = 500        # Maximum padding to prevent syllable cut-off

# Recording limits - OPTIMIZED FOR YOUTUBE
MAX_RECORDING_DURATION = 6.0    # Short window to catch ONLY the question
MIN_AUDIO_LENGTH = 0.3          # seconds

# =============================================================================
# Adaptive Silence Detection - FINAL OPTIMIZED
# =============================================================================

SILENCE_DEFAULT = 0.5   # ULTRA FAST (User request)
SILENCE_YOUTUBE = 0.8   # Faster YouTube
SILENCE_MEET = 0.8
SILENCE_ZOOM = 0.8
SILENCE_TEAMS = 0.8

# =============================================================================
# Speech-to-Text (Whisper)
# =============================================================================

STT_MODEL = "tiny.en"   # LIGHTWEIGHT & FAST (User request)
STT_DEVICE = None       # Auto-detect (cuda/cpu)

# =============================================================================
# LLM Configuration (Claude)
# =============================================================================

LLM_MODEL = "claude-3-haiku-20240307"  # Fastest Claude model
LLM_MAX_TOKENS_INTERVIEW = 200         # Short answers
LLM_MAX_TOKENS_CODING = 512            # Code needs more
LLM_TEMPERATURE_INTERVIEW = 0.3        # Consistent
LLM_TEMPERATURE_CODING = 0.2           # Deterministic
LLM_TIMEOUT = 10.0                     # seconds

# =============================================================================
# Timing & Latency
# =============================================================================

COOLDOWN_BASE = 0.5           # Snappier recovery
COOLDOWN_PER_CHAR = 0.002     # Faster reading assumption
COOLDOWN_CODE_BONUS = 1.0     # Less wait for code

# Cooldown after answer (prevents rapid re-triggering)
COOLDOWN_DURATION = 2.0  # seconds

# Deduplication window (same question ignored)
DEDUP_WINDOW = 5.0  # seconds

# Latency targets (for logging/monitoring)
TARGET_SIMPLE_QUESTION_MS = 2000   # < 2s for simple questions
TARGET_COMPLEX_QUESTION_MS = 4000  # < 4s for complex questions
TARGET_CACHE_HIT_MS = 500          # < 0.5s for cached answers

# =============================================================================
# Answer Caching
# =============================================================================

ENABLE_CACHE = True
CACHE_MAX_SIZE = 1000  # Max cached questions

# =============================================================================
# Web UI
# =============================================================================

WEB_PORT = 8000
WEB_HOST = "0.0.0.0"

# =============================================================================
# Paths
# =============================================================================

RESUME_PATH = "resume.txt"
ANSWERS_DIR = "~/.interview_assistant"

# =============================================================================
# Debug (Disabled in production)
# =============================================================================

DEBUG = False
VERBOSE = True                  # Re-enabled for final verification
LOG_TO_FILE = True
DEBUG_MODE = True
SAVE_DEBUG_AUDIO = True
