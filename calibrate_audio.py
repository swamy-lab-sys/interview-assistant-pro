
import subprocess
import os
import time
import numpy as np
import select

def test_source(idx, name):
    print(f"Testing ID {idx} ({name})...")
    # Try different capture methods
    cmds = [
        f"gst-launch-1.0 -q pipewiresrc path={idx} ! audioconvert ! audioresample ! audio/x-raw,rate=16000,channels=1,format=F32LE ! fdsink fd=1",
        f"parec -d {idx} --format=float32le --rate=16000 --channels=1"
    ]
    
    for cmd in cmds:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, shell=True, bufsize=0)
        start = time.time()
        vol_sum = 0
        chunks = 0
        
        try:
            while time.time() - start < 1.0:
                r, _, _ = select.select([p.stdout], [], [], 0.2)
                if r:
                    data = p.stdout.read(4800)
                    if data:
                        vol = np.sqrt(np.mean(np.frombuffer(data, dtype=np.float32)**2))
                        vol_sum += vol
                        chunks += 1
            
            p.terminate()
            if chunks > 0:
                avg_vol = vol_sum / chunks
                print(f"  -> CMD: {cmd[:15]}... Avg Vol: {avg_vol:.6f}")
                if avg_vol > 0.0005:
                    return cmd
        except:
            try: p.terminate()
            except: pass
    return None

print("PLAY YOUTUBE NOW! CALIBRATING IN 3s...")
time.sleep(3)

try:
    sources = subprocess.check_output(['pactl', 'list', 'short', 'sources'], text=True)
    for line in sources.split('\n'):
        if 'monitor' in line.lower():
            parts = line.split('\t')
            if len(parts) >= 2:
                idx = parts[0]
                name = parts[1]
                cmd = test_source(idx, name)
                if cmd:
                    print(f"\nSUCCESS! USE THIS: {cmd}")
except Exception as e:
    print(e)
