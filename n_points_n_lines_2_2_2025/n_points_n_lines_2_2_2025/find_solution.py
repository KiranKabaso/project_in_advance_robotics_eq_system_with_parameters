from sympy import symbols, Matrix
import numpy as np

from wolframclient.evaluation import WolframLanguageSession
from wolframclient.language import wl
from sympy.printing.mathematica import mathematica_code

def find_solution(equation_to_minimize, equations, variables):
  session = None
  try:
    error_mma = mathematica_code(equation_to_minimize)
    constraints_mma = " && ".join([mathematica_code(constraint) for constraint in equations])
    variables_mma = "{" + ",".join([mathematica_code(var) for var in variables]) + "}"
    session = WolframLanguageSession()
    optimize_command = f"NMinimize[{{{error_mma}, {constraints_mma}}}, {variables_mma}]"

    print("Evaluating optimization solution...")
    solution_raw = session.evaluate(wl.ToExpression(optimize_command))

    #convert solution to dictionary
    _, variable_values = solution_raw
    solution_dict = {str(var): val for var, val in variable_values}
    return solution_dict

  except Exception as e:
    print("Error during optimization:", e)
    return None

  finally:
    if session:
      session.terminate()