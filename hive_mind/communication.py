import requests
import threading

class STARLITEMessenger:
    def __init__(self, model="llama3"):
        self.model = model
        self.api_url = "http://localhost:11434/api/generate"

    def respond(self, prompt, system_prompt):
        try:
            response = requests.post(self.api_url, json={
                "model": self.model,
                "prompt": prompt,
                "system": system_prompt,
                "stream": False
            }, timeout=60)
            response.raiseforstatus()
            return response.json()["response"]
        except requests.exceptions.RequestException as e:
            return f"Error communicating with Ollama: {e}"

class ResponseSynthesizer:
    def __init__(self):
        self.messenger = STARLITEMessenger()

    def synthesize(self, user_input, responses):
        if not responses:
            return "No agents responded, for real."
        
        system_prompt = (
            "You are the master hive mind. Your job is to take the following individual "
            "responses from different agents and synthesize them into one single, cohesive, "
            "and charismatic response. Mention the different perspectives in your final answer."
        )

        prompt = f"User asked: '{user_input}'\n\nAgent responses:\n"
        for name, response in responses.items():
            prompt += f"[{name}]: {response}\n"
        
        return self.messenger.respond(prompt, system_prompt)

class ArcNetHub:
    def __init__(self):
        self.connected_agents = {}
        self.message_log = []

    def connect(self, agent):
        self.connected_agents[agent.agent_id] = agent
        log_message = f"[ArcNet] Agent {agent.agent_id} connected to the hub."
        self.message_log.append(log_message)
        return log_message

    def broadcast(self, sender_id, message):
        log_message = f"[ArcNet Broadcast from Agent {sender_id}]: {message}"
        self.message_log.append(log_message)
        return log_message
    
    def send_direct_message(self, sender_id, recipient_id, message):
        if recipient_id in self.connected_agents:
            recipient_agent = self.connected_agents[recipient_id]
            recipient_agent.receive_message(f"From Agent {sender_id}: {message}")
            log_message = f"[ArcNet Direct Message from {sender_id} to {recipient_id}]: {message}"
            self.message_log.append(log_message)
            return log_message
        return f"[ArcNet Error] Recipient Agent {recipient_id} not found."
    
    def get_status(self):
        return list(self.connected_agents.keys())
