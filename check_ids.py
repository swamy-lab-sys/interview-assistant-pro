
import subprocess
import time
import numpy as np

def get_rms(device_id):
    cmd = f"timeout 2s gst-launch-1.0 -q pipewiresrc path={device_id} ! audioconvert ! audioresample ! audio/x-raw,rate=16000,channels=1,format=F32LE ! fdsink fd=1"
    try:
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        data = proc.stdout.read(16000 * 4 * 1) # 1 sec
        proc.terminate()
        if not data: return 0.0
        nums = np.frombuffer(data, dtype=np.float32)
        return np.sqrt(np.mean(nums**2))
    except:
        return 0.0

print("CHECKING VOLUME ON 52 (Monitor) and 54 (Mic)...")
print("Please play YouTube now!")
time.sleep(1)
v52 = get_rms(52)
v54 = get_rms(54)
print(f"ID 52 (System Monitor) Volume: {v52:.6f}")
print(f"ID 54 (Digital Mic)     Volume: {v54:.6f}")
