import subprocess
import time
import os
import numpy as np

def get_monitors():
    result = subprocess.run(['pactl', 'list', 'short', 'sources'], capture_output=True, text=True)
    monitors = []
    for line in result.stdout.splitlines():
        name = line.split()[1]
        if 'monitor' in name:
            monitors.append(name)
    return monitors

monitors = get_monitors()
print(f"Recording from {len(monitors)} monitors for 5 seconds...")

processes = []
for i, m in enumerate(monitors):
    raw_file = f"/tmp/test_monitor_{i}.raw"
    cmd = ["parec", "-d", m, "--format=s16le", "--rate=16000", "--channels=1"]
    f = open(raw_file, "wb")
    p = subprocess.Popen(cmd, stdout=f, stderr=subprocess.DEVNULL)
    processes.append((p, f, m, i, raw_file))

time.sleep(5)

for p, f, m, i, raw_file in processes:
    p.terminate()
    f.close()
    
    if os.path.exists(raw_file):
        size = os.path.getsize(raw_file)
        # Read and check RMS
        with open(raw_file, 'rb') as rf:
            data = rf.read()
            if data:
                audio = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
                rms = np.sqrt(np.mean(audio**2))
                print(f"Monitor {i} ({m}): Size={size} bytes, RMS={rms:.6f}")
                if rms > 0.001:
                    print(f"*** FOUND SIGNAL ON MONITOR {i} ***")
            else:
                print(f"Monitor {i} ({m}): Size={size} bytes (Empty)")
    
print("Done.")
