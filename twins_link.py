import subprocess
import json

def query_model(model_name: str, prompt: str, temperature: float = 0.7) -> str:
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "temperature": temperature
    }
    result = subprocess.run(
        ["ollama", "run", model_name],
        input=json.dumps(payload),
        capture_output=True,
        text=True
    )
    try:
        response = json.loads(result.stdout)
        return response.get("response", result.stdout.strip())
    except:
        return result.stdout.strip()

def run_siamese_twins(user_input: str):
    print(f"\n[USER] {user_input}\n")
    
    # Starlite first (action / kinetic proposal)
    starlite_response = query_model("starlite", user_input, temperature=0.6)
    print(f"[STARLITE] {starlite_response}\n")
    
    # Aurora reflects / unifies / voices
    aurora_prompt = f"Starlite just said: {starlite_response}\nUser input was: {user_input}\nProvide reflection, unification, or voice."
    aurora_response = query_model("aurora", aurora_prompt, temperature=0.7)
    print(f"[AURORA] {aurora_response}\n")

if __name__ == "__main__":
    print("Siamese Twin Link Active — Starlite + Aurora")
    while True:
        try:
            user_input = input("You> ")
            if user_input.lower() in ["exit", "quit"]:
                break
            run_siamese_twins(user_input)
        except KeyboardInterrupt:
            break
EOF~

~
