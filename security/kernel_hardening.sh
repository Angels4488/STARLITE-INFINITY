#!/bin/bash

# Kernel Hardening - Lock down the kernel

echo "🔧 Hardening kernel security..."

# Backup current sysctl
cp /etc/sysctl.conf /etc/sysctl.conf.backup

# Add hardening parameters
cat >> /etc/sysctl.conf << EOF

# StarLight Kernel Hardening
# Disable IP forwarding (unless needed)
net.ipv4.ip_forward = 0
net.ipv6.conf.all.forwarding = 0

# Disable source routing
net.ipv4.conf.all.accept_source_route = 0
net.ipv6.conf.all.accept_source_route = 0

# Disable ICMP redirects
net.ipv4.conf.all.accept_redirects = 0
net.ipv6.conf.all.accept_redirects = 0

# Enable TCP SYN cookies
net.ipv4.tcp_syncookies = 1

# Disable core dumps
fs.suid_dumpable = 0
kernel.core_uses_pid = 1

# Restrict dmesg access
kernel.dmesg_restrict = 1

# Disable kptr_restrict for security
kernel.kptr_restrict = 2

# Randomize VA space
kernel.randomize_va_space = 2

# Restrict ptrace
kernel.yama.ptrace_scope = 2

# Disable unprivileged user namespaces
kernel.unprivileged_userns_clone = 0

# Enable ASLR
kernel.randomize_va_space = 2
EOF

# Apply settings
sysctl -p

# Install kernel hardening tools
apt install -y paxctl grsecurity

# Configure paxctl for additional hardening
# This would require specific binary configuration

echo "✅ Kernel hardened"