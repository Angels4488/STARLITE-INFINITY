#!/bin/bash

# System Integrity Check - Detect rootkits, file changes, anomalies

echo "🔍 Checking system integrity..."

# Install required tools if not present
apt update && apt install -y rkhunter chkrootkit aide debsums

# Run rootkit checks
echo "Scanning for rootkits..."
rkhunter --check --sk
chkrootkit

# File integrity check
echo "Checking file integrity..."
debsums -c

# AIDE database init/update
if [ ! -f /var/lib/aide/aide.db ]; then
    aideinit
    mv /var/lib/aide/aide.db.new /var/lib/aide/aide.db
else
    aide --check
fi

# Check for suspicious processes
echo "Checking for suspicious processes..."
ps aux | grep -E "(netcat|nc|ncat|socat|backdoor|trojan)" | grep -v grep

# Check for hidden files in common directories
echo "Checking for hidden files..."
find /etc /bin /sbin /usr/bin /usr/sbin -name ".*" -type f 2>/dev/null | head -20

# Check system logs for anomalies
echo "Checking system logs..."
journalctl -p err --since "1 hour ago" | tail -10

echo "✅ System integrity check complete"