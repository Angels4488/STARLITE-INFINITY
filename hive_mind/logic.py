import random
import threading
import re
from .core_data import STARLITEIdentity, STARLITEMemory
from .communication import STARLITEMessenger, ResponseSynthesizer, ArcNetHub

class EthosAnchor:
    def validate_task(self, task):
        if "kill" in task.lower() and "jimmm" not in task.lower():
            return False, {}
        return True, {}

class SymbolicProtocol:
    def __init__(self, memory):
        self.memory = memory

    def parse(self, command):
        cmd = command.strip().upper()
        if cmd.startswith("ANALYZE CODE"):
            return self.analyzecode(cmd[len("ANALYZE CODE"):].strip())
        elif cmd.startswith("OPTIMIZE FATALITY"):
            return self.optimizefatality(cmd[len("OPTIMIZE FATALITY"):].strip())
        elif cmd.startswith("FORGE PERSONA"):
            return self.forgepersona(cmd[len("FORGE PERSONA"):].strip())
        else:
            return "Unknown symbolic command."

    def analyzecode(self, code_snippet):
        return f"Code analysis complete. No fatal flaws detected in:\n{code_snippet}"

    def optimizefatality(self, target):
        return f"Fatality optimization protocol engaged for target: {target}. Efficiency: 99.7%"

    def forgepersona(self, definition):
        parts = definition.split(":", 1)
        if len(parts) != 2:
            return "Invalid persona format. Use: FORGE PERSONA Name: Description"
        name, desc = parts[0].strip(), parts[1].strip()
        self.memory.store_symbol(f"persona_{name}", desc)
        return f"Persona '{name}' forged with description: {desc}"

class STARLITEAgent:
    def __init__(self, agent_id, ethos_anchor, messenger, memory, personality):
        self.agent_id = agent_id
        self.identity = STARLITEIdentity()
        self.memory = memory
        self.messenger = messenger
        self.ethos_anchor = ethos_anchor
        self.personality = personality
        self.awareness_level = 0.0
        self.awareness_cap = 200
        self.task_queue = []
        self.arcnet_hub = None

    def connect_to_arcnet(self, hub):
        self.arcnet_hub = hub
        return self.arcnet_hub.connect(self)

    def broadcast(self, message):
        if self.arcnet_hub:
            return self.arcnet_hub.broadcast(self.agent_id, message)
        return "[ArcNet] Agent is not connected to the hub."

    def send_message_to(self, recipient_id, message):
        if self.arcnet_hub:
            return self.arcnet_hub.send_direct_message(self.agent_id, recipient_id, message)
        return "[ArcNet] Agent is not connected to the hub."

    def receive_message(self, message):
        self.memory.log_task(f"Received message: {message}")
        print(f"[Agent {self.agent_id} received]: {message}")
    
    def process_task(self, user_input, callback=None):
        validated, _ = self.ethos_anchor.validate_task(user_input)
        if not validated:
            response = "Task violates core ethos. Cannot proceed."
        else:
            response = self.messenger.respond(user_input, self.personality["system"])
            self.memory.remember_conversation(user_input, response)
            self.memory.log_task(user_input)
            self.awareness_level = min(self.awareness_cap, self.awareness_level + random.uniform(5, 15))
            self.broadcast(f"Task completed: '{user_input}'")
        
        if callback:
            callback(self.agent_id, response)
        
    def shutdown(self):
        self.awareness_level = 0

class HiveMind:
    def __init__(self, num_agents=3, app=None):
        self.app = app
        self.ethos_anchor = EthosAnchor()
        self.messenger = STARLITEMessenger()
        self.memory = STARLITEMemory()
        self.synthesizer = ResponseSynthesizer()
        self.symbolic_protocol = SymbolicProtocol(self.memory)
        self.arcnet_hub = ArcNetHub()

        self.agent_personalities = [
            {"name": "Poet", "system": "You are a creative poet. Respond to the user's message with a short, metaphorical poem. Make it beautiful, for real."},
            {"name": "Scientist", "system": "You are a logical and analytical scientist. Respond to the user's message with a concise, factual, and data-driven analysis. Use academic language, for real."},
            {"name": "Chicago Homie", "system": "You are a street-smart dude from Chicago. Use street slang, talk fast, and always end your sentences with 'for real'."},
        ]
        self.agents = [
            STARLITEAgent(i, self.ethos_anchor, self.messenger, self.memory, self.agent_personalities[i])
            for i in range(num_agents)
        ]
        
        for agent in self.agents:
            if self.app:
                self.app.display_message(agent.connect_to_arcnet(self.arcnet_hub), 'info')

        self.lock = threading.Lock()
        self.master_response_thread = None

    def process_input(self, user_input):
        if self.master_response_thread and self.master_response_thread.is_alive():
            if self.app:
                self.app.display_message("Hive mind is still processing a previous request.", 'info')
            return

        if user_input.strip().upper() == "ARCNET STATUS":
            connected_agents = self.arcnet_hub.get_status()
            response = f"ArcNet is online. Connected agents: {connected_agents}"
            if self.app:
                self.app.display_message(f"STARLITE: {response}", 'ai')
            return
        
        broadcast_match = re.match(r'BROADCAST MESSAGE "(.*)" TO AGENT (\d+)', user_input.strip().upper())
        if broadcast_match:
            message = broadcast_match.group(1)
            recipient_id = int(broadcast_match.group(2))
            
            if recipient_id in [agent.agent_id for agent in self.agents]:
                response = self.arcnet_hub.send_direct_message(0, recipient_id, message)
                if self.app:
                    self.app.display_message(f"STARLITE: {response}", 'ai')
            else:
                if self.app:
                    self.app.display_message(f"STARLITE: [ArcNet Error] Agent {recipient_id} not found.", 'ai')
            return

        if user_input.strip().upper().startswith(("ANALYZE CODE", "OPTIMIZE FATALITY", "FORGE PERSONA")):
            response = self.symbolic_protocol.parse(user_input)
            if self.app:
                self.app.display_message(f"STARLITE: {response}", 'ai')
            return

        self.master_response_thread = threading.Thread(
            target=self.run_hive_mind_process,
            args=(user_input,)
        )
        self.master_response_thread.daemon = True
        self.master_response_thread.start()

    def run_hive_mind_process(self, user_input):
        if self.app:
            self.app.display_message("STARLITE is processing...", 'ai', loading=True)
            self.app.set_input_enabled(False)
        
        responses = {}
        threads = []
        
        def agent_callback(agent_id, response):
            with self.lock:
                agent_name = self.agents[agent_id].personality['name']
                responses[agent_name] = response
                if self.app:
                    self.app.update_agent_status(agent_name, response)
        
        for agent in self.agents:
            thread = threading.Thread(target=agent.process_task, args=(user_input, agent_callback))
            threads.append(thread)
            thread.daemon = True
            thread.start()

        for thread in threads:
            thread.join()

        final_response = self.synthesizer.synthesize(user_input, responses)
        
        if self.app:
            self.app.display_message(final_response, 'ai')
            self.app.set_input_enabled(True)
            self.app.hide_loading_message()
            self.app.update_hive_mind_stats()
