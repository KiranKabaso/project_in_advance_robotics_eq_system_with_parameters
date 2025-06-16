import psutil
import os
import signal
import time
import logging

# === CONFIGURATION ===
PID: int = 905                         # Replace with your actual process ID
STOP_THRESHOLD_MB: int = 150          # Pause if avail mem is below this
RESUME_THRESHOLD_MB: int = 220        # Resume if avail mem goes above this
SWAP_WAKEUP_INTERVAL_SEC: int = 30    # Interval to resume briefly while paused
BRIEF_RESUME_DURATION_SEC: int = 5    # How long to resume temporarily
EMERGENCY_STOP_MB: int = 70          # Force stop if memory drops below this

# === Logging Setup ===
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

def get_available_memory_mb() -> float:
  return psutil.virtual_memory().available / (1024 * 1024)

def is_stopped(pid: int) -> bool:
  try:
    return psutil.Process(pid).status() == psutil.STATUS_STOPPED
  except psutil.NoSuchProcess:
    return False

def encourage_swapping(pid: int) -> None:
  try:
    with open(f"/proc/{pid}/clear_refs", "w") as f:
      f.write("1")  # Mark all memory pages as "not recently accessed"
    logging.info("Encouraged swap: cleared accessed memory flags")
  except Exception as e:
    logging.warning(f"Could not write to clear_refs for PID {pid}: {e}")

def main() -> None:
  if not psutil.pid_exists(PID):
    logging.error(f"PID {PID} not found.")
    return

  logging.info(f"Managing PID {PID}")
  last_swap_trigger_time = 0

  while psutil.pid_exists(PID):
    avail_mb = get_available_memory_mb()
    status = 'stopped' if is_stopped(PID) else 'running'
    logging.info(f"Available Memory: {avail_mb:.1f} MiB | Status: {status}")

    now = time.time()

    # 🚨 Emergency hard stop
    if avail_mb < EMERGENCY_STOP_MB:
      logging.critical("Emergency: Memory critically low (<100 MiB) — force-stopping process!")
      if not is_stopped(PID):
        try:
          os.kill(PID, signal.SIGSTOP)
        except ProcessLookupError:
          logging.warning("Process already exited")
          break
      last_swap_trigger_time = now
      time.sleep(2)
      continue

    # 🔻 Regular stop if under threshold
    if avail_mb < STOP_THRESHOLD_MB and not is_stopped(PID):
      logging.warning("Memory low — pausing process")
      try:
        os.kill(PID, signal.SIGSTOP)
      except ProcessLookupError:
        logging.warning("Process already exited")
        break
      last_swap_trigger_time = now

    # 🔁 Periodic swap encouragement
    elif avail_mb < RESUME_THRESHOLD_MB and is_stopped(PID):
      if now - last_swap_trigger_time >= SWAP_WAKEUP_INTERVAL_SEC:
        logging.info("Resuming briefly to trigger swap...")
        try:
          os.kill(PID, signal.SIGCONT)
          time.sleep(BRIEF_RESUME_DURATION_SEC)
          encourage_swapping(PID)
          os.kill(PID, signal.SIGSTOP)
        except ProcessLookupError:
          logging.warning("Process already exited")
          break
        last_swap_trigger_time = now

    # 🔼 Resume if memory is healthy
    elif avail_mb >= RESUME_THRESHOLD_MB and is_stopped(PID):
      logging.info("Memory recovered — resuming process")
      try:
        os.kill(PID, signal.SIGCONT)
      except ProcessLookupError:
        logging.warning("Process already exited")
        break

    time.sleep(2)

  logging.info("Process has exited — monitor stopped.")

if __name__ == "__main__":
  main()
