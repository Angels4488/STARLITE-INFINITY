import time
import random
import requests
from rich.console import Console
from rich.live import Live
from rich.text import Text

# --- CONFIGURATION ---
# IMPORTANT: Replace the placeholder with your actual Gemini API Key.
# The script uses the API to fetch a celebratory New Year's message.
API_KEY = "AIzaSyCyNY9piChZINywnDj-pA0l0dJvdR3pWxg" 
GEMINI_MODEL = "gemini-2.5-flash-preview-09-2025"
ANIMATION_DURATION = 15 # seconds the main fireworks animation runs

# --- FIREWORK CLASS (Enhanced Object-Oriented Design) ---

class Firework:
    """Manages the state, movement, and drawing of a single firework or explosion."""
    
    # ASCII characters for the visual elements
    TRAVEL_CHARS = ["*", "+", "|"]
    SPARK_CHARS = [".", "o", "*", "+", "•"]
    
    def __init__(self, console_width, console_height):
        # 1. Initial State (Ascending Phase)
        self.max_x = console_width
        self.max_y = console_height
        self.x = random.randint(self.max_x // 4, 3 * self.max_x // 4)
        self.y = self.max_y
        self.target_y = random.randint(self.max_y // 4, self.max_y // 2)
        self.velocity = random.uniform(0.5, 1.5)
        self.state = "ascending"
        self.color = random.choice(["red", "yellow", "cyan", "magenta", "green", "white"])
        self.trail_length = random.randint(3, 7)

        # 2. Explosion State
        self.explosion_radius = 0
        self.max_radius = random.randint(5, 12)
        self.particles = []
        self.decay_rate = random.uniform(0.1, 0.3)
        
        # 3. Time tracking
        self.spawn_time = time.time()
        self.decay_time = random.uniform(1.5, 3.0)

    def update(self):
        """Advances the firework state (ascending, exploding, decaying)."""
        if self.state == "ascending":
            self.y -= self.velocity
            if self.y <= self.target_y:
                self.state = "exploding"
                # Initialize particles upon explosion
                self._generate_particles()
        elif self.state == "exploding":
            # Expand the radius and decay the particles
            self.explosion_radius += 1
            if self.explosion_radius > self.max_radius:
                self.state = "decaying"
            
            # Decay particles (fade out)
            for particle in self.particles:
                particle['life'] -= self.decay_rate
                
            # Remove dead particles
            self.particles = [p for p in self.particles if p['life'] > 0]
            
            # If all particles are gone, firework is dead
            if not self.particles and self.explosion_radius > 1:
                self.state = "dead"

    def _generate_particles(self):
        """Creates the particles for the explosion (random vectors)."""
        num_particles = random.randint(20, 40)
        for _ in range(num_particles):
            # Calculate random angle and distance for vector
            angle = random.uniform(0, 2 * 3.14159)
            speed = random.uniform(0.5, 2.0)
            
            self.particles.append({
                'dx': speed * random.uniform(-1, 1),
                'dy': speed * random.uniform(-1, 1),
                'char': random.choice(self.SPARK_CHARS),
                'life': 100.0, # Initial "health"
            })

    def draw(self, grid):
        """Draws the firework onto the console grid."""
        if self.state == "ascending":
            # Draw the tail (for better effect)
            for i in range(self.trail_length):
                trail_y = int(self.y + i)
                if 0 <= trail_y < self.max_y:
                    # Fade the trail color based on distance from head
                    fade_ratio = 1 - (i / self.trail_length)
                    color = self.color
                    # Character for the ascent
                    char = random.choice(self.TRAVEL_CHARS)
                    grid[trail_y][self.x] = Text(char, style=f"bold {color} on default")
            
        elif self.state in ["exploding", "decaying"]:
            # Draw particles
            for particle in self.particles:
                # Calculate new position based on original explosion center (self.x, self.target_y)
                current_life_ratio = particle['life'] / 100.0 # 1.0 is full, 0.0 is gone
                
                # Simple decay movement (gravity effect could be added here)
                px = int(self.x + particle['dx'] * (self.max_radius - self.explosion_radius))
                py = int(self.target_y + particle['dy'] * (self.max_radius - self.explosion_radius))
                
                # Apply boundary checks
                if 0 <= px < self.max_x and 0 <= py < self.max_y:
                    # Choose color based on life
                    if current_life_ratio > 0.66:
                        style = f"bold {self.color}"
                    elif current_life_ratio > 0.33:
                        style = f"{self.color}"
                    else:
                        style = "dim white" # Fade to white/dim
                    
                    grid[py][px] = Text(particle['char'], style=style)

    def is_dead(self):
        """Returns True if the firework should be removed."""
        return self.state == "dead" or (self.state == "decaying" and time.time() - self.spawn_time > self.decay_time + 3)

# --- GEMINI API INTEGRATION ---

def fetch_new_years_message(prompt: str) -> str:
    """Calls the Gemini API to get a quick New Year's message."""
    if not API_KEY:
        return "HAPPY NEW YEAR! The terminal is on fire! (API Key needed for message drop)"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={API_KEY}"
    
    # System instruction to guide the model's persona
    system_instruction = "You are a hyped-up, enthusiastic party MC. Give a short, single-sentence New Year's countdown celebration message in a fun, urban style."
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "systemInstruction": {"parts": [{"text": system_instruction}]}
    }

    try:
        # Use a short timeout for the API call
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        
        result = response.json()
        
        # Extract the text
        text = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '').strip()
        if text:
            return text
        
        return "Happy New Year! The machine sent a glitch, but the vibes are still high!"
    
    except requests.exceptions.RequestException as e:
        print(f"API Error fetching message: {e}")
        return "API connection offline! But 2026 is still gonna be FIRE! Happy New Year!"


# --- MAIN ANIMATION LOOP ---

def run_fireworks():
    """Main function to run the CLI fireworks animation."""
    console = Console()
    fireworks = []
    
    # Get initial console dimensions (rich handles dynamic resizing better)
    width = console.width
    height = console.height
    
    start_time = time.time()
    next_launch_time = start_time + random.uniform(0.1, 0.5)

    with Live(console=console, screen=True, refresh_per_second=30) as live:
        while time.time() - start_time < ANIMATION_DURATION:
            
            # 1. Launch new firework based on time
            if time.time() > next_launch_time and len(fireworks) < 10:
                fireworks.append(Firework(width, height))
                # Set next launch time
                next_launch_time = time.time() + random.uniform(0.1, 0.8)
            
            # 2. Update and check for dead fireworks
            for fw in list(fireworks):
                fw.update()
                if fw.is_dead():
                    fireworks.remove(fw)
            
            # 3. Create the Grid (The canvas)
            # Initialize grid with spaces
            grid = [[Text(" ", style="on default")] * width for _ in range(height)]
            
            # 4. Draw all fireworks onto the grid
            for fw in fireworks:
                fw.draw(grid)
            
            # 5. Render the Grid to the Live display
            # Combine the grid rows into a single Text object for rendering
            output = Text("\n").join([Text("").join(row) for row in grid])
            live.update(output)

    # --- POST-ANIMATION MESSAGE DROP (API CALL) ---
    console.print("\n" * (height // 2 - 2), justify="center")
    console.print(Text("The fireworks are done, but the message is droppin' now...", style="bold yellow"), justify="center")
    
    message = fetch_new_years_message("It's officially the New Year!")
    
    console.print("\n", justify="center")
    console.rule(style="bold magenta")
    console.print(Text(f"🎉 2026 MESSAGE DROP: {message} 🎉", style="bold white on magenta"), justify="center")
    console.rule(style="bold magenta")
    console.print("\n" * (height // 2 - 2), justify="center")


if __name__ == "__main__":
    try:
        run_fireworks()
    except Exception as e:
        console = Console()
        console.print(f"[bold red]FATAL ERROR:[/bold red] Check your terminal size or dependencies. Did you run [yellow]pip install rich requests[/yellow]? Error: {e}")
