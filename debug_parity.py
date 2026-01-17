from src.cube.cube import Cube

c = Cube()
print(f"Initially solved: {c.is_solved()}")
c.apply_move("U")
print(f"After U, solved: {c.is_solved()}")
c.apply_move("U'")
print(f"After U', solved: {c.is_solved()}")
