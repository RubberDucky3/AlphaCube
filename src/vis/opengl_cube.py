
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import threading
import time
import os
import copy

from src.env.cube_env import CubeEnv
from src.agent.ppo import PPOAgent
from src.cube.constants import MOVE_NAMES
from src.agent.bc_data import generate_bc_dataset

# Colors
COLORS = {
    'W': (1.0, 1.0, 1.0),
    'Y': (1.0, 1.0, 0.0),
    'G': (0.0, 1.0, 0.0),
    'B': (0.0, 0.0, 1.0),
    'O': (1.0, 0.5, 0.0),
    'R': (1.0, 0.0, 0.0),
    'X': (0.1, 0.1, 0.1)  # Internal / Black
}

# Mapping centers to faces
CENTERS = {
    (0, 1, 0): 'W',   # U
    (0, -1, 0): 'Y',  # D
    (0, 0, 1): 'G',   # F
    (0, 0, -1): 'B',  # B
    (-1, 0, 0): 'O',  # L
    (1, 0, 0): 'R'    # R
}

PIECE_COLOR_MAP = {
    'c': [
        {'U':'W', 'R':'R', 'F':'G'}, # 0:URF
        {'U':'W', 'F':'G', 'L':'O'}, # 1:UFL
        {'U':'W', 'L':'O', 'B':'B'}, # 2:ULB
        {'U':'W', 'B':'B', 'R':'R'}, # 3:UBR
        {'D':'Y', 'F':'G', 'R':'R'}, # 4:DFR
        {'D':'Y', 'L':'O', 'F':'G'}, # 5:DLF
        {'D':'Y', 'B':'B', 'L':'O'}, # 6:DBL
        {'D':'Y', 'R':'R', 'B':'B'}  # 7:DRB
    ],
    'e': [
        {'U':'W', 'R':'R'}, # 0:UR
        {'U':'W', 'F':'G'}, # 1:UF
        {'U':'W', 'L':'O'}, # 2:UL
        {'U':'W', 'B':'B'}, # 3:UB
        {'D':'Y', 'R':'R'}, # 4:DR
        {'D':'Y', 'F':'G'}, # 5:DF
        {'D':'Y', 'L':'O'}, # 6:DL
        {'D':'Y', 'B':'B'}, # 7:DB
        {'F':'G', 'R':'R'}, # 8:FR
        {'F':'G', 'L':'O'}, # 9:FL
        {'B':'B', 'L':'O'}, # 10:BL
        {'B':'B', 'R':'R'}  # 11:BR
    ]
}

C_SLOTS = [
    (1,1,1), (-1,1,1), (-1,1,-1), (1,1,-1),
    (1,-1,1), (-1,-1,1), (-1,-1,-1), (1,-1,-1)
]
E_SLOTS = [
    (1,1,0), (0,1,1), (-1,1,0), (0,1,-1),
    (1,-1,0), (0,-1,1), (-1,-1,0), (0,-1,-1),
    (1,0,1), (-1,0,1), (-1,0,-1), (1,0,-1)
]

class OpenGLCubeVis:
    def __init__(self):
        pygame.init()
        self.display = (800, 600)
        pygame.display.set_mode(self.display, DOUBLEBUF | OPENGL)
        pygame.display.set_caption("AlphaCube RL Visualizer (OpenGL)")
        
        gluPerspective(45, (self.display[0] / self.display[1]), 0.1, 50.0)
        glTranslatef(0.0, 0.0, -10)
        
        glEnable(GL_DEPTH_TEST)
        
        self.cube_state = None
        self.lock = threading.Lock()
        self.running = True
        self.rotation_x = 30
        self.rotation_y = 45
        
        self.title_font = None 
        self.stat_font = None
            
        self.stats = {
            "episode": 0,
            "reward": 0.0,
            "success_rate": 0.0,
            "scramble_len": 1,
            "last_move": "-",
            "phase": "Initializing..."
        }

    def draw_cubie(self, pos, face_colors):
        """
        pos: (x, y, z)
        face_colors: dict {face_id: color_name} 
        Face IDs: 0:+R, 1:-L, 2:+U, 3:-D, 4:+F, 5:-B
        """
        x, y, z = pos
        size = 0.45 # slight gap
        
        vertices = [
            (x+size, y-size, z-size), (x+size, y+size, z-size), (x-size, y+size, z-size), (x-size, y-size, z-size),
            (x+size, y-size, z+size), (x+size, y+size, z+size), (x-size, y-size, z+size), (x-size, y+size, z+size)
        ]
        
        faces = [
            (0, 1, 2, 3), (4, 5, 7, 6), (0, 4, 6, 3), (1, 5, 7, 2), (2, 7, 6, 3), (0, 1, 5, 4)
        ]
        
        # OpenGL Face mappings:
        # 0: +X (Right), 1: -X (Left), 2: +Y (Up), 3: -Y (Down), 4: +Z (Front), 5: -Z (Back)
        glBegin(GL_QUADS)
        # Right (+X)
        color = COLORS[face_colors.get('R', 'X')]
        glColor3fv(color)
        glVertex3fv(vertices[0]); glVertex3fv(vertices[1]); glVertex3fv(vertices[5]); glVertex3fv(vertices[4])
        
        # Left (-X)
        color = COLORS[face_colors.get('L', 'X')]
        glColor3fv(color)
        glVertex3fv(vertices[2]); glVertex3fv(vertices[3]); glVertex3fv(vertices[6]); glVertex3fv(vertices[7])
        
        # Up (+Y)
        color = COLORS[face_colors.get('U', 'X')]
        glColor3fv(color)
        glVertex3fv(vertices[1]); glVertex3fv(vertices[2]); glVertex3fv(vertices[7]); glVertex3fv(vertices[5])
        
        # Down (-Y)
        color = COLORS[face_colors.get('D', 'X')]
        glColor3fv(color)
        glVertex3fv(vertices[0]); glVertex3fv(vertices[3]); glVertex3fv(vertices[6]); glVertex3fv(vertices[4])
        
        # Front (+Z)
        color = COLORS[face_colors.get('F', 'X')]
        glColor3fv(color)
        glVertex3fv(vertices[4]); glVertex3fv(vertices[5]); glVertex3fv(vertices[7]); glVertex3fv(vertices[6])
        
        # Back (-Z)
        color = COLORS[face_colors.get('B', 'X')]
        glColor3fv(color)
        glVertex3fv(vertices[0]); glVertex3fv(vertices[1]); glVertex3fv(vertices[2]); glVertex3fv(vertices[3])
        glEnd()
        
        # Draw outlines
        glColor3fv((0, 0, 0))
        glLineWidth(2)
        glBegin(GL_LINES)
        for edge in [(0,1),(1,2),(2,3),(3,0),(4,5),(5,7),(7,6),(6,4),(0,4),(1,5),(2,7),(3,6)]:
            glVertex3fv(vertices[edge[0]])
            glVertex3fv(vertices[edge[1]])
        glEnd()

    def draw_text(self, text, x, y, font, color=(255, 255, 255)):
        if not font: return
        text_surface = font.render(text, True, color)
        text_data = pygame.image.tostring(text_surface, "RGBA", True)
        
        glWindowPos2d(x, y)
        glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()
        glRotatef(self.rotation_x, 1, 0, 0)
        glRotatef(self.rotation_y, 0, 1, 0)
        
        with self.lock:
            state = self.cube_state
            stats = copy.deepcopy(self.stats)
            
        if state:
            # Draw centers
            for pos, color in CENTERS.items():
                self.draw_cubie(pos, {pos_to_face(pos): color})
            
            # Draw pieces
            for i in range(8):
                piece_idx = state['cp'][i]
                piece_colors = PIECE_COLOR_MAP['c'][piece_idx]
                self.draw_cubie(C_SLOTS[i], piece_colors)
            for i in range(12):
                piece_idx = state['ep'][i]
                piece_colors = PIECE_COLOR_MAP['e'][piece_idx]
                self.draw_cubie(E_SLOTS[i], piece_colors)
        
        glPopMatrix()
        
        # HUD Overlay
        glDisable(GL_DEPTH_TEST)
        self.draw_text(f"AlphaCube Protocol: {stats.get('phase', 'Initializing...')}", 20, 560, self.title_font, (0, 255, 127))
        self.draw_text(f"Episode: {stats.get('episode', 0)}", 20, 520, self.stat_font)
        self.draw_text(f"Scramble Len: {stats.get('scramble_len', 1)}", 20, 495, self.stat_font)
        self.draw_text(f"Success Rate: {stats.get('success_rate', 0):.1f}%", 20, 470, self.stat_font, (255, 215, 0))
        self.draw_text(f"Goal Similarity: {stats.get('similarity', 0):.1f}%", 20, 445, self.stat_font, (135, 206, 250))
        
        # Phase Validation
        self.draw_text(f"Last Move: {stats.get('last_move', '-')}", 600, 560, self.stat_font)
        self.draw_text(f"Reward: {stats.get('reward', 0):.2f}", 600, 530, self.stat_font)
        
        if stats.get('is_solved'):
            self.draw_text("CUBE SOLVED", 300, 300, self.title_font, (0, 255, 0))
        
        glEnable(GL_DEPTH_TEST)
        pygame.display.flip()

def pos_to_face(pos):
    x, y, z = pos
    if x == 1: return 'R'
    if x == -1: return 'L'
    if y == 1: return 'U'
    if y == -1: return 'D'
    if z == 1: return 'F'
    if z == -1: return 'B'
    return None

def training_thread(vis):
    DB_PATH = "reconstructions.db"
    MODEL_PATH = "models/pretrained_policy.pth"
    
    print("Training thread started...")
    # Focus expert data on cross
    expert_states, expert_actions, expert_dists = generate_bc_dataset(DB_PATH, limit=20000, stage="cross")
    
    # Start with FULL WCA scrambles (20 moves)
    current_scramble_len = 20
    update_timestep = 4096
    memory = []
    
    # Start with CROSS_1 goal (Solve 1 edge first)
    goal = "cross_1"
    env = CubeEnv(scramble_len=20, max_steps=50, goal=goal)
    obs_dim = 100 # pieces (20) * features (5)
    agent = PPOAgent(obs_dim, env.action_space.n, lr=5e-4) 
    if os.path.exists(MODEL_PATH):
        agent.load_pretrained(MODEL_PATH)
        
    successes = []
    prev_phase = ""
    timestep = 0
    total_episodes = 500000
    
    for ep in range(1, total_episodes):
        # Reset with current complexity
        obs, _ = env.reset(scramble_len=current_scramble_len, goal=goal)
        ep_reward = 0
        ep_moves = []
        
        # Scramble tracking (cube.history is populated during reset)
        scramble_moves = env.unwrapped.cube.history.copy()

        for _ in range(env.max_steps):
            mask = env.get_action_mask()
            action, log_prob, val = agent.select_action(obs, mask=mask)
            next_obs, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            
            # PPO memory expects (s, a, logp, r, done)
            memory.append((obs, action, log_prob, reward, done))
            
            ep_reward += reward
            ep_moves.append(MOVE_NAMES[action])
            obs = next_obs
            timestep += 1

            if done:
                if terminated:
                    print(f"\n[SUCCESS] Goal: {goal.upper()} | Moves: {len(ep_moves)}")
                    print(f"Scramble: {' '.join(scramble_moves)}")
                    print(f"Solution: {' '.join(ep_moves)}\n")
                break
                
            # Phase Tracking for HUD
            cube = env.unwrapped.cube
            cross = cube.cross_count()
            f2l = cube.f2l_slots_solved()
            eo = cube.eo_solved()
            
            if cross < 4: phase = "Cross"
            elif f2l < 4: phase = f"F2L ({f2l}/4)"
            elif not eo: phase = "EO"
            else: phase = "Last Layer"

            if phase != prev_phase:
                prev_phase = phase

            # Update Vis State
            if timestep % 10 == 0:
                with vis.lock:
                    vis.cube_state = {
                        'cp': cube.corners_pos.tolist(),
                        'co': cube.corners_ori.tolist(),
                        'ep': cube.edges_pos.tolist(),
                        'eo': cube.edges_ori.tolist()
                    }
                    vis.stats['episode'] = ep
                    vis.stats['phase'] = phase
                    vis.stats['scramble_len'] = current_scramble_len
                    vis.stats['is_solved'] = terminated
                    vis.stats['reward'] = reward
                    vis.stats['last_move'] = ep_moves[-1] if ep_moves else "-"
                    vis.stats['success_rate'] = (sum(successes)/len(successes)*100) if successes else 0
                    if hasattr(env.unwrapped, 'prev_similarity'):
                        vis.stats['similarity'] = env.unwrapped.prev_similarity * 100
            
            if len(memory) >= update_timestep:
                idx = np.random.choice(len(expert_states), 128)
                expert_batch = (expert_states[idx], expert_actions[idx], expert_dists[idx])
                agent.update(memory, expert_batch=expert_batch)
                memory = []
                
                # Dynamic update of expert knowledge (every 10 updates)
                if timestep % (update_timestep * 10) == 0:
                     expert_states, expert_actions, expert_dists = generate_bc_dataset(DB_PATH, limit=50000, stage="cross")
                     print(f"Cross Expert Knowledge Updated: {len(expert_states)} samples")

            time.sleep(0.005) # Speed up simulation
            
            if done:
                is_successful = terminated # For cross goal, terminated means cross=4
                successes.append(1 if is_successful else 0)
                if len(successes) > 100: successes.pop(0)
                avg = sum(successes)/len(successes)
                
                if ep % 10 == 0:
                    sim_pct = env.unwrapped.prev_similarity * 100
                    print(f"[EP {ep}] {goal.upper()} | Avg Success: {avg*100:.1f}% | Similarity: {sim_pct:.1f}% | Len: {current_scramble_len} | Reward: {ep_reward:.2f}")

                # Curriculum logic (Incremental Cross Mastery)
                if len(successes) >= 100:
                    if avg >= 0.95:
                        if goal == "cross_1":
                            print("CROSS_1 MASTERED. Moving to CROSS_2.")
                            goal = "cross_2"
                        elif goal == "cross_2":
                            print("CROSS_2 MASTERED. Moving to CROSS_3.")
                            goal = "cross_3"
                        elif goal == "cross_3":
                            print("CROSS_3 MASTERED. Moving to FULL CROSS.")
                            goal = "cross"
                        elif goal == "cross":
                            print("FULL CROSS MASTERED. Moving to F2L Pair 1.")
                            goal = "f2l_fr"
                        successes = []
                    
                    # Adaptive downscaling DISABLED (Stay at WCA depth)
                break
        
        if ep % 500 == 0:
            torch.save(agent.policy.state_dict(), f"models/policy_ep{ep}.pth")
            
        time.sleep(0.01)

if __name__ == "__main__":
    vis = OpenGLCubeVis()
    
    t = threading.Thread(target=training_thread, args=(vis,))
    t.daemon = True
    t.start()
    
    dragging = False
    last_mouse_pos = None
    clock = pygame.time.Clock()
    
    while vis.running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                vis.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: dragging = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1: dragging = False
            elif event.type == pygame.MOUSEMOTION:
                if dragging:
                    new_pos = pygame.mouse.get_pos()
                    if last_mouse_pos:
                        vis.rotation_y += (new_pos[0] - last_mouse_pos[0]) * 0.5
                        vis.rotation_x += (new_pos[1] - last_mouse_pos[1]) * 0.5
                    last_mouse_pos = new_pos
            if not dragging:
                last_mouse_pos = pygame.mouse.get_pos()
                
        vis.render()
        clock.tick(60)
    
    pygame.quit()
