
import subprocess
import os
import sys
import numpy as np
import select
import time

# Use the ID 52 which we know works
device = "52"
target_str = f"path={device}"
cmd = f"gst-launch-1.0 -q pipewiresrc {target_str} ! audioconvert ! audioresample ! audio/x-raw,rate=16000,channels=1,format=F32LE ! fdsink fd=1"

print(f"Testing Command: {cmd}")
print("Playing YouTube? (Wait 2s then check)")
time.sleep(2)

process = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    bufsize=0,
    shell=True
)

CHUNK_SIZE = 480 # 30ms
bytes_to_read = CHUNK_SIZE * 4
start_time = time.time()
chunks_received = 0

try:
    while time.time() - start_time < 5:
        r, _, _ = select.select([process.stdout], [], [], 0.5)
        if not r:
            print("No data ready yet...")
            continue
            
        data = process.stdout.read(bytes_to_read)
        if not data:
            print("EOF reached")
            break
            
        chunks_received += 1
        if chunks_received % 10 == 0:
            vol = np.sqrt(np.mean(np.frombuffer(data, dtype=np.float32)**2))
            print(f"Received {chunks_received} chunks... Current volume: {vol:.6f}")

    if chunks_received == 0:
        err = process.stderr.read().decode()
        print(f"FAILED. Error: {err}")
    else:
        print(f"SUCCESS. Received {chunks_received} chunks total.")

finally:
    process.terminate()
