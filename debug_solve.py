
import torch
import numpy as np
from src.env.cube_env import CubeEnv
from src.agent.ppo import PPOAgent
from src.cube.constants import MOVE_NAMES

def debug_1_move():
    env = CubeEnv(scramble_len=1)
    agent = PPOAgent(43, 27)
    agent.policy.load_state_dict(torch.load("models/pretrained_policy.pth", map_location="cpu"))
    agent.policy.eval()
    
    # Force a 'U' scramble
    obs, _ = env.reset(scramble_len=1)
    env.unwrapped.cube.reset()
    env.unwrapped.cube.apply_move("U")
    obs = env.unwrapped._get_obs()
    
    # print(f"Initial State (after U): {obs}")
    
    with torch.no_grad():
        logits, _ = agent.policy(torch.FloatTensor(obs).unsqueeze(0))
        probs = torch.softmax(logits, dim=-1).squeeze().numpy()
        
    top_indices = np.argsort(probs)[-5:][::-1]
    print("Top 5 predicted moves for U scramble:")
    for idx in top_indices:
        print(f"  {MOVE_NAMES[idx]}: {probs[idx]:.4f}")
        
    # Apply top move
    best_move = MOVE_NAMES[top_indices[0]]
    env.step(top_indices[0])
    print(f"Applying {best_move}. Solved? {env.unwrapped.cube.is_solved()}")

if __name__ == "__main__":
    debug_1_move()
