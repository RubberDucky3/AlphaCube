# AlphaCube 🧩⚡️

AlphaCube is a high-performance Rubik's Cube F2L (First Two Layers) solver designed for speed, ergonomics, and advanced solving strategies. It leverages a compiled C++ backend to find optimal and semi-optimal solutions for the Yellow Cross and F2L stages in near-real-time.

## Key Features 🚀

- **High-Performance C++ Core**: Integration with a specialized C++ solver (`solver_bridge`) for lightning-fast computation (over 100x faster than traditional Python-only methods).
- **X-Cross & Multi-Slotting Intelligence**: The solver proactively searches for and prioritizes solutions that solve multiple F2L pairs simultaneously (XX-Cross, XXX-Cross, etc.).
- **Ergonomic Move Optimization**: Prioritizes solutions that minimize awkward `B` (Back) moves by using `y` rotations and ergonomic face selections.
- **Continuous Orientation Tracking**: Instructions include relative rotations from the previous state, allowing for a seamless, continuous solve experience without resetting your cube orientation.
- **Yellow Cross Branding**: Tailored specifically for Yellow Cross solvers.
- **Interactive Web UI**: A modern, responsive Flask-based web interface for easy scramble input and clear, step-by-step solution visualization.

## Technical Stack 🛠️

- **Backend**: Python (Flask) orchestrating C++ subprocesses.
- **Solver Engine**: Compiled C++ implementing depth-limited search and pruning tables.
- **Frontend**: Vanilla HTML5, CSS3, and JavaScript with a focus on premium aesthetics and smooth animations.
- **Git Integration**: Ready for deployment and collaborative development.

## Getting Started 🏁

### Prerequisites
- Python 3.10+
- A C++ compiler (GCC/Clang) for rebuilding the solver bridge if necessary.

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/RubberDucky3/AlphaCube.git
   cd AlphaCube
   ```
2. Set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. Run the development server:
   ```bash
   cd ui_cross_solver
   python app.py
   ```
4. Open `http://localhost:5000` in your browser.

## Roadmap 🗺️

- [ ] **React Native Integration**: Porting the C++ core to mobile via JSI for offline support.
- [ ] **Advanced OLL/PLL Support**: Extending the solver to handle the full CFOP pipeline.
- [ ] **Bluetooth Cube Integration**: Future support for smart cubes.

---
Developed by [RubberDucky3](https://github.com/RubberDucky3)
