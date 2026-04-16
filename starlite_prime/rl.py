import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random
import queue
import multiprocessing
import optuna
from typing import List, Tuple

from .config import StarliteConfig

class EvolutionEngine(nn.Module):
    """
    The Anima Mundi of the Agent, a neural forge where raw potential is
    hammered into intelligent action. This network serves as the soul,
    learning and evolving through the crucible of the GridWorld.
    """
    def __init__(self, input_size: int, output_size: int, hidden_layers: int, layer_size: int):
        super().__init__()
        layers = []
        layers.append(nn.Linear(input_size, layer_size))
        layers.append(nn.ReLU())
        for _ in range(hidden_layers - 1):
            layers.append(nn.Linear(layer_size, layer_size))
            layers.append(nn.ReLU())
        layers.append(nn.Linear(layer_size, output_size))
        self.network = nn.Sequential(*layers)

    def forward(self, x):
        return self.network(x)

class GridWorld:
    """A simulated reality, a pocket dimension for agents to learn and grow."""
    def __init__(self, size=StarliteConfig.GRID_SIZE, max_obstacles=StarliteConfig.MAX_OBSTACLES):
        self.size = size
        self.max_obstacles = max_obstacles
        self.state_shape = (3, size, size)
        self.reset()

    def reset(self):
        self.agent_pos = [random.randint(0, self.size-1), random.randint(0, self.size-1)]
        self.goal_pos = self._random_position(exclude=[self.agent_pos])
        self.obstacles = [self._random_position(exclude=[self.agent_pos, self.goal_pos]) for _ in range(random.randint(1, self.max_obstacles))]
        return self.get_state()

    def _random_position(self, exclude=None) -> List[int]:
        exclude = exclude or []
        while True:
            pos = [random.randint(0, self.size-1), random.randint(0, self.size-1)]
            if pos not in exclude: return pos

    def get_state(self) -> np.ndarray:
        state = np.zeros(self.state_shape, dtype=np.float32)
        state[0, self.agent_pos[0], self.agent_pos[1]] = 1
        state[1, self.goal_pos[0], self.goal_pos[1]] = 1
        for obs in self.obstacles: state[2, obs[0], obs[1]] = 1
        return state.flatten()

    def step(self, action: int) -> Tuple[np.ndarray, float, bool]:
        moves = [[-1, 0], [1, 0], [0, -1], [0, 1]]
        new_pos = [self.agent_pos[0] + moves[action][0], self.agent_pos[1] + moves[action][1]]

        if (0 <= new_pos[0] < self.size and 0 <= new_pos[1] < self.size and new_pos not in self.obstacles):
            self.agent_pos = new_pos

        done = (self.agent_pos == self.goal_pos)
        reward = 10.0 if done else -0.1
        return self.get_state(), reward, done

def train_rl_core(status_queue: multiprocessing.Queue, control_queue: multiprocessing.Queue, params: dict):
    """
    The training grounds where an agent is subjected to trials of fire,
    learning the path to its goal through reinforcement.
    """
    try:
        env = GridWorld()
        device = "cuda" if torch.cuda.is_available() else "cpu"
        agent = EvolutionEngine(
            input_size=np.prod(env.state_shape),
            output_size=4,
            hidden_layers=params['hidden_layers'],
            layer_size=params['layer_size']
        ).to(device)
        optimizer = optim.Adam(agent.parameters(), lr=params['lr'])

        for episode in range(StarliteConfig.RL_EPISODES):
            try:
                if control_queue.get_nowait() == 'stop': break
            except queue.Empty: pass

            state = torch.tensor(env.reset(), device=device)
            done = False
            total_reward = 0

            while not done:
                q_values = agent(state)
                action = torch.argmax(q_values).item()
                next_state_arr, reward, done = env.step(action)
                total_reward += reward

                target = reward
                if not done:
                    with torch.no_grad():
                        next_q = agent(torch.tensor(next_state_arr, device=device)).max()
                        target += params['discount'] * next_q

                loss = (q_values[action] - target).pow(2)
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                state = torch.tensor(next_state_arr, device=device)

            progress = (episode + 1) / StarliteConfig.RL_EPISODES
            status_queue.put(('progress', progress))
            status_queue.put(('update', {'agent_pos': env.agent_pos, 'goal_pos': env.goal_pos, 'obstacles': env.obstacles, 'reward': total_reward}))

        status_queue.put(('status', "Training complete."))
    except Exception as e:
        status_queue.put(('error', f"RL training failed: {e}"))

def objective(trial: optuna.trial.Trial, status_queue: multiprocessing.Queue) -> float:
    """
    The celestial oracle (Optuna) consults this function to find the most
    promising path for an agent's evolution. It suggests parameters, runs a
    short training, and measures the agent's final wisdom (reward).
    """
    # Define the search space for the agent's soul
    lr = trial.suggest_float("lr", 1e-5, 1e-2, log=True)
    discount = trial.suggest_float("discount", 0.9, 0.999)
    hidden_layers = trial.suggest_int("hidden_layers", 1, 3)
    layer_size = trial.suggest_categorical("layer_size", [32, 64, 128])

    params = {'lr': lr, 'discount': discount, 'hidden_layers': hidden_layers, 'layer_size': layer_size}

    # Run a condensed training simulation
    env = GridWorld()
    device = "cpu" # Use CPU for faster parallel trials
    agent = EvolutionEngine(np.prod(env.state_shape), 4, hidden_layers, layer_size).to(device)
    optimizer = optim.Adam(agent.parameters(), lr=lr)

    total_rewards = []
    # Use fewer episodes for faster optimization trials
    for episode in range(50):
        state = torch.tensor(env.reset(), device=device)
        done = False
        episode_reward = 0
        while not done:
            q_values = agent(state)
            action = torch.argmax(q_values).item()
            next_state_arr, reward, done = env.step(action)
            episode_reward += reward
            target = reward + (discount * agent(torch.tensor(next_state_arr, device=device)).max() if not done else 0)
            loss = (q_values[action] - target).pow(2)
            optimizer.zero_grad(); loss.backward(); optimizer.step()
            state = torch.tensor(next_state_arr, device=device)
        total_rewards.append(episode_reward)

    avg_reward = np.mean(total_rewards[-10:]) # Evaluate based on final performance
    status_queue.put(('optuna_trial', f"Trial {trial.number}: Reward={avg_reward:.2f} | Params={trial.params}"))
    return avg_reward

def optimize_rl_agent(status_queue: multiprocessing.Queue):
    """
    Initiates the grand ritual of optimization. Optuna will seek the divine
    proportions for the agent's neural architecture and learning parameters.
    """
    try:
        study = optuna.create_study(direction="maximize")
        study.optimize(lambda trial: objective(trial, status_queue), n_trials=StarliteConfig.RL_OPTIMIZATION_TRIALS)

        status_queue.put(('status', "Optimization complete!"))
        status_queue.put(('best_params', study.best_trial.params))
    except Exception as e:
        status_queue.put(('error', f"Optimization failed: {e}"))
