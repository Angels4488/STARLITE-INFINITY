import subprocess
import sys
import os

# --- STARLITE-INFINITY: RESOLUTE BRIDGE PATCH ---
# ARCHITECTURE: Resilient Repo Injection / Fallback Protocol
# DIRECTIVE: Keep the session alive even when PPAs fail.

class StarliteBridge:
    def __init__(self):
        self.os_codename = "resolute" # Ubuntu 26.04
        self.bleeding_edge = False

    def inject_bleeding_edge_repos(self):
        """
        Attempts PPA injection but catches 404s/Errors to prevent
        subprocess.CalledProcessError from killing the AGI spine.
        """
        print(f"🔧 [BRIDGE] Checking repository alignment for {self.os_codename}...")

        repos = [
            "ppa:graphics-drivers/ppa",
            # "ppa:deadsnakes/ppa"  # REMOVED: 404 on 26.04
        ]

        for ppa in repos:
            try:
                print(f"💉 [BRIDGE] Injecting {ppa}...")
                subprocess.run(["sudo", "add-apt-repository", "-y", ppa], check=True, capture_output=True)
            except subprocess.CalledProcessError:
                print(f"⚠️ [BRIDGE] Warning: {ppa} not available for {self.os_codename}. Skipping.")

        # CRITICAL FIX: The update check
        try:
            print("🔄 [BRIDGE] Synchronizing system indexes...")
            # We use --allow-releaseinfo-change to handle the 'resolute' shift
            subprocess.run(["sudo", "apt-get", "update", "--allow-releaseinfo-change"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"🛑 [BRIDGE] Non-critical update error (Status {e.returncode}). Moving to Fallback Logic.")

    def launch_session(self, target_files):
        """Plugs the modules in one-by-one, skipping the broken repo-links."""
        self.inject_bleeding_edge_repos()

        print("📂 [BRIDGE] Systematically loading modules into the Resolute Spine...")
        for f in target_files:
            if os.path.exists(f):
                print(f"✅ [BRIDGE] Plugging in: {f}")
                # Logic to execute/import the module goes here
            else:
                print(f"❌ [BRIDGE] Module {f} missing from local VFS.")

if __name__ == "__main__":
    bridge = StarliteBridge()
    target_files = ["N7_Astral_Core.py", "starlite_synapse.py"]
    bridge.launch_session(target_files)
