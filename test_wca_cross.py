import torch
import numpy as np
import random
from src.env.cube_env import CubeEnv
from src.agent.ppo import PPOAgent
from src.cube.constants import MOVE_NAMES

def test_wca_cross(model_path="models/pretrained_policy.pth", num_tests=50, scramble_len=20):
    env = CubeEnv(scramble_len=scramble_len, max_steps=60, goal="cross")
    obs_dim = 100
    agent = PPOAgent(obs_dim, env.action_space.n)
    
    try:
        agent.load_pretrained(model_path)
    except Exception as e:
        print(f"Failed to load model: {e}")
        return

    success_count = 0
    total_moves = 0
    
    print(f"Testing {num_tests} Cross solves with {scramble_len}-move WCA scrambles...")
    
    for i in range(num_tests):
        obs, _ = env.reset(scramble_len=scramble_len, goal="cross")
        scramble = " ".join(env.unwrapped.cube.history)
        
        done = False
        moves = []
        while not done:
            mask = env.get_action_mask()
            action, _, _ = agent.select_action(obs, mask=mask)
            obs, reward, terminated, truncated, _ = env.step(action)
            moves.append(MOVE_NAMES[action])
            done = terminated or truncated
            
        if terminated:
            success_count += 1
            total_moves += len(moves)
            print(f"Test {i+1}: SUCCESS in {len(moves)} moves.")
        else:
            similarity = env.unwrapped.prev_similarity * 100
            print(f"Test {i+1}: FAILED (Similarity: {similarity:.1f}%)")

    success_rate = (success_count / num_tests) * 100
    avg_moves = (total_moves / success_count) if success_count > 0 else 0
    print(f"\nResults for {scramble_len}-move scramble:")
    print(f"Success Rate: {success_rate:.1f}%")
    print(f"Avg Moves (Successful): {avg_moves:.2f}")

if __name__ == "__main__":
    test_wca_cross()
