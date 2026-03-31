#!/bin/bash
# gno-daemon.sh — Control the ABE knowledge base daemon
#
# Usage:
#   bash scripts/gno-daemon.sh start    # Start daemon
#   bash scripts/gno-daemon.sh stop     # Stop daemon
#   bash scripts/gno-daemon.sh restart  # Restart daemon
#   bash scripts/gno-daemon.sh status   # Check if running
#   bash scripts/gno-daemon.sh logs     # Tail the log

PLIST="$HOME/Library/LaunchAgents/com.abe.gno-daemon.plist"
LOG="/Users/lucas/Documents/Pi515/ABE/logs/gno-daemon.log"

case "$1" in
  start)
    launchctl load "$PLIST"
    echo "Daemon started."
    ;;
  stop)
    launchctl unload "$PLIST"
    echo "Daemon stopped."
    ;;
  restart)
    launchctl unload "$PLIST" 2>/dev/null
    launchctl load "$PLIST"
    echo "Daemon restarted."
    ;;
  status)
    launchctl list | grep com.abe.gno && echo "Running." || echo "Not running."
    ;;
  logs)
    tail -f "$LOG"
    ;;
  *)
    echo "Usage: bash scripts/gno-daemon.sh [start|stop|restart|status|logs]"
    ;;
esac
