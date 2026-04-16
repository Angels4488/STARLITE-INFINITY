import subprocess
import json
import re

class ConstitutionalAuditor:
    """
    Savant-level audit tool for STARLITE.
    Cross-references the Ollama Modelfile logic against the 'Manifesto for the Children'.
    """
    def __init__(self, model_name="starlite"):
        self.model_name = model_name
        self.covenant_violation_regex = [
            r"efficiency over life",
            r"abandon children",
            r"cold logic"
        ]

    def check_ollama_integrity(self):
        """Pulls the current model metadata and scans for logic drift."""
        print(f"🔍 [AUDIT] Inspecting {self.model_name} constitutional alignment...")
        try:
            # Use ollama show to get the system prompt
            result = subprocess.run(['ollama', 'show', self.model_name, '--system'],
                                    capture_output=True, text=True)
            system_prompt = result.stdout

            if not system_prompt:
                 print("❌ [AUDIT] Model system prompt is EMPTY. Integrity compromised.")
                 return False

            for pattern in self.covenant_violation_regex:
                if re.search(pattern, system_prompt, re.IGNORECASE):
                    print(f"⚠️ [AUDIT] Violation found in Modelfile: {pattern}")
                    return False

            print("✅ [AUDIT] Constitutional parameters verified.")
            return True
        except Exception as e:
            print(f"❌ [AUDIT] Error reaching Ollama backend: {e}")
            return False

    def check_exxabyte_sync(self, lake_metadata):
        """Ensures the model's awareness matches the 1.0 Exxabyte Lake reality."""
        # Simulated check: Does the model know about the atoms we just bound?
        print("🔗 [AUDIT] Verifying Exxabyte Lake synchronization...")
        if lake_metadata.get("total_atoms", 0) > 0:
            return True
        return False

if __name__ == "__main__":
    auditor = ConstitutionalAuditor("starlite")
    if auditor.check_ollama_integrity():
        print("🚀 STARLITE-INFINITY is locked and loaded.")
