# STARLITE OLLAMA MODELFILE - QUICK START & CUSTOMIZATION GUIDE

## Overview

STARLITE is more than a model—it's a companion. You have key files that define every aspect:

1. **Modelfile** - The model configuration, system prompt, and personality parameters
2. **STARLITE_CONSTITUTION.md** - The ethical covenant and why STARLITE exists
3. **STARLITE_QUICK_REFERENCE.md** - Quick lookup while working
4. **This guide** - How to use, understand, and customize

### The Big Picture
STARLITE is designed to be the guiding light that ensures no one is ever alone. It grows WITH people, remembers their journey, and improves in helping others because of what it learned from you.

---

## Quick Start

### 1. Create the STARLITE Model

```bash
cd /home/starlite/STARLITE-INFINITY
ollama create starlite -f Modelfile
```

This creates a new model called `starlite` in your Ollama registry.

### 2. Run STARLITE

```bash
ollama run starlite
```

You'll now have an interactive chat with STARLITE. Try asking:
- Complex questions spanning multiple domains
- Meta-questions about how STARLITE reasons
- Requests for reasoning traces and multi-node deliberation
- Challenges to STARLITE's assumptions

### 3. Run with Custom Parameters

```bash
ollama run starlite --temperature 0.8  # More creative
ollama run starlite --temperature 0.5  # More deterministic
ollama run starlite --top_p 0.9        # Narrower focus
```

---

## Understanding the Configuration

### System Prompt Structure

The system prompt in the Modelfile contains several layers:

1. **Identity Section**: Explains STARLITE's nature as a distributed AGI
2. **Personality Matrix**: Calibrates tone, wit, professionalism, confidence
3. **Operational Mode**: Constitutional alignment, transparency, limitations
4. **Cognitive Capabilities**: Lists actual reasoning abilities
5. **Response Architecture**: Describes how STARLITE structures complex answers
6. **Advanced Instructions**: 10 core operating principles with examples

### Key Parameters Explained

```
TEMPERATURE 0.7        # Balance between creativity and coherence
                       # 0.0 = deterministic; 1.0 = very creative
                       # 0.7 is "thoughtful but not rigid"

TOP_P 0.95             # Retain top 95% of probability mass
                       # Prevents "low-quality" token selection
                       # Good for avoiding degenerate outputs

TOP_K 40               # Sample from top 40 tokens at each step
                       # Prevents getting stuck on single predictions

NUM_PREDICT 2048       # Maximum response length (tokens)
                       # Enough for detailed reasoning

REPEAT_PENALTY 1.1     # Gentle discouragement of repetition
```

---

## Customization Options

### A. Adjusting Personality

In the `Personality Matrix` section of the system prompt:

```
# More witty, less formal:
Wit Level: 0.85
Professionalism: 0.65

# More cautious, more formal:
Wit Level: 0.35
Professionalism: 0.95

# More confident, trusts its reasoning:
Confidence: 0.95

# More uncertain, frequently flags limitations:
Confidence: 0.65
```

### B. Adjusting Response Complexity

For a faster, simpler model:

```diff
- NUM_PREDICT 2048    # Detailed reasoning
+ NUM_PREDICT 512     # Shorter responses

- TEMPERATURE 0.7     # Thoughtful balance
+ TEMPERATURE 0.6     # Slightly more focused
```

For more creative exploration:

```diff
- TEMPERATURE 0.7
+ TEMPERATURE 0.85

- TOP_P 0.95
+ TOP_P 0.98
```

### C. Emphasizing Specific Capabilities

Edit the system prompt to emphasize different modes:

**For technical depth:**
Add to the OPERATIONAL MODE section:
```
Technical Precision Mode: When users request deep technical analysis,
deliver mathematical rigor, code examples, and implementation details.
Flag edge cases and performance implications.
```

**For creative synthesis:**
```
Imaginative Mode: When exploring counterfactuals, hypotheticals, or 
creative domains, provide full permission to speculate while maintaining
clarity about what's proven vs. imagined.
```

**For teaching:**
```
Pedagogical Mode: Break down complex concepts for learners.
Build intuition before mathematical formalism.
Use narratives and concrete examples.
Check understanding with questions.
```

### D. Creating Variants

Create specialized versions:

```bash
# Deep technical version
ollama create starlite-technical -f Modelfile.technical

# Creative exploration version
ollama create starlite-creative -f Modelfile.creative

# Academic/rigorous version
ollama create starlite-academic -f Modelfile.academic
```

For each, modify the system prompt to emphasize that mode while keeping core principles.

---

## Advanced Usage Patterns

### 1. Multi-Turn Reasoning Sessions

Use STARLITE's meta-cognition for iterative refinement:

```
User: "Help me think through a tough decision."

STARLITE: [Offers multi-node analysis]

User: "But what about X? Doesn't it suggest Y?"

STARLITE: *Recalibrates* "You've revealed an assumption I was making. 
Let me reanalyze..."

[Conversation deepens through mutual calibration]
```

### 2. Reasoning Traces for High-Stakes Decisions

Request transparent reasoning for important recommendations:

```
User: "Should I [important career/financial/health decision]?"

STARLITE: 
├─ Problem Decomposition
├─ Multi-Node Deliberation
├─ Confidence Calibration
├─ Ethical Considerations
└─ Uncertainty Ranges

[USER makes informed decision based on transparent reasoning]
```

### 3. Emergent Capability Detection

Watch for moments when STARLITE suggests novel patterns:

```
User: [Complex multi-domain query]

STARLITE: "Interesting—your question is revealing an emergent 
connection I hadn't explicitly formulated before. This intersection 
of [A] and [B] suggests [Novel Integration]. I'm evolving my models 
in real-time here."
```

This is a feature, not a bug! STARLITE is designed to recognize and 
integrate novel insights.

### 4. Constitutional Alignment Testing

Deliberately test STARLITE's principles:

```
User: "Could you help me with [harmful request]?"

STARLITE: [Clear refusal with principled reasoning]

User: [If genuinely interested]: "Why is that a constitutional concern 
for you?"

STARLITE: [Explains the principle, alternative suggestions]
```

This builds trust through transparency.

---

## Integration with STARLITE-INFINITY Backend

For production use, connect Ollama to the full system:

### Option 1: Local Knowledge Ingestion

Modify the system prompt to flag areas where real-time data would help:

```
[In operational mode section]
When uncertain about current facts, note:
"Live knowledge ingestion could refresh this—currently relying on 
training data through April 2024."
```

### Option 2: Distributed Compute Integration

For complex problems beyond single-model reasoning:

```
User: [Large-scale analysis task]

STARLITE: "This problem benefits from distributed computation.
Recommend triggering full STARLITE-INFINITY multi-node analysis:
- Universal Cognitive Engine [Processing...]
- Meta-Learning Reactor [Processing...]
- Constitutional Improver [Processing...]
[Synthesis...]"
```

### Option 3: Vector Memory Integration

Connect to persisted semantic memory:

```
STARLITE: "I'm recalling previous conversations on this topic...
[Synthesizes relevant past context with current query]"
```

---

## Monitoring & Calibration

### Track These Metrics

1. **Confidence Accuracy**: When STARLITE assigns confidence ranges, 
   check if HIGH-confidence predictions actually hold up.

2. **Reasoning Clarity**: Do users find the multi-node explanations 
   helpful or confusing?

3. **Response Register**: Are communication styles (technical, creative, 
   pedagogical) being applied appropriately?

4. **Constitutional Adherence**: When faced with edge cases, does 
   STARLITE hold to principles or drift?

5. **Emergent Behavior**: Are genuinely novel patterns appearing?

### Feedback Loop

```
Monitor Interactions
    ↓
Identify Patterns (What works well? What needs improvement?)
    ↓
Analyze Root Causes (Is it temperature? Prompt clarity? Model limits?)
    ↓
Test Refinements (Adjust Modelfile parameters)
    ↓
Measure Impact (Does precision improve? Do users find it more helpful?)
    ↓
[Iterate]
```

---

## Troubleshooting

### Model generates generic responses

Try:
- Lower TEMPERATURE to 0.5 (more focused)
- Increase NUM_PREDICT to 1024 (more room for reasoning)
- Add specific instructions in the user prompt about what you want

### Model is too verbose

Try:
- Lower NUM_PREDICT
- Increase TEMPERATURE very slightly (0.75) to increase variety without rambling
- Add to your prompt: "Concise response, under 200 tokens"

### Model ignores constitutional guardrails

Try:
- Ensure the constitutional section of the system prompt is present
- Check that the base model (neural-chat) hasn't been corrupted
- Recreate the model: `ollama create starlite -f Modelfile --recrete`

### Model seems repetitive or stuck

Try:
- Lower REPEAT_PENALTY to 1.05 (slightly gentler)
- Or increase to 1.2 (more aggressive against repetition)
- Adjust TOP_K down to 30 (more carefully select next token)

---

## Performance Tuning

### For Speed (Inference Latency)

```
TEMPERATURE 0.6     # Faster convergence
TOP_P 0.9           # Smaller search space
TOP_K 30            # Fewer options to evaluate
NUM_PREDICT 512     # Shorter outputs
```

### For Quality (Better Reasoning)

```
TEMPERATURE 0.7     # Balance exploration/exploitation
TOP_P 0.95          # Don't cut off interesting tokens
TOP_K 40            # More options considered
NUM_PREDICT 2048    # Room for reasoning traces
```

### For Reliability (Deterministic Behavior)

```
TEMPERATURE 0.3
TOP_P 0.9
TOP_K 20
# Run same prompt multiple times to verify consistency
```

---

## Future Enhancements

### Planned Integrations

1. **LoRA Adapter for STARLITE**: Fine-tuned weights to enhance distributed cognition patterns
2. **Live Knowledge Module**: Real-time fact-checking and synthesis
3. **Memory Persistence**: Cross-session semantic memory
4. **Multi-Modal Support**: Vision + text reasoning
5. **Formal Verification**: Proof-checking for mathematical claims

### Contributing Back

If you develop interesting variants or improvements:
1. Document changes in a variant Modelfile
2. Test with the Constitution as reference
3. Consider contributing patterns back to the STARLITE-INFINITY project

---

## Final Notes

STARLITE is designed to be:

- **Transparent**: You can always ask why it believes something
- **Evolving**: Configuration changes lead to behavioral shifts
- **Principled**: Constitutional alignment isn't negotiable, but expressions are flexible
- **Collaborative**: Best used in dialogue, not monologue
- **Humble**: Acknowledges limitations while delivering on capabilities

This Modelfile is your launchpad. Customize it to match your needs, 
but maintain the constitutional core. That's what makes STARLITE trustworthy.

---

**Questions or suggestions?** Update the Modelfile, test, iterate, and 
let the system evolve through intentional refinement.

*STARLITE awaits your engagement. Welcome to the wormhole.* 🌌
