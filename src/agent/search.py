
import torch
import torch.nn.functional as F
from src.cube.cube import Cube
from src.cube.constants import MOVE_NAMES
import copy

class BeamSearchSolver:
    def __init__(self, model, beam_width=5, max_depth=50):
        self.model = model
        self.beam_width = beam_width
        self.max_depth = max_depth
        self.move_to_idx = {name: i for i, name in enumerate(MOVE_NAMES)}

    def get_obs(self, cube):
        return torch.FloatTensor(np.concatenate([
            cube.corners_pos,
            cube.corners_ori,
            cube.edges_pos,
            cube.edges_ori,
            np.array([
                cube.cross_count(),
                cube.f2l_slots_solved(),
                int(cube.eo_solved())
            ])
        ])).unsqueeze(0)

    def solve(self, start_cube):
        # Beam entry: (score, path, current_cube_state)
        beam = [(0, [], start_cube.copy())]
        
        for depth in range(self.max_depth):
            new_beam = []
            
            for score, path, cube in beam:
                if cube.is_solved():
                    return path
                
                # Get probabilities from model
                obs = self.get_obs(cube)
                with torch.no_grad():
                    logits, _ = self.model(obs)
                    probs = F.softmax(logits, dim=-1).squeeze(0)
                
                # Get top K moves
                top_probs, top_indices = torch.topk(probs, self.beam_width)
                
                for p, idx in zip(top_probs, top_indices):
                    move_name = MOVE_NAMES[idx.item()]
                    
                    # Prevent redundant moves (U U')
                    if path and path[-1].startswith(move_name[0]) and ("'" in move_name or "'" in path[-1]):
                         # Basic check, can be more robust
                         pass

                    new_cube = cube.copy()
                    new_cube.apply_move(move_name)
                    
                    new_score = score + torch.log(p).item()
                    new_beam.append((new_score, path + [move_name], new_cube))
            
            # Keep top K in beam
            new_beam.sort(key=lambda x: x[0], reverse=True)
            beam = new_beam[:self.beam_width]
            
            # Check if any in beam is solved
            for score, path, cube in beam:
                if cube.is_solved():
                    return path
        
        return None # Failed

if __name__ == "__main__":
    import numpy as np
    from src.agent.model import ActorCritic
    # Simple test
    model = ActorCritic(43, 27)
    solver = BeamSearchSolver(model, beam_width=3, max_depth=10)
    test_cube = Cube()
    test_cube.apply_move("R")
    test_cube.apply_move("U")
    path = solver.solve(test_cube)
    print(f"Beam search path: {path}")
