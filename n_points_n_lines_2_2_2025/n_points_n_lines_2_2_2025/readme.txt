Problem Description:
Given n points and n lines, where each point has a matching line, find a rigid transformation on the n points that minimizes the distance between each point and its matching line.

What the Code Does:
The code finds a close approximation to the optimal rigid transformation and tests the accuracy of the found transformation.

Main Method:
The main idea is to create equations that define the problem and then send the mathematical problem to Wolfram Mathematica to find the solution.

Algorithm (Simplified):
Create points and lines.
Create an equation system.
Solve the equation system.
Return the transformation (the result of the equation system: R and t).
Evaluate the transformation.

Algorithm (Detailed):
-Create n random points and a random transformation.

Use the transformation to define the lines. This way, we know how good the transformation found was supposed to be.
The lines are created by transforming the original points and then shifting the transformed points by a radius, using n more random points.
This ensures that a transformation exists, guaranteeing that each point is at worst a distance radius from its line.
We should expect to find a transformation that is similarly good.

Now that we have the lines and points, find a transformation that minimizes the distance:
Define equations:
R: Rotation matrix
t: Translation vector
The sum of squared distances of the points after applying the transformation (R and t) to the lines.

Send a request to Wolfram Mathematica to find the global minimum of the sum, under the constraints of R and t.
Retrieve the result.
Evaluate the result.

Functions
Scripts and their functions:

main_function_culler.py:
define_n_random_points(n)
create_transformation()
apply_transformation(points, rotation_matrix, translation)
scramble_points(points, radius)
create_nearly_random_direction_vector()
create_lines(c_points, on_line_points)
evaluate_transformation(rotation, translation, source_points, target_lines)

find_best_transformation.py:
find_best_transformation(source_points, target_lines)
point_line_distance(point, line)

find_solution.py:
find_solution(equation_to_minimize, equations, variables)
Additional Information
More details about the functions and the algorithm are available in the code.

results:
We managed to find a good transformation.
For no scramble, the transformation found is near perfect.
Tested on n = 100, the code finished fast and found a good transformation with lower than the scramble radius average distance.
Tested on n = 1000, for large n like 1000, the code takes longer but finds a good transformation.
In short, the code does not find the best transformation but a close approximation to it.

README_END