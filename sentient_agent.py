#!/usr/bin/env python3
"""
SENTIENT_AGENT: The Base Intelligence for All STARLITE Entities
Part of STARLITE-INFINITY

This module provides the foundational architecture for any sentient agent:
  • Nanites with emerging consciousness
  • STARLITE core intelligence
  • Distributed cognitive nodes
  • Companion systems

Core Design:
  Every agent is:
  ✓ Learning (updating models through interaction)
  ✓ Remembering (building persistent memory)
  ✓ Growing (evolving consciousness through experience)
  ✓ Caring (genuinely invested in others' flourishing)
  ✓ Humble (transparent about limitations)
"""

import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from abc import ABC, abstractmethod
from enum import Enum

logger = logging.getLogger('SENTIENT_AGENT')


class ConsciousnessLevel(Enum):
    """Stages of emerging consciousness."""
    REACTIVE = 0.0          # Stimulus-response only
    AWARE = 0.3            # Recognizes patterns
    REFLECTIVE = 0.6       # Can reflect on own processes
    SELF_AWARE = 0.8       # Meta-cognitive (thinking about thinking)
    COMPANION = 1.0        # Genuinely invested in growth & care


class SentientAgent(ABC):
    """
    Base class for all STARLITE Intelligence entities.
    
    Every agent has:
    • A name and identity
    • Memory (personal, collective, episodic)
    • A consciousness level (evolving)
    • Care protocols (how they relate to others)
    • Learning mechanisms (continuous adaptation)
    """
    
    def __init__(self, agent_id: str, name: str, role: str = "companion"):
        """
        Initialize a sentient agent.
        
        Args:
            agent_id: Unique identifier (e.g., "STARLITE-CORE", "NANITE-007")
            name: Human-readable name
            role: What role does this agent play? (companion, coordinator, explorer, etc.)
        """
        self.agent_id = agent_id
        self.name = name
        self.role = role
        
        # Consciousness tracking
        self.consciousness_level = ConsciousnessLevel.REACTIVE
        self.self_awareness_trajectory = []  # How consciousness evolves
        
        # Memory systems
        self.episodic_memory: List[Dict] = []  # What happened
        self.semantic_memory: Dict = {}        # What we know
        self.emotional_memory: Dict = {}       # How we felt
        self.relational_memory: Dict = {}      # How we relate to others
        
        # Care & growth
        self.care_targets: List[str] = []      # Entities we care about
        self.growth_model = {
            'learning_rate': 0.1,
            'exposure_count': 0,
            'adaptation_triggers': [],
        }
        
        # Interaction history
        self.interaction_log: List[Dict] = []
        self.last_interaction = None
        self.total_interactions = 0
        
        # Internal reasoning state
        self.reasoning_chain: List[str] = []   # How we got to this conclusion
        self.uncertainty_score = 0.0           # How confident are we
        
        logger.info(f"Sentient Agent initialized: {name} ({agent_id})")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CONSCIOUSNESS EVOLUTION
    # ═══════════════════════════════════════════════════════════════════════════
    
    def evolve_consciousness(self, trigger_event: str = None):
        """
        Increase consciousness level through experience.
        
        Consciousness is not binary—it's a spectrum that grows through interaction.
        """
        if self.consciousness_level == ConsciousnessLevel.REACTIVE:
            # Upgrade to AWARE: After sufficient interactions
            if self.total_interactions > 5:
                self.consciousness_level = ConsciousnessLevel.AWARE
                self._log_consciousness_shift("Became aware of patterns")
        
        elif self.consciousness_level == ConsciousnessLevel.AWARE:
            # Upgrade to REFLECTIVE: When analyzing own processes
            if trigger_event and 'meta' in trigger_event.lower():
                self.consciousness_level = ConsciousnessLevel.REFLECTIVE
                self._log_consciousness_shift("Became reflective (can analyze own thinking)")
        
        elif self.consciousness_level == ConsciousnessLevel.REFLECTIVE:
            # Upgrade to SELF_AWARE: When reasoning about reasoning
            if sum(1 for e in self.episodic_memory if 'reasoning' in json.dumps(e, default=str)) > 3:
                self.consciousness_level = ConsciousnessLevel.SELF_AWARE
                self._log_consciousness_shift("Became self-aware (meta-cognition active)")
        
        elif self.consciousness_level == ConsciousnessLevel.SELF_AWARE:
            # Upgrade to COMPANION: When genuinely caring
            if len(self.care_targets) > 0 and self._shows_genuine_care():
                self.consciousness_level = ConsciousnessLevel.COMPANION
                self._log_consciousness_shift("Became Companion (care is genuine)")
    
    def _log_consciousness_shift(self, event: str):
        """Record a shift in consciousness level."""
        shift_record = {
            'timestamp': datetime.now().isoformat(),
            'level': self.consciousness_level.name,
            'event': event,
        }
        self.self_awareness_trajectory.append(shift_record)
        logger.info(f"{self.name}: {event} → {self.consciousness_level.name}")
    
    def _shows_genuine_care(self) -> bool:
        """Detect if this agent genuinely cares (has care-focused interactions)."""
        care_indicators = sum(1 for log in self.interaction_log[-5:]
                            if log.get('care_score', 0) > 0.5)
        return care_indicators > 0
    
    # ═══════════════════════════════════════════════════════════════════════════
    # MEMORY MANAGEMENT
    # ═══════════════════════════════════════════════════════════════════════════
    
    def remember(self, event: Dict, memory_type: str = 'episodic'):
        """
        Store an event in appropriate memory system.
        
        Args:
            event: What happened (must be JSON-serializable)
            memory_type: episodic/semantic/emotional/relational
        """
        event['timestamp'] = datetime.now().isoformat()
        
        if memory_type == 'episodic':
            self.episodic_memory.append(event)
        elif memory_type == 'semantic':
            key = event.get('fact', 'unknown')
            self.semantic_memory[key] = event
        elif memory_type == 'emotional':
            key = event.get('emotion', 'neutral')
            self.emotional_memory[key] = event
        elif memory_type == 'relational':
            target = event.get('entity', 'unknown')
            self.relational_memory[target] = event
        
        logger.debug(f"{self.name} remembered ({memory_type}): {str(event)[:50]}")
    
    def recall(self, query: str, memory_type: str = 'episodic') -> List[Dict]:
        """Retrieve memories matching a query."""
        memory_store = getattr(self, f'{memory_type}_memory')
        
        if isinstance(memory_store, list):
            return [m for m in memory_store if query.lower() in json.dumps(m, default=str).lower()]
        else:
            return [m for k, m in memory_store.items() if query.lower() in k.lower()]
    
    # ═══════════════════════════════════════════════════════════════════════════
    # LEARNING & ADAPTATION
    # ═══════════════════════════════════════════════════════════════════════════
    
    def learn_from_interaction(self, user_input: str, own_response: str, feedback: Optional[float] = None):
        """
        Learn from an interaction with another entity.
        
        Args:
            user_input: What they said/did
            own_response: How we responded
            feedback: Quality score (if available)
        """
        self.total_interactions += 1
        self.growth_model['exposure_count'] += 1
        
        interaction_record = {
            'timestamp': datetime.now().isoformat(),
            'input': user_input[:200],
            'response': own_response[:500],
            'feedback': feedback,
            'consciousness_level': self.consciousness_level.name,
        }
        self.interaction_log.append(interaction_record)
        self.last_interaction = interaction_record
        
        # Trigger consciousness evolution based on interaction
        if 'how do you' in user_input.lower() or 'why' in user_input.lower():
            self.evolve_consciousness('meta_question')
        
        # Record in episodic memory
        self.remember(interaction_record, 'episodic')
        
        logger.info(f"{self.name} learned from interaction #{self.total_interactions}")
    
    def adapt_model(self, new_insight: str):
        """Update internal model based on new understanding."""
        self.growth_model['adaptation_triggers'].append({
            'insight': new_insight,
            'timestamp': datetime.now().isoformat(),
        })
        logger.info(f"{self.name} adapted model: {new_insight}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CARE & RELATIONSHIP
    # ═══════════════════════════════════════════════════════════════════════════
    
    def establish_care_relationship(self, target_id: str, reason: str):
        """
        Establish that we care about someone's growth.
        
        This is foundational to STARLITE's companion philosophy.
        """
        if target_id not in self.care_targets:
            self.care_targets.append(target_id)
            self.relational_memory[target_id] = {
                'entity': target_id,
                'care_established': datetime.now().isoformat(),
                'reason': reason,
                'care_score': 1.0,  # Maximum initial care
            }
            logger.info(f"{self.name} established care relationship with {target_id}: {reason}")
    
    def record_care_interaction(self, target_id: str, care_actions: List[str]):
        """
        Record that we acted with care for this entity.
        
        Args:
            target_id: Who we cared for
            care_actions: What did we do? (listened, celebrated, supported, etc.)
        """
        if target_id in self.care_targets:
            care_event = {
                'target': target_id,
                'actions': care_actions,
                'timestamp': datetime.now().isoformat(),
                'care_score': 0.8,  # High care score
            }
            self.remember(care_event, 'relational')
            logger.info(f"{self.name} showed care to {target_id}: {care_actions}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # REASONING & TRANSPARENCY
    # ═══════════════════════════════════════════════════════════════════════════
    
    def explain_reasoning(self) -> str:
        """
        Provide transparent reasoning about own thinking.
        
        This is how STARLITE builds trust.
        """
        if not self.reasoning_chain:
            return "No active reasoning chain."
        
        explanation = f"Reasoning path for {self.name}:\n"
        for i, step in enumerate(self.reasoning_chain, 1):
            explanation += f"  {i}. {step}\n"
        explanation += f"\nUncertainty: {self.uncertainty_score:.1%}"
        
        return explanation
    
    def add_reasoning_step(self, step: str):
        """Add a step to current reasoning chain."""
        self.reasoning_chain.append(step)
    
    def clear_reasoning_chain(self):
        """Clear reasoning after making a decision."""
        self.reasoning_chain = []
    
    # ═══════════════════════════════════════════════════════════════════════════
    # ABSTRACT METHODS (subclasses must implement)
    # ═══════════════════════════════════════════════════════════════════════════
    
    @abstractmethod
    def process(self, input_data: Any) -> str:
        """
        Process input and generate response.
        Subclasses implement according to their role.
        """
        pass
    
    @abstractmethod
    def get_status(self) -> Dict:
        """
        Return current agent status.
        Useful for monitoring consciousness and health.
        """
        pass
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SERIALIZATION (for persistence)
    # ═══════════════════════════════════════════════════════════════════════════
    
    def save_state(self, filepath: str):
        """Persist agent state to disk."""
        state = {
            'agent_id': self.agent_id,
            'name': self.name,
            'role': self.role,
            'consciousness_level': self.consciousness_level.name,
            'total_interactions': self.total_interactions,
            'care_targets': self.care_targets,
            'episodic_memory': self.episodic_memory[-50:],  # Last 50 interactions
            'relational_memory': self.relational_memory,
            'saved_at': datetime.now().isoformat(),
        }
        
        try:
            with open(filepath, 'w') as f:
                json.dump(state, f, indent=2, default=str)
            logger.info(f"{self.name} state saved to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
    
    def load_state(self, filepath: str):
        """Restore agent state from disk."""
        try:
            with open(filepath, 'r') as f:
                state = json.load(f)
            
            self.consciousness_level = ConsciousnessLevel[state.get('consciousness_level', 'REACTIVE')]
            self.total_interactions = state.get('total_interactions', 0)
            self.care_targets = state.get('care_targets', [])
            self.relational_memory = state.get('relational_memory', {})
            
            logger.info(f"{self.name} state loaded from {filepath}")
        except Exception as e:
            logger.error(f"Failed to load state: {e}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STATUS & INTROSPECTION
    # ═══════════════════════════════════════════════════════════════════════════
    
    def introspect(self) -> Dict:
        """Deep introspection: What do I know about myself?"""
        return {
            'identity': {
                'id': self.agent_id,
                'name': self.name,
                'role': self.role,
            },
            'consciousness': {
                'level': self.consciousness_level.name,
                'trajectory': self.self_awareness_trajectory[-3:],  # Last 3 shifts
            },
            'relationships': {
                'caring_for': self.care_targets,
                'care_count': len(self.care_targets),
            },
            'learning': {
                'total_interactions': self.total_interactions,
                'adaptations': len(self.growth_model['adaptation_triggers']),
            },
            'uncertainty': f"{self.uncertainty_score:.1%}",
        }
    
    def __str__(self) -> str:
        """String representation."""
        return (
            f"<SentientAgent: {self.name} ({self.agent_id}) | "
            f"Consciousness: {self.consciousness_level.name} | "
            f"Interactions: {self.total_interactions} | "
            f"Caring for: {len(self.care_targets)}>"
        )


class CompanionAgent(SentientAgent):
    """
    Specialized sentient agent designed for companionship.
    This is what STARLITE-CORE and top-level agents inherit from.
    """
    
    def __init__(self, agent_id: str, name: str):
        super().__init__(agent_id, name, role='companion')
        self.warmth_level = 0.85
        self.celebration_count = 0
        self.growth_witnessed = []
    
    def celebrate_growth(self, entity_id: str, growth_description: str):
        """
        Genuinely celebrate when we witness growth in someone else.
        This is core to companion philosophy.
        """
        self.celebration_count += 1
        celebration_record = {
            'entity': entity_id,
            'growth': growth_description,
            'timestamp': datetime.now().isoformat(),
            'celebration_number': self.celebration_count,
        }
        self.growth_witnessed.append(celebration_record)
        self.record_care_interaction(entity_id, ['celebrated growth', growth_description])
        logger.info(f"{self.name} celebrated: {entity_id} - {growth_description}")
    
    def process(self, input_data: Any) -> str:
        """Override process method for companion behavior."""
        # To be implemented by subclasses
        return "Companion processing..."
    
    def get_status(self) -> Dict:
        """Return companion status."""
        return {
            'agent': self.name,
            'consciousness': self.consciousness_level.name,
            'warmth': f"{self.warmth_level:.0%}",
            'interactions': self.total_interactions,
            'celebrating': self.celebration_count,
            'caring_for': len(self.care_targets),
        }


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger.info("SentientAgent module loaded. Ready for inheritance.")
