"""
Interview Question Validator

Accepts real interview questions, rejects:
- YouTube/tutorial audio
- Fillers, noise, hallucinations
- Platform commands
"""

import re
from typing import Tuple
from collections import Counter


# =============================================================================
# STT CORRECTION - Fix common Whisper misheard terms
# =============================================================================

STT_CORRECTIONS = {
    # CI/CD misheard variants
    r"\ba,?\s*c,?\s*d\b": "CI CD",
    r"\ba c d\b": "CI CD",
    r"\bca cd\b": "CI CD",
    r"\bc a c d\b": "CI CD",
    r"\bci cd\b": "CI/CD",
    r"\bci slash cd\b": "CI/CD",
    r"\bcontinuous integration continuous (delivery|deployment)\b": "CI/CD",
    r"\bsee\s*eye\s*see\s*dee\b": "CI/CD",
    r"\bintegration\s*continuous\b": "CI/CD",
    # SSH
    r"\bs s h\b": "SSH",
    r"\bss h\b": "SSH",
    # Django (many misheard variants)
    r"\bjungle\b": "Django",
    r"\bjango\b": "Django",
    r"\bdd\s*jango\b": "Django",
    r"\bd\s*django\b": "Django",
    r"\bddjango\b": "Django",
    # Python misheard
    r"\b4[\s-]*by[\s-]*thon\b": "Python",
    r"\bfour[\s-]*by[\s-]*thon\b": "Python",
    # Serializer
    r"\bserial address\b": "serializer",
    r"\bserial izer\b": "serializer",
    # Kubernetes
    r"\bcubernetes\b": "Kubernetes",
    r"\bcuber netties\b": "Kubernetes",
    r"\bk8s\b": "Kubernetes",
    # Other common mishearings
    r"\breston tuple\b": "list and tuple",
    r"\bpost grass\b": "PostgreSQL",
    r"\bpost gress\b": "PostgreSQL",
    r"\bred is\b": "Redis",
    r"\baws lamba\b": "AWS Lambda",
    # Palindrome
    r"\bball and rum\b": "Palindrome",
    r"\bpal and rom\b": "Palindrome",
    # Kubernetes terms
    r"\bconflict\s*map\b": "ConfigMap",
    r"\bconfig\s*map\b": "ConfigMap",
    r"\bsecrete?\b": "Secret",
    # Terraform
    r"\bterra\s*form\b": "Terraform",
    r"\bterraform applet\b": "Terraform apply",
    r"\bterra form apply\b": "Terraform apply",
    # Ansible
    r"\bansible\b": "Ansible",
    # Kafka
    r"\bcafka\b": "Kafka",
    r"\bkafka\b": "Kafka",
    # Grafana
    r"\bgrafana\b": "Grafana",
    r"\bgra fana\b": "Grafana",
    # kubectl
    r"\bkubectl locks\b": "kubectl logs",
    r"\bkubectl\b": "kubectl",
    # Django commands misheard
    r"\bmeet\s*migrations?\b": "makemigrations",
    r"\bmeat\s*migrations?\b": "makemigrations",
    r"\bmake\s*migrations?\b": "makemigrations",
    # *args/**kwargs misheard
    r"\barcs?\s*and\s*kw\s*arcs?\b": "*args and **kwargs",
    r"\barks?\s*and\s*kw\s*arks?\b": "*args and **kwargs",
    r"\barcs?\s*and\s*kwas?\b": "*args and **kwargs",
    r"\barks?\s*and\s*kwas?\b": "*args and **kwargs",
    # Generator misheard
    r"\bgenerate?\s*trip\b": "generator",
    r"\bgenerator\s*trip\b": "generator",
    # Microservices misheard
    r"\bmicro\s*letic\b": "microservices",
    r"\bmicro\s*litic\b": "microservices",
    # JWT misheard as GWT
    r"\bgwt\b": "JWT",
    r"\bg\s*w\s*t\b": "JWT",
    # Django ORM misheard
    r"\bdjango\s*over\s*m\b": "Django ORM",
    # CORS misheard
    r"\bcars\s*error": "CORS error",
    # Nginx misheard
    r"\bnvidia\s*architecture\s*engine\b": "Nginx",
    # "Write" misheard as "Right here/Right there/Righty" at sentence start
    r"^right\s+here,?\s*": "Write a ",
    r"^right\s+there,?\s*": "Write a ",
    r"^righty\s+": "Write an ",
    # Noise prefixes (garbage before real question)
    r"^async\s+out\s+there\.?\s*": "",
    # "explain" misheard as "ask my"
    r"\bask\s+my\b": "explain",
    # OpenStack terms misheard
    r"\bopen\s*sit\b": "OpenShift",
    r"\bopen[\s-]*set\b": "OpenShift",
    r"\bopen\s*savio\b": "OpenStack",
    r"\bopen\s*sav\w+\b": "OpenStack",
    r"\bnawakama\b": "nova.conf",
    r"\bnf[\s_-]?com[\s_-]?track[\s_-]?mo\w*\b": "nf_conntrack",
    r"\bnf\s*com\s*track\b": "nf_conntrack",
    r"\bobvious\s+system\b": "OVS",
    r"\bself[\s-]state\b": "ERROR state",
    r"\bopen\s*stack\b": "OpenStack",
    r"\bopen\s*shift\b": "OpenShift",
    # Linux patching misheard
    r"\bdf[\s-]fn\w+\b": "df -h",
    r"\bdfa[\s-]f\w+\b": "df -h",
    # KVM/QEMU misheard
    r"\bkevm\b": "KVM",
    r"\bkolla\s+ansible\b": "Kolla-Ansible",
}

COMPILED_STT_CORRECTIONS = [(re.compile(p, re.IGNORECASE), r) for p, r in STT_CORRECTIONS.items()]



def apply_stt_corrections(text: str) -> str:
    """Fix common Whisper misheard technical terms."""
    for pattern, replacement in COMPILED_STT_CORRECTIONS:
        text = pattern.sub(replacement, text)
    return text


# =============================================================================
# VAGUE QUESTION DETECTION - Reject pronoun-only follow-ups
# =============================================================================

VAGUE_PRONOUNS = {"it", "this", "that", "them", "they", "those", "these", "its"}

def is_vague_question(text: str) -> bool:
    """Reject vague follow-up questions with only pronouns, no specific subject.

    Examples rejected:
    - "How do you implement it?"
    - "Can you explain that?"
    - "What does it do?"

    Examples allowed:
    - "How do you implement CI/CD?" (has tech term)
    - "What is Docker?" (has tech term)
    """
    lower = text.lower().strip().rstrip("?.,!")
    words = lower.split()

    if len(words) < 3 or len(words) > 8:
        return False

    # Check if any real tech term exists
    has_tech = any(t in lower for t in TECH_TERMS)
    if has_tech:
        return False

    # Check if the only "subject" words are pronouns
    filler_words = {"how", "do", "does", "did", "you", "we", "can", "could", "would",
                    "should", "will", "what", "is", "are", "was", "were", "a", "an",
                    "the", "to", "for", "in", "on", "about", "explain", "describe",
                    "tell", "me", "implement", "use", "work", "mean", "define"}

    subject_words = [w for w in words if w not in filler_words and w not in VAGUE_PRONOUNS]

    # If no subject words AND has a vague pronoun -> reject
    if not subject_words and any(w in VAGUE_PRONOUNS for w in words):
        return True

    return False


# =============================================================================
# YOUTUBE / TUTORIAL DETECTION - Reject non-interview audio
# =============================================================================

YOUTUBE_PATTERNS = [
    r"subscribe", r"like and subscribe", r"hit the bell",
    r"in this video", r"in today's video", r"in this tutorial",
    r"welcome to (my|this|the) (channel|video|tutorial|course|series)",
    r"hey (guys|everyone|everybody)", r"what's up (guys|everyone)",
    r"hello (everyone|guys|friends)", r"hi (guys|everyone)",
    r"let's (get started|begin|dive|jump|look)", r"let me show you",
    r"as you can see", r"on (the|your) screen",
    r"first (we need to|let's|we will|we'll)", r"step (one|two|three|1|2|3)",
    r"(next|now) (we|let's|I'll|I will|we'll)", r"moving on to",
    r"(click|go to|navigate|open) (on|the|this|here)",
    r"(link|links) (in|is in) (the|my) description",
    r"(leave|drop) a comment", r"comment (below|down)",
    r"share this video", r"don't forget to",
    r"thanks for watching", r"see you (in the|next)",
    r"(if you|you should) (liked|enjoyed|found)", r"please (like|share|subscribe)",
    r"(sponsored|brought to you) by",
    r"(check out|visit) (my|our|the) (website|patreon|github|link)",
    r"before we (start|begin|continue|proceed)",
    r"(so|okay|alright|now),?\s+(let's|I'll|we'll|let me)\s+(start|begin|install|setup|configure|learn|see|look|run|open|create|build|go|do|move|jump|proceed|continue|check)",
    r"(chapter|section|part) (one|two|three|\d+)",
    r"(prerequisite|before you|you need to) (know|have|install|understand)",
    r"(watch|see) (my|the) (previous|last|earlier|other) video",
    r"(i'll|i will|we'll|we will) (explain|show|demonstrate|walk you through)",
    r"(follow along|code along|type along)",
    r"(here|this) is (the|a|my|our) (output|result|demo|example)",
    r"(pause|stop) (the|this) video",
    r"(python|programming|coding) (tutorial|course|lesson|series|bootcamp)",
    r"(beginner|intermediate|advanced) (guide|tutorial|course)",
    r"(learn|learning|master|mastering) (python|programming|coding|django)",
]

COMPILED_YOUTUBE = [re.compile(p, re.IGNORECASE) for p in YOUTUBE_PATTERNS]


def is_youtube_or_tutorial(text: str) -> bool:
    """Detect YouTube/tutorial audio content (not interview questions)."""
    if not text or len(text) < 10:
        return False

    lower = text.lower()

    for pattern in COMPILED_YOUTUBE:
        if pattern.search(lower):
            return True

    words = lower.split()
    if len(words) > 40:
        return True

    if len(words) > 20:
        tutorial_words = {'video', 'tutorial', 'channel', 'subscribe', 'course',
                          'lesson', 'click', 'link', 'website', 'download',
                          'install', 'setup', 'screen', 'demo', 'example',
                          'output', 'result', 'step', 'chapter', 'section'}
        found = sum(1 for w in words if w in tutorial_words)
        if found >= 3:
            return True

    return False


# =============================================================================
# QUESTION STARTERS
# =============================================================================

QUESTION_STARTERS = [
    "what is", "what are", "what does", "what do", "what's",
    "why is", "why do", "why does", "why would",
    "how do", "how does", "how to", "how can", "how would",
    "when do", "when does", "when should", "when would",
    "where do", "where does", "where is",
    "which", "is there", "are there", "can you", "could you",
    "explain", "describe", "define", "compare", "tell me",
    "difference between", "walk me through",
    "write", "implement", "create", "give me",
    "have you", "do you have", "how much", "how many years",
]

TECH_TERMS = {
    "python", "class", "function", "method", "decorator", "generator",
    "list", "tuple", "dict", "dictionary", "set", "string", "array",
    "inheritance", "polymorphism", "encapsulation", "abstraction",
    "django", "flask", "api", "rest", "database", "sql", "orm",
    "docker", "kubernetes", "aws", "git", "ci/cd", "pipeline",
    "async", "await", "thread", "process", "memory", "garbage",
    "exception", "error", "try", "except", "loop", "recursion",
    "lambda", "closure", "scope", "variable", "module", "package",
    "import", "virtual", "environment", "pip", "pytest", "unittest",
    "serializer", "middleware", "authentication", "authorization",
    "cache", "redis", "celery", "microservice", "monolith",
    "deployment", "container", "pod", "helm", "terraform",
    "branch", "merge", "commit", "pull request", "cicd",
    "agile", "scrum", "sprint", "devops", "cloud",
    # DevOps/SRE terms
    "prometheus", "grafana", "monitoring", "metrics", "alerting",
    "kafka", "zookeeper", "broker", "topic", "partition",
    "jenkins", "ansible", "terraform", "argo", "argocd",
    "configmap", "secret", "namespace", "ingress", "service",
    "kubectl", "eks", "ecs", "ec2", "s3", "iam", "vpc",
    "cloudwatch", "cloudfront", "load balancer", "autoscaling",
    "infrastructure", "provisioning", "automation",
    "nginx", "apache", "reverse proxy", "ssl", "tls",
    "linux", "bash", "shell", "script", "cron",
    "openshift", "rancher", "istio", "envoy",
    # OpenStack services
    "openstack", "nova", "neutron", "cinder", "glance", "keystone", "swift", "heat", "kolla",
    "nova-compute", "nova-api", "nova-conductor", "nova-scheduler",
    "ovs", "openvswitch", "open vswitch", "ovs-vsctl",
    "kvm", "qemu", "libvirt", "hypervisor", "ceph", "lvm",
    "migration", "live migration", "cold migration", "evacuate",
    # Linux/SRE commands and concepts
    "nf_conntrack", "conntrack", "iptables", "netfilter", "firewall",
    "lsof", "iostat", "vmstat", "iotop", "htop", "lsblk", "fdisk", "fstab",
    "fsck", "grub", "selinux", "sestatus", "inode",
    "load average", "iowait", "cpu utilization",
    "patching", "yum", "dnf", "apt",
    "read-only", "mount point", "file system", "remount",
    "single user mode", "rescue mode", "recovery mode",
    "open files", "file descriptor",
    "disk io", "block device", "storage",
    # Networking
    "tcp", "udp", "dns", "dhcp", "nat", "vlan", "vxlan",
    "bridge", "veth", "tap interface",
    # NFS/SAN/NAS
    "nfs", "san", "nas", "cifs",
    "rollout", "rollback", "canary", "blue green",
    "log", "logging", "tracing", "observability",
    "annotation", "label", "selector", "replica",
    "node", "cluster", "scaling", "hpa",
    "yaml", "json", "xml", "config",
    "module", "provider", "state", "plan", "apply",
    "troubleshoot", "debug", "performance", "optimize",
    "experience", "responsibility", "profile", "tool",
    "component", "configuration", "command",
    # Web framework terms
    "makemigrations", "migrate", "migration", "orm", "jwt", "cors",
    "drf", "rest framework", "viewset", "serializer",
    "manage.py", "routing", "signal", "signals",
    "args", "kwargs", "anagram", "anagrams",
    "context manager", "metaclass", "abstract",
    "overriding", "overloading", "oops", "oop",
    "http method", "http verb", "http status", "put method", "post method", "get method",
    "patch method", "delete method", "http",
    "merge conflict", "merge conflicts",
    "flask", "fastapi", "nginx",
}

INCOMPLETE_ENDINGS = {
    "and", "or", "but", "the", "a", "an", "of", "to", "with", "for",
    "in", "on", "at", "between", "is", "are", "was", "were",
    "can", "could", "would", "should", "will", "do", "does",
}

IGNORE_PATTERNS = [
    # Fillers and acknowledgements
    r"^(okay|ok|alright|sure|yes|no|yeah|right|hmm|um|uh)[\s,.!?]*$",
    r"^(great|good|nice|perfect|thanks|thank you)[\s,.!?]*$",
    # Audio/screen checks
    r"can you hear me", r"is (this|my audio) working",
    r"one (moment|second|minute)", r"let me (think|see|check)",
    r"share.*screen", r"open.*link", r"click on", r"mute",
    r"Microsoft Office Word.*", r"Word\.Document.*", r"MSWordDoc",
    r"you're on mute", r"can you see my screen",
    # Greetings and small talk (not interview questions)
    r"^(hi|hello|hey|bye|goodbye),?\s*([\w]+)?[.!,]?\s*(good\s*(morning|evening|afternoon|night))?[.!,]?\s*$",
    r"^good\s*(morning|evening|afternoon|night)[.!,]?\s*$",
    r"^(hi|hello|hey),?\s*\w+\.\s*(good\s*(morning|evening|afternoon))?",
    r"^(hi|hello|hey),?\s*\w+\.\s*(bye|goodbye),?\s*\w+",
    # Camera, physical, and setup instructions
    r"come\s*(on\s*)?to\s*(the\s*)?camera",
    r"move\s*towards", r"move\s*to\s*(your|the)\s*(left|right)",
    r"place\s*(any|a|the)\s*table", r"table\s*or\s*something",
    r"(face|eye)\s*contact", r"not\s*able\s*to\s*see\s*(the|your)\s*face",
    r"(above|below|behind)\s*light", r"light\s*is\s*there",
    r"(your|the)\s*(camera|webcam|video)\s*(is|position|focus|angle)",
    r"focus\s*slide\s*position", r"slide\s*position",
    # Physical instructions: light, holding, positioning
    r"light\s*is\s*coming\s*from\s*(the\s*)?(top|bottom|side|above|behind)",
    r"(your\s*)?face\s*(is\s*)?(really\s*)?(not\s*)?(visible|clear|showing)\b",
    r"can\s*you\s*hold\s*(it|the|this)\b",
    r"(hold|keep)\s*(it|the|this|camera|laptop|phone|light)\s*(up|down|on\s*top|there|still|higher|lower)",
    r"\blittle\s*(more|higher|lower|up|down)\s*[?,]",
    r"take\s*(a\s*)?(snapshot|photo|picture|screenshot)\s*(of|now)?",
    r"keep\s*(the\s*)?(laptop|camera|phone|light|it)\s*(down|up|there|now)\b",
    r"(adjust|position|fix)\s*(your\s*)?(camera|light|lighting)\b",
    r"sit\s*(to|towards)\s*(the\s*)?(light|camera|left|right)",
    # End-of-interview chatter
    r"(we\s*will\s*)?let\s*you\s*know\b",
    r"thank\s*you\s*for\s*(your\s*)?time",
    r"any\s*questions\s*(from|for)\s*(you|your\s*side)",
    # Recording/compliance setup
    r"record\s*(the|this)\s*session", r"hope\s*you.*(re|are)\s*comfortable",
    r"compliance\s*and\s*audit", r"as\s*it\s*is\s*a\s*compliance",
    # Coordinator/scheduling talk
    r"waiting\s*for\s*(your|the)\s*confirmation",
    r"(is\s*it|that)\s*fine\??\s*(can\s*I|shall)", r"can\s*I\s*change\s*the\s*time",
    r"getting\s*another\s*call", r"stopped\s*recruiting",
    r"want\s*(to|you)\s*arrange", r"you\s*want\s*(to|any)\s*changes",
    r"(I|we)\s*(have|are)\s*done\s*from\s*(my|our)\s*side",
    r"anything\s*else\s*from\s*(your|his|her)\s*side",
    r"now\s*it'?s?\s*perfect", r"it\s*is\s*like\s*not\s*good",
    r"last\s*time.*said.*good\s*now",
    # Non-question interviewer statements (not directed at candidate)
    r"^(so|okay),?\s*\w+,?\s*we\s*(are|were)",
    r"^yeah,?\s*(yeah,?\s*)?now",
    # Meeting platform notifications (Google Meet, Teams, Zoom)
    r"joined the (meeting|conversation|call)",
    r"left the (meeting|conversation|call)",
    r"(meeting|call)\s*(started|ended|recorded)",
    r"recording\s*(started|stopped|in progress)",
    r"is presenting",
    r"named the meeting",
    r"created this meeting",
    r"muted their (microphone|mic)",
]

COMPILED_IGNORE = [re.compile(p, re.IGNORECASE) for p in IGNORE_PATTERNS]


# =============================================================================
# HALLUCINATION DETECTION
# =============================================================================

def is_hallucination(text: str) -> bool:
    """Detect Whisper hallucinations (repeated phrases during silence)."""
    if not text or len(text) < 20:
        return False

    lower = text.lower().strip()
    words = lower.split()

    if len(words) > 15:
        unique = len(set(words))
        if unique < 5:
            return True
        if len(words) / unique > 3:
            return True

    parts = [p.strip() for p in lower.split(',') if p.strip()]
    if len(parts) >= 3:
        counts = Counter(parts)
        if counts.most_common(1)[0][1] >= 3:
            return True

    if len(words) >= 8:
        bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words)-1)]
        bigram_counts = Counter(bigrams)
        if bigram_counts.most_common(1)[0][1] >= 4:
            return True

    return False


# =============================================================================
# MAIN VALIDATION
# =============================================================================

def validate_question(text: str) -> Tuple[bool, str, str]:
    """
    Validate if text is an interview question.
    Returns: (is_valid, cleaned_text, rejection_reason)
    """
    if not text:
        return False, "", "empty"

    text = text.strip()

    # Strip common noise prefixes FIRST (before STT corrections, so corrections
    # can match start-of-string patterns like ^right\s+here)
    noise_prefixes = [
        r"^(?:async\s+out\s+there|out\s+there|over\s+there)\.?\s*",
        r"^(?:yeah|yes|okay|ok|so|and|but|now)\s*,?\s+(?=[A-Z])",
    ]
    for prefix_pattern in noise_prefixes:
        text = re.sub(prefix_pattern, "", text, flags=re.IGNORECASE).strip()

    # Apply STT corrections AFTER noise stripping
    text = apply_stt_corrections(text)

    if is_hallucination(text):
        return False, "", "hallucination"

    if is_youtube_or_tutorial(text):
        return False, "", "youtube_tutorial"

    for pattern in COMPILED_IGNORE:
        if pattern.search(text):
            return False, "", "ignore_pattern"

    words = text.split()
    if len(words) < 2:
        return False, "", "too_short"

    # Reject vague pronoun-only questions (e.g., "How do you implement it?")
    if is_vague_question(text):
        return False, "", "vague_pronoun_only"

    lower = text.lower()

    last_word = words[-1].rstrip("?.,!").lower()
    if last_word in INCOMPLETE_ENDINGS and not text.endswith("?"):
        return False, "", "incomplete"

    has_starter = any(lower.startswith(s) or f" {s}" in lower for s in QUESTION_STARTERS)
    has_tech = any(t in lower for t in TECH_TERMS)
    has_question_mark = "?" in text

    # Reject very short questions with no tech term (e.g. "What is?", "How?")
    if len(words) <= 3 and not has_tech and has_question_mark:
        return False, "", "too_vague"

    # Reject questions with only vague/filler words and no tech term
    vague_filler = {"what", "about", "the", "other", "one", "that", "this",
                    "it", "those", "these", "how", "why", "where", "which",
                    "is", "are", "do", "does", "can", "could", "would", "should",
                    "a", "an", "of", "for", "and", "or", "some", "any", "just"}
    content_words = [w.rstrip("?.,!") for w in words if w.rstrip("?.,!").lower() not in vague_filler]
    if not content_words and not has_tech:
        return False, "", "too_vague"

    # HR/behavioral interview questions count as interview-relevant
    hr_patterns = ["yourself", "your experience", "your background", "your responsibility",
                   "looking for change", "looking for a change", "why are you leaving",
                   "still working", "left this organization", "left this company",
                   "left this job", "left your previous", "left your last",
                   "have you left",
                   "notice period", "current ctc", "expected ctc", "salary",
                   "years of experience", "why do you want", "strengths", "weaknesses",
                   "tell me about", "walk me through", "your role", "your team",
                   "current organization", "previous organization", "latest organization",
                   "go ahead about", "about your"]
    if any(p in lower for p in hr_patterns):
        has_tech = True

    is_coding_question = False
    if re.search(r'\b\w+\s*=\s*\[', text):
        is_coding_question = True
    if "find" in lower:
        is_coding_question = True
    coding_words = ['sort', 'reverse', 'sum', 'max', 'min', 'count', 'even', 'odd', 'prime', 'duplicate',
                    'fibonacci', 'palindrome', 'missing', 'largest', 'smallest', 'average',
                    'slicing', 'slice', 'comprehension', 'factorial', 'swap', 'matrix',
                    'binary', 'search', 'linked', 'stack', 'queue', 'hash', 'tree']
    if any(w in lower for w in coding_words):
        is_coding_question = True

    # Interview relevance check: reject casual/setup questions with no tech content
    # Only include words that are UNAMBIGUOUSLY non-interview (no double meanings)
    non_interview_words = {'camera', 'webcam', 'table', 'arrange', 'comfortable',
                           'recording', 'audible', 'visible', 'mute', 'unmute',
                           'confirmation', 'slide position', 'focus slide',
                           'sit', 'stand'}
    non_interview_phrases = [
        'come on to the camera', 'move towards', 'place any table',
        'eye contact', 'above light', 'is it fine', 'want to arrange',
        'from my side', 'from your side', 'anything else from',
        'now it\'s perfect', 'not good properly', 'can I change the time',
    ]
    has_non_interview = (any(w in lower for w in non_interview_words) or
                         any(p in lower for p in non_interview_phrases)) and not has_tech

    if has_starter and has_tech:
        pass
    elif has_question_mark and len(words) >= 3 and not has_non_interview:
        pass
    elif has_starter and len(words) >= 2 and not has_non_interview:
        pass
    elif has_tech and len(words) >= 6:
        pass
    elif is_coding_question:
        pass
    else:
        return False, "", "no_question_pattern"

    cleaned = text[0].upper() + text[1:] if len(text) > 1 else text

    if has_starter and not cleaned.endswith(("?", ".", "!")):
        cleaned += "?"

    return True, cleaned, ""


def clean_and_validate(text: str) -> Tuple[bool, str, str]:
    """Alias for validate_question."""
    return validate_question(text)


def is_valid_interview_question(text: str) -> bool:
    """Simple boolean check."""
    is_valid, _, _ = validate_question(text)
    return is_valid


# =============================================================================
# QUESTION SPLITTING
# =============================================================================

def split_merged_questions(text: str) -> str:
    """Extract the best question from merged audio."""
    if not text:
        return text

    text = text.strip()
    lower = text.lower()

    positions = []
    for starter in QUESTION_STARTERS:
        idx = 0
        while True:
            pos = lower.find(starter, idx)
            if pos == -1:
                break
            if pos == 0 or text[pos-1] in ' ,.':
                positions.append((pos, starter))
            idx = pos + 1

    if len(positions) < 2:
        return text

    positions.sort()

    for pos, starter in reversed(positions):
        candidate = text[pos:].strip()
        if len(candidate.split()) >= 4:
            return candidate

    return text


_is_whisper_hallucination = is_hallucination


def is_code_request(text: str) -> bool:
    """Check if question explicitly asks for code/script output.

    Must be conservative - only trigger for clear "write code" requests,
    not for questions that mention code-related words in passing.
    """
    if not text:
        return False
    lower = text.lower().strip()

    # If the user explicitly asks for an explanation, it's NOT a code request
    explanation_triggers = [
        "explain", "describe", "concept", "theory", "what is the difference",
        "difference between", "what is", "what are", "what does", "how does",
        "how do", "how to deploy", "how to set up", "how to configure",
        "how to monitor", "how to troubleshoot", "how to scale",
        "how to manage", "how to handle", "how to secure",
        "why", "when would", "tell me", "what will", "what if",
        "do we need", "can you", "is it", "those are", "status code",
        "time complexity", "send", "chat box", "chat book",
        "all the available", "available playbooks", "list the",
    ]
    if any(lower.startswith(t) for t in explanation_triggers):
        return False
    # Also reject if it's a conversational/follow-up question
    if any(p in lower for p in ["send this", "send me", "in the chat", "chat box", "chat book",
                                  "time complexity", "those are", "status code",
                                  "do we need", "is it the", "what will be"]):
        return False

    # Only trigger for explicit "write code/program/function" requests
    explicit_code_phrases = [
        "write code", "write a code", "write the code for",
        "write a function", "write a program", "write a script",
        "write a method", "write a class", "write a generator",
        "write script", "write a query", "code for decorator",
        "code for palindrome", "code for fibonacci",
        "simple code for", "write simple code",
        "define a class", "define a function", "define a method",
        "define a generator", "define class", "define function",
        "create a class", "create a function", "create a method",
        "implement a function", "implement a class", "implement a method",
        "use a list comprehension", "use list comprehension",
        "yaml script", "ansible playbook", "terraform script",
        "groovy script", "jenkinsfile", "dockerfile", "docker-compose",
        "sql query",
    ]
    if any(p in lower for p in explicit_code_phrases):
        return True

    # "Write ... code/function/method" pattern (e.g. "Write me a decorator code")
    if re.search(r'\bwrite\b.*\b(code|function|program|script|query|method|class)\b', lower):
        return True

    # "Define ... class/function/method" pattern
    if re.search(r'\bdefine\b.*\b(class|function|method|generator)\b', lower):
        return True

    # NEW: Implicit code requests - questions that clearly expect code output
    # Pattern: "find/get/return/calculate/reverse/sort/check ... [data structure/algorithm term]"
    implicit_code_verbs = [
        "find", "get", "return", "calculate", "compute", "reverse",
        "sort", "check", "validate", "convert", "transform", "merge",
        "filter", "remove", "delete", "insert", "add", "count",
        "sum", "multiply", "divide", "swap", "rotate", "flatten",
        "group", "split", "join", "search", "detect", "extract"
    ]
    
    # Algorithm/data structure terms that indicate coding
    coding_context_terms = [
        "anagram", "palindrome", "fibonacci", "factorial", "prime",
        "even", "odd", "duplicate", "unique", "missing", "largest",
        "smallest", "maximum", "minimum", "average", "median",
        "list", "array", "string", "dict", "dictionary", "set",
        "tree", "linked list", "stack", "queue", "heap", "graph",
        "matrix", "binary", "hash", "sorted", "unsorted",
        "ascending", "descending", "recursive", "iterative"
    ]
    
    # Check if question has implicit code pattern: verb + coding term
    has_code_verb = any(f"{verb} " in lower or lower.startswith(verb) for verb in implicit_code_verbs)
    has_coding_term = any(term in lower for term in coding_context_terms)
    
    if has_code_verb and has_coding_term:
        return True
    
    # Pattern: "by passing [data structure]" - common in coding questions
    if re.search(r'\bby passing\b.*(list|array|string|dict)', lower):
        return True
    
    # Pattern: variable assignment in question (e.g., "str = ['eat', 'cat']")
    if re.search(r'\b\w+\s*=\s*[\[\{"\']', lower):
        return True

    return False



if __name__ == "__main__":
    tests = [
        ("What is a class in Python?", True),
        ("Explain decorators", True),
        ("Difference between list and tuple", True),
        ("How does garbage collection work?", True),
        ("Tell me about yourself", True),
        ("What is, What is, What is, What is", False),
        ("Okay", False),
        ("Can you hear me?", False),
        ("the", False),
        ("What is the", False),
        # YouTube detection
        ("In this video we will learn about Python decorators", False),
        ("Subscribe to my channel for more tutorials", False),
        ("Let's get started with today's tutorial", False),
        ("Hey guys welcome to my Python course", False),
        ("Don't forget to like and subscribe", False),
        # Vague pronoun-only questions
        ("How do you implement it?", False),
        ("Can you explain that?", False),
        ("What does it do?", False),
        # STT correction: "A, C, D" -> "CI/CD"
        ("What is a, c, d?", True),
        ("What is A C D and how do you implement it in your project?", True),
    ]

    print("=" * 50)
    print("QUESTION VALIDATOR TEST")
    print("=" * 50)

    passed = 0
    for text, expected in tests:
        is_valid, cleaned, reason = validate_question(text)
        status = "PASS" if is_valid == expected else "FAIL"
        if is_valid == expected:
            passed += 1
        print(f"{status} '{text[:50]}' -> valid={is_valid} (expected={expected})")
        if reason:
            print(f"   Reason: {reason}")

    print(f"\n{passed}/{len(tests)} tests passed")
