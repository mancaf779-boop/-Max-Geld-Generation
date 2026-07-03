/**
 * A minimal interval scheduler. Not cron — just setInterval with guarded
 * start/stop, so both the server and the CLI can share one implementation.
 */
function createScheduler(fn, intervalMs) {
  let timer = null;
  let runCount = 0;

  return {
    start() {
      if (timer) return false;
      timer = setInterval(async () => {
        runCount += 1;
        await fn(runCount);
      }, intervalMs);
      if (typeof timer.unref === "function") timer.unref();
      return true;
    },
    stop() {
      if (!timer) return false;
      clearInterval(timer);
      timer = null;
      return true;
    },
    isRunning() {
      return timer !== null;
    },
    get runCount() {
      return runCount;
    },
  };
}

module.exports = { createScheduler };
