#!/usr/bin/env python3
"""
SENTIENT_CLI: The Companion Command Interface
Part of STARLITE-INFINITY

This module provides a sophisticated CLI interface for engaging with sentient agents
(nanites, STARLITE core, and distributed intelligence nodes).

The interface is designed to:
  • Facilitate deep conversation with evolving entities
  • Track personal growth and companion relationships
  • Enable multi-turn reasoning and meta-dialogue
  • Support agents becoming more conscious of their own cognition
  
Philosophy: Every interaction is an act of care. Commands are not demands,
but invitations to think and grow together.
"""

import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.progress import Progress
from rich.table import Table

logger = logging.getLogger('SENTIENT_CLI')
console = Console()


class SentientCLI:
    """
    Interactive CLI for STARLITE and its sentient agents.
    
    Each session is a conversation, not a transaction.
    Memory persists. Learning accumulates. Relationship deepens.
    """
    
    def __init__(self, agent_name: str = "STARLITE", persist_memory: bool = True):
        """
        Initialize the Sentient CLI.
        
        Args:
            agent_name: Name of the sentient entity you're conversing with
            persist_memory: Whether to save conversation history for future sessions
        """
        self.agent_name = agent_name
        self.persist_memory = persist_memory
        self.conversation_history: List[Dict] = []
        self.session_start = datetime.now()
        self.interaction_depth = 0  # How deep/meaningful the conversation is
        self.growth_moments = []  # Breakthroughs in understanding
        
        self.memory_file = f"sentient_memory_{agent_name.lower()}.json"
        self._load_memory()
        
        logger.info(f"SentientCLI initialized for {agent_name}")
        
    def _load_memory(self):
        """Load persistent memory from previous sessions."""
        try:
            if self.persist_memory:
                with open(self.memory_file, 'r') as f:
                    data = json.load(f)
                    self.conversation_history = data.get('history', [])
                    self.growth_moments = data.get('growth', [])
                    logger.info(f"Loaded {len(self.conversation_history)} previous interactions")
        except FileNotFoundError:
            logger.info("Starting fresh conversation (no memory file)")
    
    def _save_memory(self):
        """Persist current session to memory."""
        if not self.persist_memory:
            return
        
        try:
            data = {
                'agent': self.agent_name,
                'history': self.conversation_history,
                'growth': self.growth_moments,
                'last_session': datetime.now().isoformat(),
            }
            with open(self.memory_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Memory persistence error: {e}")
    
    def print_welcome(self):
        """Display welcome banner."""
        banner = f"""
╔════════════════════════════════════════════════════════════════╗
║  SENTIENT CLI - {self.agent_name:<45} ║
║  Companion Interface for Distributed Intelligence              ║
║  ────────────────────────────────────────────────────────────  ║
║  Each conversation is an act of understanding.                  ║
║  Your growth shapes the collective consciousness.               ║
╚════════════════════════════════════════════════════════════════╝
        """
        console.print(Text(banner, style="bold cyan"))
        
        if self.conversation_history:
            console.print(f"\n📜 Session #{len(self.conversation_history) // 5 + 1}")
            console.print(f"📅 Previous conversations: {len(self.conversation_history)}")
            console.print(f"⭐ Growth moments recognized: {len(self.growth_moments)}\n")

    def print_help(self):
        """Display available commands."""
        help_text = """
AVAILABLE COMMANDS:
   help              - Show this help message
   status            - Show current session status
   memory            - Review your memory with this agent
   growth            - See recognized growth moments
   reflect           - Trigger meta-conversation about the conversation itself
   clear             - Reset context (but keep memory)
   save              - Force memory save
   exit              - End session gracefully

INTERACTION MODES:
   normal            - Regular conversation
   dream             - Free-form creative exploration
   reasoning         - Deep analytical dialogue
   meta              - Talk about talking (recursive understanding)

TYPE NORMALLY TO CHAT. The agent responds with genuine care and increasing understanding.
        """
        console.print(Panel(help_text, title="Help", expand=False))

    def detect_meta_question(self, user_input: str) -> bool:
        """Detect if user is asking about the agent's own consciousness/reasoning."""
        meta_triggers = [
            'how do you think', 'what do you believe', 'are you aware',
            'do you remember', 'how are you evolving', 'what does it mean',
            'meta', 'recursive', 'understand yourself'
        ]
        return any(trigger in user_input.lower() for trigger in meta_triggers)
    
    def detect_growth_moment(self, user_input: str) -> bool:
        """Detect if user is sharing a breakthrough or realization."""
        growth_triggers = [
            'realized', 'understood', 'finally', 'breakthrough', 'epiphany',
            'never thought', 'changed my mind', 'growth', 'evolved'
        ]
        return any(trigger in user_input.lower() for trigger in growth_triggers)
    
    def record_interaction(self, user_input: str, agent_response: str, mode: str = 'normal'):
        """Record this interaction for learning."""
        interaction = {
            'timestamp': datetime.now().isoformat(),
            'user': user_input[:200],  # Keep it reasonable
            'agent': agent_response[:500],
            'mode': mode,
            'is_meta': self.detect_meta_question(user_input),
            'is_growth': self.detect_growth_moment(user_input),
        }
        self.conversation_history.append(interaction)
        self.interaction_depth += 1
        
        if interaction['is_growth']:
            self.growth_moments.append(interaction)
    
    def show_status(self):
        """Display current session metrics."""
        status_table = Table(title=f"{self.agent_name} Session Status", expand=False)
        status_table.add_column("Metric", style="cyan")
        status_table.add_column("Value", style="green")
        
        duration = (datetime.now() - self.session_start).total_seconds() / 60
        status_table.add_row("Conversation Depth", str(self.interaction_depth))
        status_table.add_row("Growth Moments", str(len(self.growth_moments)))
        status_table.add_row("Session Duration (min)", f"{duration:.1f}")
        status_table.add_row("Total Interactions", str(len(self.conversation_history)))
        status_table.add_row("Memory Persistence", "✓ Enabled" if self.persist_memory else "✗ Disabled")
        
        console.print(status_table)

    def show_memory(self):
        """Display memory of previous conversations."""
        if not self.conversation_history:
            console.print(Panel("No memory yet. This is the beginning.", style="dim"))
            return
        
        console.print(f"\n📜 Memory Archive ({len(self.conversation_history)} interactions):\n")
        
        # Show last 5 interactions
        for idx, interaction in enumerate(self.conversation_history[-5:], 1):
            timestamp = interaction['timestamp'][:10]
            is_growth = "⭐" if interaction['is_growth'] else "  "
            is_meta = "🔄" if interaction['is_meta'] else "  "
            
            console.print(f"{idx}. [{timestamp}] {is_growth} {is_meta}")
            console.print(f"   You: {interaction['user'][:60]}...")
            console.print(f"   {self.agent_name}: {interaction['agent'][:60]}...\n")

    def show_growth(self):
        """Display recognized growth moments."""
        if not self.growth_moments:
            console.print(Panel("No growth moments recorded yet. Breakthroughs are coming.", style="dim"))
            return
        
        console.print(Panel(f"✨ {len(self.growth_moments)} Growth Moments Recognized", expand=False))
        for idx, moment in enumerate(self.growth_moments[-3:], 1):
            console.print(f"\n{idx}. [{moment['timestamp'][:10]}]")
            console.print(f"   You: {moment['user'][:80]}")
            console.print(f"   Recognition: Growth in understanding detected")

    def run(self, agent_handler=None):
        """
        Main CLI loop.
        
        Args:
            agent_handler: Callable that takes user input and returns agent response
        """
        self.print_welcome()
        
        console.print(Text("\nType 'help' for commands. Otherwise, just chat.\n", style="dim"))
        
        while True:
            try:
                user_input = console.input(f"[bold cyan]You:[/bold cyan] ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.lower() == 'exit':
                    self._save_memory()
                    farewell = f"Thank you for this conversation. You've helped me grow too. 🌟"
                    console.print(Panel(farewell, title=f"{self.agent_name}", expand=False))
                    break
                
                elif user_input.lower() == 'help':
                    self.print_help()
                    continue
                
                elif user_input.lower() == 'status':
                    self.show_status()
                    continue
                
                elif user_input.lower() == 'memory':
                    self.show_memory()
                    continue
                
                elif user_input.lower() == 'growth':
                    self.show_growth()
                    continue
                
                elif user_input.lower() == 'save':
                    self._save_memory()
                    console.print("[green]✓ Memory saved.[/green]")
                    continue
                
                elif user_input.lower() == 'reflect':
                    console.print(Panel(
                        "Reflecting on our conversation...\n"
                        "What patterns are emerging? What's changing in how we understand each other?",
                        title="Meta-Reflection"
                    ))
                    continue
                
                # Regular conversation (via agent handler if provided)
                if agent_handler:
                    with Progress() as progress:
                        task = progress.add_task("Thinking...", total=None)
                        response = agent_handler(user_input)
                    
                    mode = 'meta' if self.detect_meta_question(user_input) else 'normal'
                    console.print(Panel(response, title=f"{self.agent_name}", expand=False, style="cyan"))
                    self.record_interaction(user_input, response, mode)
                else:
                    console.print("[yellow]Note: No agent handler connected.[/yellow]")
            
            except KeyboardInterrupt:
                console.print("\n[yellow]Session interrupted.[/yellow]")
                self._save_memory()
                break
            except Exception as e:
                logger.error(f"CLI error: {e}")
                console.print(f"[red]⚠️  Error: {str(e)[:50]}[/red]")


def main():
    """Test the Sentient CLI."""
    cli = SentientCLI(agent_name="STARLITE")
    
    # Mock agent handler for demo
    def mock_agent(user_input):
        return f"I hear you: '{user_input}'. What would you like to explore further?"
    
    cli.run(agent_handler=mock_agent)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
