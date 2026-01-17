from src.cube.goals.manager import GoalManager

def print_goal_visuals():
    manager = GoalManager()
    for name, goal in manager.goals.items():
        print(f"Goal: {name}")
        print("-" * 20)
        print(manager.get_visual(name))
        print("\n")

if __name__ == "__main__":
    print_goal_visuals()
