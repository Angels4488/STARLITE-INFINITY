#!/bin/bash

# Backdoor Scanner - Hunt for hidden backdoors and malware

echo "🔍 Scanning for backdoors..."

# Install scanning tools
apt install -y clamav clamav-daemon maldet lynis

# Update virus definitions
freshclam

# Full system scan
clamscan -r / --exclude-dir=/sys --exclude-dir=/proc --exclude-dir=/dev --log=/var/log/clamav_scan.log

# Malware detect scan
maldet -a / | tail -20

# Lynis security audit
lynis audit system --quiet

# Check for suspicious cron jobs
echo "Checking cron jobs..."
crontab -l
ls -la /etc/cron.*

# Check for suspicious services
echo "Checking services..."
systemctl list-units --type=service --state=running | grep -E "(unknown|suspicious)"

# Check for hidden users
echo "Checking users..."
awk -F: '{ if ($3 >= 1000 && $3 < 65534) print $1 }' /etc/passwd

# Check for world-writable files
echo "Checking world-writable files..."
find / -type f -perm -o+w 2>/dev/null | head -20

# Check for SUID/SGID binaries
echo "Checking SUID/SGID files..."
find / -type f \( -perm -4000 -o -perm -2000 \) 2>/dev/null | head -20

# Check listening ports
echo "Checking listening ports..."
netstat -tlnp | grep LISTEN

echo "✅ Backdoor scan complete - check logs for details"