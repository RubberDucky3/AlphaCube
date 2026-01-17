
import torch
import numpy as np
from src.env.cube_env import CubeEnv
from src.agent.ppo import PPOAgent
from src.cube.constants import MOVE_NAMES

def evaluate_model(model_path, num_solves=50, scramble_len=20, max_steps=100):
    env = CubeEnv(scramble_len=scramble_len, max_steps=max_steps)
    obs_dim = env.observation_space.shape[0]
    act_dim = env.action_space.n
    
    agent = PPOAgent(obs_dim, act_dim)
    agent.policy.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
    agent.policy.eval()
    
    success_count = 0
    total_moves = 0
    total_rotations = 0
    
    # Stage success counters
    stages = {"Cross": 0, "F2L": 0, "EO": 0, "Solved": 0}
    
    for i in range(num_solves):
        obs, _ = env.reset(scramble_len=scramble_len)
        moves = 0
        solved = False
        
        # Track max stage reached
        max_cross = 0
        max_f2l = 0
        has_eo = False
        
        for _ in range(max_steps):
            with torch.no_grad():
                action_idx, _, _ = agent.select_action(obs)
            
            obs, reward, terminated, truncated, _ = env.step(action_idx)
            moves += 1
            
            # Update stage tracking
            max_cross = max(max_cross, env.unwrapped.cube.cross_count())
            max_f2l = max(max_f2l, env.unwrapped.cube.f2l_slots_solved())
            if env.unwrapped.cube.eo_solved(): has_eo = True
            
            if terminated:
                solved = True
                break
            if truncated:
                break
        
        if max_cross == 4: stages["Cross"] += 1
        if max_f2l == 4: stages["F2L"] += 1
        if has_eo: stages["EO"] += 1
        
        if solved:
            success_count += 1
            total_moves += moves
            total_rotations += env.unwrapped.rotation_count
            stages["Solved"] += 1
            print(f"Solve {i+1}: Success in {moves} moves ({env.unwrapped.rotation_count} rotations)")
        else:
            print(f"Solve {i+1}: Failed (Cross: {max_cross}, F2L: {max_f2l})")
            
    avg_moves = total_moves / success_count if success_count > 0 else 0
    avg_rots = total_rotations / success_count if success_count > 0 else 0
    success_rate = (success_count / num_solves) * 100
    
    print("\n" + "="*40)
    print(f"RESULTS FOR: {model_path}")
    print(f"Success Rate: {success_rate:.1f}%")
    print(f"Avg Moves (Win): {avg_moves:.1f}")
    print(f"Avg Rotations (Win): {avg_rots:.1f}")
    print("-" * 20)
    print("STAGE SUCCESS RATES:")
    for stage, count in stages.items():
        print(f"  {stage:8}: {(count/num_solves*100):.1f}%")
    print("="*40)
    
    return success_rate, avg_moves

if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "models/pretrained_policy.pth"
    evaluate_model(path, num_solves=20, scramble_len=10)
