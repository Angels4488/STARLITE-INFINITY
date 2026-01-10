import asyncio
from src.modules.universal_cognitive_engine import UniversalCognitiveEngine
from src.utils.config import Config
from src.utils.recorder import Recorder

async def test_uce():
    config = Config()
    recorder = Recorder()
    uce = UniversalCognitiveEngine(config, recorder=recorder)
    task = type('Task', (), {'query': 'Test task', 'context': 'test'})()
    result = uce.process_arbitrary_task(task, compute_budget=100)
    assert "Summarized" in result
    print("UCE test passed")

if __name__ == "__main__":
    asyncio.run(test_uce())
