import numpy as np
from src.env.cube_env import CubeEnv
from src.agent.ppo import PPOAgent

def train():
    # Hyperparameters
    scramble_len = 5 # Start small
    max_steps = 200
    max_episodes = 1000
    update_timestep = 2000 
    
    env = CubeEnv(scramble_len=scramble_len, max_steps=max_steps)
    obs_dim = env.reset().shape[0]
    act_dim = env.action_space_size
    
    agent = PPOAgent(obs_dim, act_dim, lr=0.002, gamma=0.99, k_epochs=4, eps_clip=0.2)
    
    timestep = 0
    memory = []
    
    for i_episode in range(1, max_episodes+1):
        state = env.reset()
        current_ep_reward = 0
        
        while True:
            timestep += 1
            
            # Action
            action, log_prob, val = agent.select_action(state)
            next_state, reward, done, _ = env.step(action)
            
            # Save data
            memory.append((state, action, log_prob, reward, done, val))
            
            state = next_state
            current_ep_reward += reward
            
            # Update PPO
            if timestep % update_timestep == 0:
                agent.update(memory)
                memory = []
                timestep = 0
                
            if done:
                break
                
        print(f"Episode {i_episode} \t Reward: {current_ep_reward:.2f} \t Solved: {env.cube.is_solved()}")
        
        if i_episode % 25 == 0:
            # Curriculum: Increase scramble length if doing well? 
            # For now just print status.
            pass

if __name__ == '__main__':
    train()
