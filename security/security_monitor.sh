#!/bin/bash

# Security Monitor - Continuous threat detection

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

case "$1" in
    start)
        echo "🛡️  Starting security monitoring..."

        # Create monitoring script
        cat > /usr/local/bin/starlight_security_monitor << 'EOF'
#!/bin/bash
while true; do
    # Check system integrity every hour
    bash /home/archangel/STARLITE-INFINITY/security/system_integrity_check.sh > /var/log/starlight_security.log 2>&1

    # Check firewall status
    ufw status | grep -q "Status: active" || echo "WARNING: Firewall disabled!" >> /var/log/starlight_security.log

    # Check for suspicious logins
    last | grep -E "(unknown|invalid)" >> /var/log/starlight_security.log

    # Check disk usage (prevent DoS)
    df -h | awk '$5 > 90 {print "WARNING: High disk usage on " $1}' >> /var/log/starlight_security.log

    sleep 3600  # Check every hour
done
EOF

        chmod +x /usr/local/bin/starlight_security_monitor

        # Start as systemd service
        cat > /etc/systemd/system/starlight-security.service << EOF
[Unit]
Description=StarLight Security Monitor
After=network.target

[Service]
ExecStart=/usr/local/bin/starlight_security_monitor
Restart=always
User=root

[Install]
WantedBy=multi-user.target
EOF

        systemctl daemon-reload
        systemctl enable starlight-security
        systemctl start starlight-security

        echo "✅ Security monitoring started"
        ;;

    stop)
        systemctl stop starlight-security
        systemctl disable starlight-security
        rm -f /etc/systemd/system/starlight-security.service
        systemctl daemon-reload
        echo "🛑 Security monitoring stopped"
        ;;

    status)
        systemctl status starlight-security
        echo ""
        echo "Recent security log:"
        tail -20 /var/log/starlight_security.log
        ;;

    *)
        echo "Usage: $0 {start|stop|status}"
        ;;
esac