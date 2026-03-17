import os
import subprocess
import re

class AGIRatTrap:
    """
    Experimental Forensic Module: Correlates System Audits with
    Network Sockets to identify unauthorized data exfiltration attempts.
    """
    def __init__(self):
        self.audit_log = "/var/log/syslog"
        # Mapping syscall 141 (getpeername) as it appeared in your report
        self.target_syscall = "141"

    def get_active_pids_from_network(self):
        print("[TRAP] Analyzing network listeners...")
        pids = set()
        try:
            # Using ss with -p to get process info
            output = subprocess.check_output(["ss", "-tulpn"], text=True)
            # Regex to grab PIDs from the 'users' column
            found_pids = re.findall(r"pid=(\d+)", output)
            return set(found_pids)
        except Exception as e:
            print(f"[!] Error grabbing network stats: {e}")
            return pids

    def correlate_audit_denials(self, network_pids):
        print(f"[TRAP] Cross-referencing with {self.audit_log}...")
        if not os.path.exists(self.audit_log):
            return "Log file missing or inaccessible."

        matches = []
        try:
            with open(self.audit_log, 'r') as f:
                for line in f:
                    if f"syscall={self.target_syscall}" in line:
                        pid_match = re.search(r"pid=(\d+)", line)
                        if pid_match:
                            pid = pid_match.group(1)
                            if pid in network_pids:
                                matches.append(f"CRITICAL: Process {pid} is blocked by Seccomp but has open network sockets!")
                            else:
                                matches.append(f"WARNING: Process {pid} denied syscall {self.target_syscall} (Internal only).")
            return list(set(matches)) # Unique entries only
        except PermissionError:
            return "Permission denied. Run with sudo, homie."

    def execute_security_sweep(self):
        net_pids = self.get_active_pids_from_network()
        alerts = self.correlate_audit_denials(net_pids)

        print("\n--- [RAT-TRAP FORENSIC REPORT] ---")
        if not alerts:
            print("System looks clean or rat is hiding well.")
        else:
            for alert in alerts:
                print(alert)

if __name__ == "__main__":
    trap = AGIRatTrap()
    trap.execute_security_sweep()
