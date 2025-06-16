from sympy import symbols, Matrix

from scipy.stats import special_ortho_group #for a random rotation matrix
import numpy as np

import find_best_transformation


def define_n_random_points(n):
  points = Matrix([np.random.uniform(-100, 100, 3) for _ in range(n)])
  return points

#the code currently doesnt work with symbolic points as input and only numeric points.
# def define_n_symbolic_points(n):
#  points = Matrix([[symbols(f'x{i}', real=True), symbols(f'y{i}', real=True), symbols(f'z{i}', real=True)] for i in range(1, n + 1)])
#  return points


def create_transformation(): #create rotation matrix and translation
  rotation_matrix = Matrix(special_ortho_group.rvs(3))
  possible_t = Matrix(np.random.uniform(-100, 100, 3))
  # possible_t = Matrix(np.ones(3))
  # rotation_matrix = Matrix(np.eye(3))
  return rotation_matrix, possible_t

def apply_transformation(points, rotation_matrix, translation):
  return (rotation_matrix*(points.T) + Matrix.hstack(*[translation] * points.shape[0])).T

def scramble_points(points, radius):
  #adds a nirly uniform distribution direction_vector*radius to each point.
  scramble_points = Matrix([points.row(i) + Matrix(create_nearly_random_direction_vector()*radius).T for i in range(points.rows)])
  return scramble_points

def create_nearly_random_direction_vector():
  random_vector = np.random.uniform(-1, 1, 3)
  return random_vector/np.linalg.norm(random_vector)

def create_lines(c_points, on_line_points):
  if c_points.shape != on_line_points.shape:
    raise ValueError("Points must have the same number of rows") #not sepose to happen so as error should happen, this error isnt delth with.
  return [[c_points.row(i), on_line_points.row(i) - c_points.row(i)] for i in range(c_points.rows)]

def evaluate_transformation(rotation, translation, source_points, target_lines):
  transformed_points = apply_transformation(source_points, rotation, translation)
  total_distance = sum((find_best_transformation.point_line_distance(transformed_points.row(i), target_lines[i]))**2 for i in range(transformed_points.rows))
  print("Total squard distance is: ", total_distance)
  print("Average squard distance is: ", total_distance/transformed_points.rows)
  print("Average distance is: ", sum((find_best_transformation.point_line_distance(transformed_points.row(i), target_lines[i])) for i in range(transformed_points.rows))/transformed_points.rows)

# Test the code:
#for a test:
#points are created
#lines are created using a transformation of the points and some rundom c points
#to check for minimization we scramble the points slitely we transformed to create lines before creating the lines. therefore we accurnt fo mistakes in the matching between the lines and points
#find transformation that minimizes the distance between the lines and the points
#check the accuracy of the transformation on the points and lines.

#input:
#all points and translations are defined within [-100,100] for simplicity, to change, change define_n_random_points and create_transformation.
#n is point count
#scramble_points input are points and radius of scramble.

if __name__ == '__main__':
  n = 100
  scramble_radius = 5
  source_points = define_n_random_points(n)#create points

  rotation, translation = create_transformation()#create translation
  target_points = apply_transformation(source_points, rotation, translation)#create target points
  scrambled_target_points = scramble_points(target_points, scramble_radius)#create scrambled points from target points, with a radius
  c_points = define_n_random_points(n)
  target_lines = create_lines(c_points, scrambled_target_points)#create lines from scrambled points
  best_R_found, best_t_found = find_best_transformation.find_best_transformation(source_points, target_lines) #find_best_transformation
  print("scramble_radius is ",scramble_radius)
  evaluate_transformation(best_R_found, best_t_found, source_points, target_lines)


# results
# We managed to find a good transformation.
# For no scramble, the transformation found is near perfect.
# Tested on n = 100, the code finished fast and found a good transformation with lower than the scramble radius average distance.
# Tested on n = 1000, for large n like 1000, the code takes longer but finds a good transformation.
# In short, the code does not find the best transformation but a close approximation to it.
