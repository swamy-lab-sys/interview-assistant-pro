import subprocess
import time
import os

def get_monitors():
    result = subprocess.run(['pactl', 'list', 'short', 'sources'], capture_output=True, text=True)
    monitors = []
    for line in result.stdout.splitlines():
        name = line.split()[1]
        if 'monitor' in name:
            monitors.append(name)
    return monitors

monitors = get_monitors()
print(f"Recording from {len(monitors)} monitors...")

processes = []
for i, m in enumerate(monitors):
    out_file = f"/tmp/test_monitor_{i}.wav"
    cmd = ["parec", "-d", m, "--format=s16le", "--rate=16000", "--channels=1"]
    print(f"  {i}: {m} -> {out_file}")
    f = open(f"/tmp/test_monitor_{i}.raw", "wb")
    p = subprocess.Popen(cmd, stdout=f, stderr=subprocess.DEVNULL)
    processes.append((p, f, m, i))

time.sleep(5)

for p, f, m, i in processes:
    p.terminate()
    f.close()
    # Convert to wav for easy checking
    raw_file = f"/tmp/test_monitor_{i}.raw"
    wav_file = f"/tmp/test_monitor_{i}.wav"
    subprocess.run(["sox", "-r", "16000", "-c", "1", "-b", "16", "-e", "signed-integer", raw_file, wav_file], stderr=subprocess.DEVNULL)
    
    # Check size
    if os.path.exists(wav_file):
        size = os.path.getsize(wav_file)
        print(f"Captured {m}: {size} bytes")
    
print("Done. Check files in /tmp/test_monitor_*.wav")
