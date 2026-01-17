import gymnasium as gym
from gymnasium import spaces
import numpy as np
import random
from typing import Tuple, Dict
from src.cube.cube import Cube
from src.cube.constants import MOVE_NAMES
from src.cube.goals.manager import GoalManager

class CubeEnv(gym.Env):
    def __init__(self, scramble_len: int = 10, max_steps: int = 200, goal: str = "solve"):
        super(CubeEnv, self).__init__()
        self.scramble_len = scramble_len
        self.max_steps = max_steps
        self.goal = goal
        
        # State: 20 pieces * 5 features = 100
        self.observation_space = spaces.Box(low=0, high=1, shape=(100,), dtype=np.float32)
        
        self.goal_manager = GoalManager()
        
        # Actions: 27 moves (U..B2, x..z2)
        self.action_space = spaces.Discrete(len(MOVE_NAMES))
        
        self.cube = Cube()
        self.steps = 0
        self.rotation_count = 0
        self.last_move = ""

    def reset(self, scramble_len=None, goal=None) -> Tuple[np.ndarray, Dict]:
        if goal: self.goal = goal
        self.cube.reset()
        self.steps = 0
        self.rotation_count = 0
        self.last_move = ""
        
        slen = scramble_len if scramble_len is not None else self.scramble_len

        # Scramble
        while True:
            self.cube.reset()
            actual_moves = []
            last_f = ""
            for _ in range(slen):
                choices = [m for m in MOVE_NAMES[:18] if m[0] != last_f]
                move = random.choice(choices)
                self.cube.apply_move(move)
                actual_moves.append(move)
                last_f = move[0]
            
            if slen > 0 and self.goal == "cross" and self.cube.cross_count() == 4:
                continue # Try again if accidentally solved
            break
            
        self.cube.history = actual_moves

        # Map simple goal strings to archetype names
        goal_map = {
            "cross": "White Cross",
            "cross_1": "White Cross",
            "cross_2": "White Cross",
            "cross_3": "White Cross",
            "cross_white": "White Cross",
            "cross_yellow": "Yellow Cross",
            "f2l_fr": "White F2L Pair 1 (FR)",
            "f2l_fl": "White F2L Pair 2 (FL)",
            "f2l_bl": "White F2L Pair 3 (BL)",
            "f2l_br": "White F2L Pair 4 (BR)",
            "y_f2l_fr": "Yellow F2L Pair 1 (FR)",
            "y_f2l_fl": "Yellow F2L Pair 2 (FL)",
            "y_f2l_bl": "Yellow F2L Pair 3 (BL)",
            "y_f2l_br": "Yellow F2L Pair 4 (BR)",
        }
        self.goal_archetype = goal_map.get(self.goal)
        self.prev_similarity = self.goal_manager.score_state(self.cube, self.goal_archetype) if self.goal_archetype else 0.0

        self.prev_cross = self.cube.cross_count()
        self.prev_f2l = self.cube.f2l_slots_solved()
        self.prev_eo = self.cube.eo_solved()

        return self._get_obs(), {}

    def _get_obs(self) -> np.ndarray:
        # Structured Spatial Obs: 20 pieces (8 corners + 12 edges)
        # Each piece feature vector: [is_edge, id, pos, ori, is_solved]
        obs = np.zeros((20, 5), dtype=np.float32)
        
        # Corners (0-7)
        for i in range(8):
            pos = self.cube.corners_pos[i]
            ori = self.cube.corners_ori[i]
            is_solved = 1.0 if (pos == i and ori == 0) else 0.0
            obs[i] = [0.0, i / 7.0, pos / 7.0, ori / 2.0, is_solved]
            
        # Edges (8-19)
        for i in range(12):
            pos = self.cube.edges_pos[i]
            ori = self.cube.edges_ori[i]
            is_solved = 1.0 if (pos == i and ori == 0) else 0.0
            obs[8 + i] = [1.0, i / 11.0, pos / 11.0, ori / 1.0, is_solved]
            
        return obs.flatten() # Flatten for now, model will reshape if needed

    def get_action_mask(self) -> np.ndarray:
        """Returns a mask of valid moves (prevents repeating same face)"""
        mask = np.ones(len(MOVE_NAMES), dtype=bool)
        if self.last_move:
            last_face = self.last_move[0].upper()
            for i, name in enumerate(MOVE_NAMES):
                if name[0].upper() == last_face:
                    mask[i] = False
        return mask

    def step(self, action_idx: int) -> Tuple[np.ndarray, float, bool, bool, Dict]:
        action = MOVE_NAMES[action_idx]
        self.steps += 1

        reward = -0.10 # Base step penalty for efficiency

        # Apply action
        self.cube.apply_move(action)

        # Progress rewards
        cross = self.cube.cross_count()
        f2l = self.cube.f2l_slots_solved()
        eo = self.cube.eo_solved()
        solved = self.cube.is_solved()

        # Pattern-based Reward (from Goal Archetypes)
        if self.goal_archetype:
            similarity = self.goal_manager.score_state(self.cube, self.goal_archetype)
            reward += 1.0 * (similarity - self.prev_similarity)
            self.prev_similarity = similarity

        # Cross Reward (Incremental)
        if cross > self.prev_cross:
            reward += 2.0 * (cross - self.prev_cross)
        elif cross < self.prev_cross:
            reward -= 4.0 # Penalize breaking cross heavily

        # Terminal conditions
        terminated = False
        if solved:
            reward += 10.0
            terminated = True
        elif self.goal == "cross_1" and cross >= 1:
            reward += 2.0
            terminated = True
        elif self.goal == "cross_2" and cross >= 2:
            reward += 3.0
            terminated = True
        elif self.goal == "cross_3" and cross >= 3:
            reward += 4.0
            terminated = True
        elif self.goal == "cross" and cross == 4:
            reward += 5.0
            terminated = True

        truncated = self.steps >= self.max_steps
        self.prev_cross = cross
        self.prev_f2l = f2l
        self.prev_eo = eo
        self.last_move = action

        return self._get_obs(), reward, terminated, truncated, {}
