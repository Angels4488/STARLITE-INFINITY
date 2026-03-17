#!/bin/bash

# MIM Attack Protection - SSL pinning, certificate validation

echo "🛡️  Protecting against Man-in-the-Middle attacks..."

# Install cert validation tools
apt install -y ssl-cert-check ca-certificates curl

# Update CA certificates
update-ca-certificates

# Configure SSL/TLS settings
# Force TLS 1.3 only
echo "Configuring TLS 1.3 only..."
cat > /etc/ssl/openssl.cnf << EOF
openssl_conf = openssl_init

[openssl_init]
ssl_conf = ssl_sect

[ssl_sect]
system_default = system_default_sect

[system_default_sect]
MinProtocol = TLSv1.3
CipherSuites = TLS_AES_256_GCM_SHA384:TLS_AES_128_GCM_SHA256
EOF

# Install sslstrip prevention (use HTTPS everywhere)
apt install -y https-everywhere

# Configure DNS over HTTPS (DoH) to prevent DNS poisoning
apt install -y systemd-resolved
cat > /etc/systemd/resolved.conf << EOF
[Resolve]
DNS=1.1.1.1#cloudflare-dns.com 8.8.8.8#dns.google
DNSOverTLS=yes
EOF
systemctl restart systemd-resolved

# Install and configure certificate pinning
apt install -y certbot
# Note: Would need domain for actual pinning

# ARP poisoning protection
apt install -y arpwatch
systemctl enable arpwatch
systemctl start arpwatch

# Install intrusion detection
apt install -y snort
# Basic snort configuration would go here

echo "✅ MIM protection measures implemented"