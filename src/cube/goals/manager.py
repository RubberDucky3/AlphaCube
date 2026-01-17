import json
import os
import numpy as np

class GoalManager:
    def __init__(self, goals_dir="src/cube/goals"):
        self.goals = {}
        self.goals_dir = goals_dir
        self.load_goals()

    def load_goals(self):
        if not os.path.exists(self.goals_dir):
            return
        for filename in os.listdir(self.goals_dir):
            if filename.endswith(".json"):
                path = os.path.join(self.goals_dir, filename)
                with open(path, 'r') as f:
                    goal_data = json.load(f)
                    self.goals[goal_data['name']] = goal_data

    def score_state(self, cube, goal_name):
        if goal_name not in self.goals:
            return 0.0
        
        goal = self.goals[goal_name]
        score = 0.0
        total_parts = len(goal.get('required_edges', [])) + len(goal.get('required_corners', []))
        
        if total_parts == 0:
            return 1.0

        for req in goal.get('required_edges', []):
            current_pos = np.where(cube.edges_pos == req['id'])[0][0]
            current_ori = cube.edges_ori[current_pos]
            if current_pos == req['pos'] and current_ori == req['ori']:
                score += 1.0
            elif current_pos == req['pos']:
                score += 0.5 # Right place, wrong orientation

        for req in goal.get('required_corners', []):
            current_pos = np.where(cube.corners_pos == req['id'])[0][0]
            current_ori = cube.corners_ori[current_pos]
            if current_pos == req['pos'] and current_ori == req['ori']:
                score += 1.0
            elif current_pos == req['pos']:
                score += 0.5

        return score / total_parts

    def get_visual(self, goal_name):
        if goal_name in self.goals:
            return "\n".join(self.goals[goal_name].get('visual', []))
        return "No visualization available."
