import subprocess
import numpy as np
import time

def get_monitors():
    result = subprocess.run(['pactl', 'list', 'short', 'sources'], capture_output=True, text=True)
    monitors = []
    for line in result.stdout.splitlines():
        if '.monitor' in line:
            monitors.append(line.split()[1])
    return monitors

def check_audio(monitor):
    print(f"Checking {monitor}...")
    try:
        # Record for 2 seconds
        cmd = ["parec", "-d", monitor, "--format=s16le", "--rate=16000", "--channels=1"]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        time.sleep(2)
        proc.terminate()
        data = proc.stdout.read()
        if not data:
            print("  No data received.")
            return 0
        
        audio = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
        rms = np.sqrt(np.mean(audio**2))
        non_zero = np.count_nonzero(audio)
        print(f"  RMS: {rms:.6f}, Non-zero samples: {non_zero}")
        return rms
    except Exception as e:
        print(f"  Error: {e}")
        return 0

monitors = get_monitors()
for m in monitors:
    rms = check_audio(m)
    if rms > 0.0001:
        print(f"*** FOUND ACTIVE SOURCE: {m} ***")
