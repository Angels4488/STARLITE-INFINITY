#!/bin/bash

# Network Security - Advanced network protection

echo "🌐 Securing network layer..."

# Install network security tools
apt install -y nmap wireshark tcpdump snort suricata fail2ban

# Configure fail2ban for SSH protection
systemctl enable fail2ban
systemctl start fail2ban

# Configure Suricata IDS
cat > /etc/suricata/suricata.yaml << EOF
%YAML 1.1
---

# StarLight Suricata Configuration
vars:
  address-groups:
    HOME_NET: "[192.168.0.0/16,10.0.0.0/8,172.16.0.0/12]"

  port-groups:
    HTTP_PORTS: "80"
    SHELLCODE_PORTS: "!80"
    ORACLE_PORTS: 1521
    SSH_PORTS: 22

default-rule-path: /var/lib/suricata/rules
rule-files:
  - suricata.rules

classification-file: /etc/suricata/classification.config
reference-config-file: /etc/suricata/reference.config

EOF

# Enable Suricata
systemctl enable suricata
systemctl start suricata

# Configure DNSSEC
apt install -y dnssec-tools
# DNSSEC configuration would go here

# Install and configure OpenVPN for secure remote access
apt install -y openvpn easy-rsa

# Set up basic OpenVPN (would need certificates)
# This is a placeholder for full VPN setup

# Configure iptables for additional protection
iptables -A INPUT -m state --state INVALID -j DROP
iptables -A INPUT -p tcp --tcp-flags ALL NONE -j DROP
iptables -A INPUT -p tcp ! --syn -m state --state NEW -j DROP

# Save iptables rules
iptables-save > /etc/iptables/rules.v4

echo "✅ Network security implemented"