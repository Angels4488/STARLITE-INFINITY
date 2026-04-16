import pyttsx3
import queue
import threading

class VoiceModule:
    """
    The Herald of the AGI. It takes textual wisdom from the core and
    gives it voice, speaking the AGI's thoughts into the world.
    It operates in a separate thread to not disturb the AGI's concentration.
    """
    def __init__(self):
        """Initializes the voice engine and prepares the speaking queue."""
        self.engine = pyttsx3.init()
        self.task_queue = queue.Queue()
        self.is_enabled = False

        # Start the herald's watch
        self.worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.worker_thread.start()

    def _process_queue(self):
        """The herald's eternal duty: to wait for messages and speak them aloud."""
        while True:
            text_to_speak = self.task_queue.get()
            if self.is_enabled and text_to_speak:
                self.engine.say(text_to_speak)
                self.engine.runAndWait()
            self.task_queue.task_done()

    def speak(self, text: str):
        """Places a message in the queue for the herald to proclaim."""
        self.task_queue.put(text)

    def toggle_voice(self, enabled: bool):
        """Commands the herald to speak or to hold its silence."""
        self.is_enabled = enabled
