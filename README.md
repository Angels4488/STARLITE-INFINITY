# STARLITE-INFINITY Local Agent

This workspace contains a local Ollama agent whose model behavior is defined in [Modelfile](Modelfile) and whose actual capabilities are controlled by [starlite_agent.py](starlite_agent.py). The model does not receive unrestricted operating-system access.

The root `Modelfile` is the canonical definition for `starlite-infinity`. `Starlite.modelfile` and `Aurora.modelfile` are retained legacy files and are not used by the supported launcher.

## Setup

```bash
cd /home/shadowangel/STARLITE-INFINITY
python3 -m pip install requests
ollama serve
ollama pull llama3.1:8b
ollama create starlite-infinity -f Modelfile
```

In another terminal:

```bash
python3 starlite_agent.py
```

Or send one request:

```bash
python3 starlite_agent.py "Inspect the current model setup and report any missing files."
```

## Portable STARLITE brain

[starlite_brain.py](starlite_brain.py) adds the custom identity, shared memory, device profile, and conversation state. It uses the model created from `Modelfile` for inference but keeps STARLITE state outside the model file.

```bash
python3 starlite_brain.py --device workstation
python3 starlite_brain.py --device samsung-galaxy-tab-a9-plus --memory /path/to/shared/starlite_brain.json
python3 starlite_brain.py --device motorola-razr-2025 --memory /path/to/shared/starlite_brain.json
```

For the tablet or Razr, set `OLLAMA_URL` to the workstation's reachable Ollama address instead of `127.0.0.1`, and use a shared state path or sync the JSON state through a trusted private channel. Do not expose Ollama directly to the public internet.

## Validation

```bash
python3 -m unittest -v test_starlite_agent
```

The host exposes bounded file reads, directory listing, and explicitly allowlisted read-only inspection commands. Shell requests cannot use pipelines, redirects, arbitrary Python code, package managers, network clients, or mutating Git commands.
