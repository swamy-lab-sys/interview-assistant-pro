"""
STT Engine 3.0: High-Accuracy Faster-Whisper
Optimized for exact word capture like ChatGPT voice mode.

Key improvements:
- Larger model (small.en) for better accuracy
- Enhanced VAD for clean audio segments
- Better initial prompt for technical terms
- Optimized beam search for accuracy
"""

import numpy as np
import warnings
import time
import os
import re
import torch
from faster_whisper import WhisperModel

warnings.filterwarnings("ignore", category=UserWarning)

import config

# Global model
model = None
model_name = None

# Default to config setting
DEFAULT_MODEL = config.STT_MODEL  # base.en for speed, medium.en for accuracy

def load_model(model_size=None):
    """Load Faster-Whisper model."""
    global model, model_name
    
    if model_size is None:
        model_size = DEFAULT_MODEL
        
    device = "cuda" if torch.cuda.is_available() else "cpu"
    # Use int8 on CPU or float16 on GPU for speed
    compute_type = "float16" if device == "cuda" else "int8"
    
    if model is None or model_name != model_size:
        print(f"  [STT] Loading Faster-Whisper '{model_size}' on {device}/{compute_type}...")
        # OPTIMIZATION: Limit threads to 4 to prevent CPU oversubscription on laptops
        model = WhisperModel(model_size, device=device, compute_type=compute_type, cpu_threads=4)
        model_name = model_size
        
    return model


# Technical vocabulary for better recognition
TECH_PROMPT = """Context: A technical software engineering interview.
Keywords to recognize accurately:
- CI/CD, CICD, Jenkins, GitLab CI, GitHub Actions, Pipeline, Deployment.
- Kubernetes, K8s, Docker, Container, Pod, Service, Ingress, Helm.
- Python, Django, Flask, FastAPI, PyTest, NumPy, Pandas, AsyncIO.
- REST, GraphQL, gRPC, WebSocket, API, Endpoint, JSON, YAML.
- AWS, Lambda, EC2, S3, RDS, CloudFront, Terraform, Ansible.
- SQL, PostgreSQL, MySQL, Redis, MongoDB, Cassandra, Database.
- List, Tuple, Dictionary, Set, HashMap, LinkedList, Tree, Graph.
- Algorithm, Big O, Complexity, Recursion, Dynamic Programming.
- System Design, Scalability, Load Balancer, Caching, Microservices.
- Agile, Scrum, Kanban, JIRA, Confluence, Git, Merge Request.
- SRE, DevOps, Observability, Prometheus, Grafana, ELK Stack.
"""


# Pre-compiled corrections (compiled once at module load, not per transcription)
_RAW_CORRECTIONS = {
    "pie thon": "Python", "pie-thon": "Python", "python's": "Python's",
    "pie chart": "Python", "4-by-thon": "Python", "4 by thon": "Python",
    "four by thon": "Python", "by thon": "Python",
    "tupel": "tuple", "topple": "tuple",
    "two pull": "tuple", "deck orator": "decorator", "decorate her": "decorator",
    "it a rater": "iterator", "generate her": "generator",
    "generate trip": "generator", "generator trip": "generator",
    "a sink": "async", "a wait": "await",
    "jango": "Django", "d jango": "Django", "d django": "Django",
    "dd jango": "Django", "ddjango": "Django", "d-jango": "Django",
    "re act": "React",
    "reston": "list and", "western": "list and",
    "rich and coupled": "list and tuple", "rich coupled": "list and tuple",
    "un-out": "and odd", "un out": "and odd",
    "entity puruses": "HTTP statuses", "entity purposes": "HTTP statuses",
    "at their room": "errors", "up there": "errors",
    "cacd": "CI/CD", "ci cd": "CI/CD", "c i c d": "CI/CD",
    "see i see d": "CI/CD", "a w s": "AWS",
    "blueprint": "blue-green",
    # Django-specific misheard
    "meet migrations": "makemigrations", "meetmigrations": "makemigrations",
    "meet migration": "makemigrations", "meat migrations": "makemigrations",
    "make migration": "makemigrations", "make migrations": "makemigrations",
    # *args and **kwargs
    "arcs and kwas": "*args and **kwargs", "arcs and kw arcs": "*args and **kwargs",
    "arcs and kwargs": "*args and **kwargs", "arks and kwargs": "*args and **kwargs",
    "arks and kwas": "*args and **kwargs", "arks and kw arks": "*args and **kwargs",
    "arcs": "*args", "kw arcs": "**kwargs", "kw arks": "**kwargs",
    # Microservices
    "microletic": "microservices", "micro letic": "microservices",
    "microlitic": "microservices", "micro litic": "microservices",
    # JWT (often misheard as GWT)
    "gwt": "JWT", "g w t": "JWT",
    # Django ORM
    "django over m": "Django ORM", "d jango over m": "Django ORM",
    "django orm": "Django ORM",
    # CORS
    "cars error": "CORS error", "cars errors": "CORS errors",
    # Nginx (often misheard as NVIDIA)
    "nvidia architecture engine": "Nginx",
    # Tuple misheard as Docker/other
    "list and docker": "list and tuple", "list and docker in": "list and tuple in",
    "list and darker": "list and tuple", "list and talker": "list and tuple",
    "list and tougher": "list and tuple", "list and topper": "list and tuple",
    # Encapsulation misheard
    "capitation": "encapsulation", "capitulation": "encapsulation",
    "cap station": "encapsulation", "capsulation": "encapsulation",
    "python and capitation": "Python encapsulation",
    "python capitation": "Python encapsulation",
    "python encapsulation": "Python encapsulation",
    # Raw SQL misheard
    "big django sql": "raw Django SQL", "big jango sql": "raw Django SQL",
    "pig django sql": "raw Django SQL",
    "raw sql": "raw SQL", "raw sequel": "raw SQL",
    # Abstraction misheard
    "obstruction": "abstraction", "obstraction": "abstraction",
    # etcd misheard
    "et cd": "etcd", "etc d": "etcd", "e t c d": "etcd",
    "80 cd": "etcd", "at cd": "etcd",
    # Pod lifecycle
    "pod life cycle": "pod lifecycle", "pot lifecycle": "pod lifecycle",
    # "Write" misheard as "Right/Righty" (very common STT error)
    "righty": "write an",
    # "explain" misheard as "ask my"
    "ask my": "explain",
}
_COMPILED_CORRECTIONS = [
    (re.compile(re.escape(wrong), re.IGNORECASE), right)
    for wrong, right in _RAW_CORRECTIONS.items()
]


def transcribe(audio_array):
    """
    Transcribe with HIGH ACCURACY.
    Returns (text, confidence)
    
    Optimized for exact word capture like ChatGPT.
    """
    global model
    if model is None:
        load_model()
        
    # faster-whisper expects float32
    if audio_array.dtype != np.float32:
        audio_array = audio_array.astype(np.float32)
    
    # Normalize audio for consistent levels
    max_val = np.abs(audio_array).max()
    if max_val > 0:
        audio_array = audio_array / max_val * 0.95

    # FAST transcription - optimized for low latency
    segments, info = model.transcribe(
        audio_array,
        beam_size=1,        # Greedy decoding (Faster on CPU)
        best_of=1,
        temperature=0.0,    # Deterministic
        word_timestamps=False,
        vad_filter=False,   # DISABLED: Rely on audio_listener.py VAD to avoid cutting off words
        # vad_parameters=dict(
        #     min_silence_duration_ms=200,
        #     threshold=0.4,
        #     speech_pad_ms=100,
        # ),
        initial_prompt=TECH_PROMPT,
        language="en",
        condition_on_previous_text=False,
        repetition_penalty=1.0, # Faster without penalty
        no_repeat_ngram_size=0,
    )
    
    segments = list(segments)
    
    # Extract text with proper spacing
    text_parts = []
    for seg in segments:
        seg_text = seg.text.strip()
        if seg_text:
            text_parts.append(seg_text)
    
    text = " ".join(text_parts).strip()
    
    # Clean up common transcription issues
    text = post_process_transcription(text)
    
    # Calculate confidence
    if not segments:
        return "", 0.0
        
    avg_logprob = sum(seg.avg_logprob for seg in segments) / len(segments)
    # More accurate confidence mapping
    confidence = min(1.0, np.exp(avg_logprob + 1.2))
    
    return text, confidence


def post_process_transcription(text):
    """
    Fix common transcription errors for technical terms.
    """
    if not text:
        return text
    
    result = text
    for pattern, right in _COMPILED_CORRECTIONS:
        result = pattern.sub(right, result)
    
    return result


def get_model_info():
    return {
        'name': model_name,
        'backend': 'faster-whisper',
        'device': 'gpu' if torch.cuda.is_available() else 'cpu',
        'accuracy_mode': 'high'
    }
