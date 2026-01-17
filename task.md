# AlphaCube RL Task List

## Phase 1: Core Simulator (Done)
- [x] Cubie-based state representation
- [x] Full move logic (Turns + Rotations)
- [x] CFOP progress detection

## Phase 2: Environment & RL (Done)
- [x] Gymnasium wrapper
- [x] Dense reward shaping (CFOP/ZB style)
- [x] Actor-Critic (PPO) architecture

## Phase 3: Machine Learning Protocol (Done)
- [x] Behavior Cloning from recon.db
- [x] Hybrid Loss (PPO + Imitation)
- [x] Curriculum learning logic

## Phase 4: Visualization (Done)
- [x] Web-based monitoring (Three.js)
- [x] Desktop renderer (PyOpenGL)
- [x] Mouse-controlled camera

## Phase 5: Search & Optimization (In Progress)
- [x] Beam Search solver
- [/] Planning CFOP stage completion
- [ ] Refining reward functions (Soft CFOP/ZB biases)
- [ ] Mapping curriculum stages to CFOP goals
- [ ] Training to standard WCA scrambles

## Future
- [ ] Multi-thread training
- [ ] Advanced EO/ZBLL analysis
- [ ] Solver API for external apps
