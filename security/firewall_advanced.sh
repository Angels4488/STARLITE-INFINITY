#!/bin/bash

# Advanced Firewall Setup - Fort Knox protection

echo "🔥 Setting up advanced firewall..."

# Install ufw if not present
apt install -y ufw

# Reset firewall
ufw --force reset
ufw --force enable

# Default policies
ufw default deny incoming
ufw default allow outgoing

# Allow essential services
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp

# Block common attack ports
ufw deny 23/tcp    # Telnet
ufw deny 21/tcp    # FTP
ufw deny 25/tcp    # SMTP (block spam)
ufw deny 53/udp    # DNS (use local resolver)
ufw deny 137:139/tcp  # NetBIOS
ufw deny 445/tcp   # SMB
ufw deny 3389/tcp  # RDP

# Block ICMP echo (ping) to prevent reconnaissance
ufw deny icmp echo-request

# Rate limiting for SSH
ufw limit ssh/tcp

# Allow local network traffic
ufw allow from 192.168.0.0/16
ufw allow from 10.0.0.0/8
ufw allow from 172.16.0.0/12

# Block all other incoming
ufw --force enable

# Show status
ufw status verbose

echo "✅ Advanced firewall configured"