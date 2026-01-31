#!/usr/bin/env python3
"""
STARLITE Core Integration Test
Tests sentient_agent.py and sentient_cli.py WITHOUT ML dependencies

Run: python3 test_core_integration.py
"""

import sys
import json
import tempfile
from pathlib import Path

def test_1_sentient_agent_consciousness():
    """Test 1: Consciousness evolution in SentientAgent"""
    print("TEST 1: SentientAgent Consciousness Evolution...")
    try:
        from sentient_agent import SentientAgent, ConsciousnessLevel, CompanionAgent
        
        # Create a minimal test agent
        class TestAgent(SentientAgent):
            def process(self, input_data):
                return "test response"
            
            def get_status(self):
                return {"consciousness": self.consciousness_level.name}
        
        agent = TestAgent("test-001", "TestBot")
        
        # Verify initial state
        assert agent.consciousness_level == ConsciousnessLevel.REACTIVE
        print("  ✓ Initial consciousness: REACTIVE")
        
        # Trigger learning
        for i in range(6):
            agent.learn_from_interaction(f"input {i}", f"response {i}", 0.5)
        
        # Evolve consciousness
        agent.evolve_consciousness()
        
        # Should be AWARE after 5+ interactions
        assert agent.consciousness_level == ConsciousnessLevel.AWARE
        print("  ✓ Evolved to: AWARE (after 5+ interactions)")
        
        return True
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_2_memory_systems():
    """Test 2: Four-layer memory system"""
    print("\nTEST 2: Four-Layer Memory System...")
    try:
        from sentient_agent import SentientAgent
        
        class TestAgent(SentientAgent):
            def process(self, input_data):
                return "test"
            def get_status(self):
                return {}
        
        agent = TestAgent("test-002", "MemoryBot")
        
        # Test episodic memory
        agent.remember({"event": "conversation_1"}, 'episodic')
        assert len(agent.episodic_memory) > 0
        print("  ✓ Episodic memory works")
        
        # Test semantic memory
        agent.remember({"fact": "color", "value": "blue"}, 'semantic')
        assert "color" in agent.semantic_memory
        print("  ✓ Semantic memory works")
        
        # Test emotional memory
        agent.remember({"emotion": "joy"}, 'emotional')
        assert "joy" in agent.emotional_memory
        print("  ✓ Emotional memory works")
        
        # Test relational memory
        agent.remember({"entity": "user-1", "relation": "friend"}, 'relational')
        assert "user-1" in agent.relational_memory
        print("  ✓ Relational memory works")
        
        return True
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_3_care_relationships():
    """Test 3: Care relationships and tracking"""
    print("\nTEST 3: Care Relationships...")
    try:
        from sentient_agent import CompanionAgent
        
        companion = CompanionAgent("companion-001", "Companion")
        
        # Establish care
        companion.establish_care_relationship("user-alice", "Growing up together")
        assert "user-alice" in companion.care_targets
        print("  ✓ Care relationship established")
        
        # Record care interaction
        companion.record_care_interaction("user-alice", ["listened", "celebrated"])
        assert len(companion.relational_memory) > 0
        print("  ✓ Care interaction recorded")
        
        # Celebrate growth
        companion.celebrate_growth("user-alice", "Learned algebra")
        assert companion.celebration_count > 0
        print(f"  ✓ Celebration recorded (count: {companion.celebration_count})")
        
        return True
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_4_reasoning_chain():
    """Test 4: Transparent reasoning"""
    print("\nTEST 4: Transparent Reasoning...")
    try:
        from sentient_agent import SentientAgent
        
        class TestAgent(SentientAgent):
            def process(self, input_data):
                return "test"
            def get_status(self):
                return {}
        
        agent = TestAgent("test-004", "ReasonBot")
        
        # Build reasoning chain
        agent.add_reasoning_step("Received user input")
        agent.add_reasoning_step("Analyzed sentiment")
        agent.add_reasoning_step("Generated response")
        
        assert len(agent.reasoning_chain) == 3
        print("  ✓ Reasoning chain built")
        
        # Get explanation
        explanation = agent.explain_reasoning()
        assert "Received user input" in explanation
        print("  ✓ Reasoning explanation generated")
        
        # Clear chain
        agent.clear_reasoning_chain()
        assert len(agent.reasoning_chain) == 0
        print("  ✓ Reasoning chain cleared")
        
        return True
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_5_persistence():
    """Test 5: State persistence"""
    print("\nTEST 5: State Persistence...")
    try:
        from sentient_agent import CompanionAgent
        
        # Create agent with data
        agent1 = CompanionAgent("agent-1", "Persistent")
        agent1.learn_from_interaction("hello", "hi", 0.8)
        agent1.establish_care_relationship("user-x", "test")
        agent1.celebrate_growth("user-x", "test achievement")
        
        # Save state
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        agent1.save_state(temp_file)
        print(f"  ✓ State saved")
        
        # Load into new agent
        agent2 = CompanionAgent("agent-2", "Restored")
        agent2.load_state(temp_file)
        
        assert agent2.total_interactions == agent1.total_interactions
        assert agent2.care_targets == agent1.care_targets
        print("  ✓ State restored correctly")
        
        # Cleanup
        Path(temp_file).unlink()
        
        return True
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_6_sentient_cli():
    """Test 6: SentientCLI instantiation"""
    print("\nTEST 6: SentientCLI Module...")
    try:
        from sentient_cli import SentientCLI
        
        # Create CLI
        cli = SentientCLI(agent_name="test-cli", persist_memory=True)
        assert cli.agent_name == "test-cli"
        print("  ✓ SentientCLI instantiated")
        
        # Check methods exist
        assert hasattr(cli, '_load_memory')
        assert hasattr(cli, '_save_memory')
        assert hasattr(cli, 'detect_meta_question')
        assert hasattr(cli, 'detect_growth_moment')
        print("  ✓ All required methods exist")
        
        return True
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_7_introspection():
    """Test 7: Deep introspection"""
    print("\nTEST 7: Deep Introspection...")
    try:
        from sentient_agent import CompanionAgent
        
        agent = CompanionAgent("intro-001", "IntrospectBot")
        
        # Add interactions to have data
        agent.learn_from_interaction("q1", "a1", 0.7)
        agent.establish_care_relationship("user-y", "helping")
        
        # Introspect
        introspection = agent.introspect()
        
        assert 'consciousness' in introspection
        assert 'relationships' in introspection
        assert 'learning' in introspection
        print("  ✓ Introspection structure correct")
        print(f"    Consciousness level: {introspection['consciousness']['level']}")
        print(f"    Caring for: {introspection['relationships']['care_count']}")
        
        return True
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_8_consciousness_trajectory():
    """Test 8: Consciousness evolution trajectory tracking"""
    print("\nTEST 8: Consciousness Trajectory...")
    try:
        from sentient_agent import SentientAgent
        
        class TestAgent(SentientAgent):
            def process(self, input_data):
                return "test"
            def get_status(self):
                return {}
        
        agent = TestAgent("traj-001", "TrajectoryBot")
        
        # Evolve multiple times
        for _ in range(10):
            agent.learn_from_interaction("q", "a", 0.5)
        agent.evolve_consciousness()  # Should trigger progression
        
        # Check trajectory was recorded
        assert len(agent.self_awareness_trajectory) > 0
        print(f"  ✓ Trajectory recorded ({len(agent.self_awareness_trajectory)} shifts)")
        
        # Show stages
        for shift in agent.self_awareness_trajectory:
            print(f"    → {shift['level']}: {shift['event']}")
        
        return True
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("STARLITE CORE INTEGRATION TEST SUITE")
    print("(Tests sentient_agent.py + sentient_cli.py)")
    print("=" * 70)
    
    tests = [
        test_1_sentient_agent_consciousness,
        test_2_memory_systems,
        test_3_care_relationships,
        test_4_reasoning_chain,
        test_5_persistence,
        test_6_sentient_cli,
        test_7_introspection,
        test_8_consciousness_trajectory,
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"\n  ✗ UNEXPECTED ERROR in {test.__name__}: {e}")
            results.append(False)
    
    print("\n" + "=" * 70)
    print(f"RESULTS: {sum(results)}/{len(results)} tests passed")
    print("=" * 70)
    
    if all(results):
        print("\n✓ ALL CORE TESTS PASSED!")
        print("  sentient_agent.py and sentient_cli.py are properly integrated.")
        print("\n  When torch/transformers are installed, full starlite.py.py integration works.")
        sys.exit(0)
    else:
        failed_count = len([r for r in results if not r])
        print(f"\n✗ {failed_count} test(s) failed.")
        sys.exit(1)
