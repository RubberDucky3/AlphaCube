from flask import Flask, jsonify, render_template
import threading
import time
import numpy as np
import os

# Import training components
from src.env.cube_env import CubeEnv
from src.agent.ppo import PPOAgent
from src.cube.constants import MOVE_NAMES
from src.agent.bc_data import generate_bc_dataset
from src.agent.train_bc import train_bc

app = Flask(__name__)

# Global state
training_state = {
    "cube_state": None,
    "episode": 0,
    "reward": 0,
    "last_move": "",
    "is_solved": False,
    "running": False,
    "scramble_len": 1,
    "success_rate": 0,
    "bc_status": "Idle"
}

# Shared lock
lock = threading.Lock()

def training_loop():
    global training_state
    
    DB_PATH = "reconstructions.db"
    MODEL_PATH = "models/pretrained_policy.pth"
    
    # 1. Behavior Cloning Pre-training
    if not os.path.exists(MODEL_PATH):
        with lock: training_state["bc_status"] = "Pre-training (BC)..."
        train_bc(DB_PATH, MODEL_PATH, epochs=20)
        with lock: training_state["bc_status"] = "BC Complete"
    
    print("Loading BC dataset for hybrid loss...")
    expert_states, expert_actions = generate_bc_dataset(DB_PATH, limit=1000)
    
    current_scramble_len = 1
    max_steps = 200
    max_episodes = 20000 
    update_timestep = 2048 
    
    env = CubeEnv(scramble_len=current_scramble_len, max_steps=max_steps)
    obs_dim = env.observation_space.shape[0]
    act_dim = env.action_space.n
    
    agent = PPOAgent(obs_dim, act_dim, lr=0.001, gamma=0.99, k_epochs=4, eps_clip=0.2)
    agent.load_pretrained(MODEL_PATH)
    
    timestep = 0
    memory = []
    successes = [] # Track last 100 episodes
    
    for i_episode in range(1, max_episodes+1):
        state, _ = env.reset(scramble_len=current_scramble_len)
        current_ep_reward = 0
        
        # Update state for UI
        with lock:
            training_state["episode"] = i_episode
            training_state["is_solved"] = False
            training_state["cube_state"] = _serialize_cube(env.unwrapped.cube)
            training_state["scramble_len"] = current_scramble_len
        
        while True:
            if not training_state.get("running", True):
                time.sleep(0.5)
                continue

            timestep += 1
            
            # Action
            action_idx, log_prob, val = agent.select_action(state)
            action_name = MOVE_NAMES[action_idx]
            
            next_state, reward, terminated, truncated, _ = env.step(action_idx)
            done = terminated or truncated
            
            # Save data
            memory.append((state, action_idx, log_prob, reward, done, val))
            state = next_state
            current_ep_reward += reward
            
            # Create a UI update
            # Only update UI every few steps or if solved to keep performance
            if timestep % 4 == 0 or env.unwrapped.cube.is_solved():
                with lock:
                    training_state["cube_state"] = _serialize_cube(env.unwrapped.cube)
                    training_state["reward"] = round(current_ep_reward, 2)
                    training_state["last_move"] = action_name
                    training_state["is_solved"] = env.unwrapped.cube.is_solved()

            # Throttle for visualization
            time.sleep(0.01) 

            # Update PPO
            if len(memory) >= update_timestep:
                # Sample expert batch for hybrid loss
                idx = np.random.choice(len(expert_states), 128)
                expert_batch = (expert_states[idx], expert_actions[idx])
                
                agent.update(memory, expert_batch=expert_batch)
                memory = []
                
            if done:
                successes.append(1 if env.unwrapped.cube.is_solved() else 0)
                if len(successes) > 100:
                    successes.pop(0)
                
                avg_success = sum(successes) / len(successes) if successes else 0
                with lock:
                    training_state["success_rate"] = round(avg_success * 100, 1)
                
                # Curriculum logic
                if len(successes) >= 50 and avg_success >= 0.8:
                    if current_scramble_len < 25:
                        current_scramble_len += 1
                        successes = [] # Reset tracking for new level
                        print("Increasing scramble length to {}".format(current_scramble_len))
                break
        
        time.sleep(0.1)

def _serialize_cube(cube):
    """
    Convert cube state to a simpler format for JSON.
    We need to send: 
    - 8 Corner positions
    - 8 Corner orientations
    - 12 Edge positions
    - 12 Edge orientations
    """
    return {
        "cp": cube.corners_pos.tolist(),
        "co": cube.corners_ori.tolist(),
        "ep": cube.edges_pos.tolist(),
        "eo": cube.edges_ori.tolist()
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/state')
def get_state():
    with lock:
        return jsonify(training_state)

@app.route('/toggle')
def toggle():
    with lock:
        training_state["running"] = not training_state["running"]
    return jsonify({"running": training_state["running"]})

if __name__ == '__main__':
    print("Starting AlphaCube Training Thread...")
    training_state["running"] = True
    t = threading.Thread(target=training_loop)
    t.daemon = True
    t.start()
    
    print("Launching Flask Server on http://0.0.0.0:5000")
    # Run server on all interfaces
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=5000)
