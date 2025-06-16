
from sympy import symbols, Matrix, Eq
import sympy as sp
import find_solution
def point_line_distance(point, line):
  return ((point - line[0]).cross(line[1])).norm() / (line[1]).norm()

def find_best_transformation(source_points, target_lines):
  #define equations
  r11, r12, r13, r21, r22, r23, r31, r32, r33 = symbols('r11 r12 r13 r21 r22 r23 r31 r32 r33', real=True)
  R = Matrix([[r11, r12, r13], [r21, r22, r23], [r31, r32, r33]])
  t1, t2, t3 = symbols('t1 t2 t3', real=True)
  t = Matrix([t1, t2, t3])
  transformed_points = (R*(source_points.T) + Matrix.hstack(*[t] * source_points.rows)).T
  distance_error_sum_squared_equation = (sum((point_line_distance(transformed_points.row(i), target_lines[i]))**2 for i in range(transformed_points.rows))).simplify()


  R_is_rotation_matrix_equations = [Eq(R * R.T, Matrix.eye(3)), Eq(R.det(), 1)]

  equations = [eq.simplify() for eq in R_is_rotation_matrix_equations]
  #define variables
  R_variables = [r11, r12, r13, r21, r22, r23, r31, r32, r33]
  t_variables = [t1, t2, t3]
  variables = R_variables + t_variables
  #find solution
  solution = find_solution.find_solution(distance_error_sum_squared_equation, equations, variables)
  if solution:
    solution = {key.replace("Global`", ""): value for key, value in solution.items()}
    # Extract rotation matrix R
    best_R_found = Matrix([
        [solution['r11'], solution['r12'], solution['r13']],
        [solution['r21'], solution['r22'], solution['r23']],
        [solution['r31'], solution['r32'], solution['r33']]
    ])

    # Extract translation vector t
    best_t_found = Matrix([
        [solution['t1']],
        [solution['t2']],
        [solution['t3']]
    ])
    return best_R_found, best_t_found
  else:
    print("Optimization failed, no solution found.")
    return Matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]]), Matrix([0, 0, 0])

