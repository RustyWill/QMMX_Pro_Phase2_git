# start_qmmx.py — convenience launcher (optional; you can still run scripts separately)
import subprocess, sys, time, os, signal

PY = sys.executable
procs = []

def spawn(script):
    return subprocess.Popen([PY, script], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

def main():
    try:
        print("[QMMX] Running migrations...")
        subprocess.check_call([PY, 'migrate.py'])
        print("[QMMX] Starting ml_engine.py...")
        procs.append(spawn('ml_engine.py'))
        time.sleep(1.5)
        print("[QMMX] Starting app.py...")
        procs.append(spawn('app.py'))
        print("[QMMX] All processes launched. Press Ctrl+C to stop.\n")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[QMMX] Shutting down...")
    finally:
        for p in procs:
            try:
                if p.poll() is None:
                    if os.name == 'nt':
                        p.send_signal(signal.CTRL_BREAK_EVENT)
                    p.terminate()
            except Exception:
                pass

if __name__ == '__main__':
    main()
