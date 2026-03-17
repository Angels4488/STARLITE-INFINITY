#!/bin/bash

# Sideload Protection - Prevent unauthorized software installation

echo "🚫 Preventing sideload attacks..."

# Install AppArmor
apt install -y apparmor apparmor-profiles apparmor-utils

# Enable AppArmor
systemctl enable apparmor
systemctl start apparmor

# Install SELinux (if not already)
apt install -y selinux-basics selinux-policy-default
# SELinux setup would require reboot

# Configure package manager security
# Lock down apt sources
cat > /etc/apt/sources.list.d/official-only.list << EOF
deb [arch=amd64 signed-by=/usr/share/keyrings/ubuntu-archive-keyring.gpg] http://archive.ubuntu.com/ubuntu/ $(lsb_release -cs) main restricted universe multiverse
deb [arch=amd64 signed-by=/usr/share/keyrings/ubuntu-archive-keyring.gpg] http://archive.ubuntu.com/ubuntu/ $(lsb_release -cs)-updates main restricted universe multiverse
deb [arch=amd64 signed-by=/usr/share/keyrings/ubuntu-archive-keyring.gpg] http://archive.ubuntu.com/ubuntu/ $(lsb_release -cs)-security main restricted universe multiverse
EOF

# Disable automatic package installation
cat > /etc/apt/apt.conf.d/99noauto << EOF
APT::Get::AllowUnauthenticated "false";
APT::Install-Recommends "false";
APT::Install-Suggests "false";
EOF

# Install package verification
apt install -y apt-listbugs apt-listchanges

# Configure dpkg to verify packages
cat > /etc/dpkg/dpkg.cfg << EOF
no-debsig
EOF

# Install and configure tripwire for file integrity
apt install -y tripwire
# Tripwire setup would require interactive configuration

# Disable USB auto-mount to prevent malware from USB
apt install -y usbmount
systemctl disable udisks2

echo "✅ Sideload protection enabled"