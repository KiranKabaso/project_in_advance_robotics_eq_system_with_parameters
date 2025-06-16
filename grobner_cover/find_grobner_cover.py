import os
import json
import subprocess
import shutil
import psutil
from sage.all import *
from sympy import symbols, sympify, And, Not, simplify_logic, to_dnf,  Eq, Ne, Gt, Ge, Lt, Le
# from sympy.logic.boolalg import BooleanFunction

from typing import List


import resource
import time

def run_singular_code(code: str, timeout: int = None) -> tuple[str, int]:
  singular_path: str = shutil.which("Singular")
  if not singular_path:
    raise FileNotFoundError("Singular binary not found in PATH.")

  proc: subprocess.Popen = subprocess.Popen(
    [singular_path, "--no-rc", "-q"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
  )

  try:
    out, err = proc.communicate(input=code, timeout=timeout)
  except subprocess.TimeoutExpired:
    proc.kill()
    out, err = proc.communicate()
    print("❌ Timeout: Singular process killed.")

  return_code: int = proc.returncode

  if return_code != 0:
    print("❌ Singular returned error code:", return_code)

  if err.strip():
    print("❌ Singular stderr:\n", err.strip())

  if not out.strip():
    print("⚠️ Warning: Singular produced no output (stdout empty).")

  return out.strip()  # Returning 0 as placeholder for peak_memory


def count_leading_spaces(line: str) -> int:
    return len(line) - len(line.lstrip(' '))

def grobner_cover(equations, Nequations, Wequations, variables, parameters):
    ring_decl: str = f"(0,{','.join(parameters)}), ({','.join(variables)}), lp"

    # grobcov_lib_path: str = "/home/kiran/miniforge3/envs/sage/share/singular/LIB/grobcov.lib"
    ideal_exprs = ", ".join(str(eq._singular_()) for eq in equations) or "0"
    ideal_exprs_Nequations = ", ".join(str(eq._singular_()) for eq in Nequations) or "0"
    ideal_exprs_Wequations = ", ".join(str(eq._singular_()) for eq in Wequations) or "0"

    #Singular code
    singular_code = f"""
ring R = {ring_decl};  // Q[parameters][variables]
LIB "grobcov.lib";
ideal I = {ideal_exprs};
ideal N = {ideal_exprs_Nequations};
ideal W = {ideal_exprs_Wequations};
def G = grobcov(I, list("can", 1, "rep", 2));
G;
"""

    print("📤 Sending to Singular...\n" + singular_code)
    output = run_singular_code(singular_code)
    print("📦 Singular Output:\n" + output)
    print("end Singular Output")
    return output

def create_equations():
    """Define symbolic variables and equations for the Grobner Cover system."""
    x1, x2, x3, x4, lambda1, lambda2 = var('x1 x2 x3 x4 lambda1 lambda2')
    f11, f12, f21, f22 = var('f11 f12 f21 f22')
    g11, g12, g21, g22 = var('g11 g12 g21 g22')

    F = Matrix([[f11, f12], [0, 0]])
    G = Matrix([[f21, 0], [0, 0]])
    vec1 = vector([x1, x2])
    vec2 = vector([0, x4])

    M = (F + x3 * G) * vec1 + vec2
    f = M[0]**2 + M[1]**2

    phi1 = x1**2 + x2**2 - 1
    phi2 = x3**2 + x4**2 - 1
    L = f + lambda1 * phi1 + lambda2 * phi2

    # equations = [diff(L, v) for v in [x1, x2]]
    # equations = [diff(L, v) for v in [x1, x2, x3, x4, lambda1, lambda2]]
    equations = [diff(L, v) for v in [x1, x2, x3, x4, lambda1, lambda2]]
    print(equations)
    variables = ['x1', 'x2', 'x3', 'x4', 'lambda1', 'lambda2']
    parameters = ['f11', 'f12', 'f21']
    # parameters = ['f11', 'f12', 'f21']
    Nequations = []
    Wequations = []
    return equations, Nequations, Wequations, variables, parameters

def test_simple_grobcov():
    # a, b = var('a b')
    parameters = ['a', 'b']
    singular_code = """
ring R = (0,a,b), (x,y), lp;
LIB "grobcov.lib";
ideal I = x^2 + a*x + b, y*a+x - 1;
def G = grobcov(I, list("can", 1, "rep", 2));
G;
"""
    print("📤 Sending to Singular...\n")
    output = run_singular_code(singular_code)
    print("📦 Singular Raw Output:\n", output)
    print("end singular raw output")
    data = parse_output_to_json(output, parameters)
    print("data:", data)
    with open("simple_test_grobner_cover_base_condition_partition.json", "w") as f:
        json.dump(data, f, indent=4)


def parse_output_to_json(output, parameters):
    lines = [line.rstrip() for line in output.splitlines() if line.strip()]
    lines_partition_to_segments = getLinesDevidedToSegments(lines)
    segments = []
    for partition in lines_partition_to_segments:
        i = 0
        while count_leading_spaces(partition[i]) != 3 or partition[i].strip() != '[2]:':
            i = i+1
        basis = []
        while count_leading_spaces(partition[i]) != 3 or partition[i].strip() != '[3]:':
            if '=' in partition[i].strip():
                _, expr = partition[i].strip().split('=', 1)
                expr = expr.strip()
                basis.append(expr)
            i = i + 1
        while count_leading_spaces(partition[i]) != 3 or partition[i].strip() != '[4]:':
            print(partition[i])
            i = i+1
        E_conditions = []
        N_conditions = []
        while partition[i].strip() != '[2]:':
            if '=' in partition[i].strip():
                _, expr = partition[i].strip().split('=', 1)
                expr = expr.strip()
                if expr not in ['0']:
                    E_conditions.append(expr + '== 0')
            i = i + 1
        for j in range(i, len(partition)):
            if '=' in partition[j].strip():
                _, expr = partition[j].strip().split('=', 1)
                expr = expr.strip()
                if expr not in ['0']:
                    N_conditions.append(expr + '== 0')

        conditions = getConditions(E_conditions, N_conditions, parameters)
        if conditions != "False":
            segments.append({"basis" : basis, "conditions" : conditions})
    return segments

def getConditions(E_conditions, N_conditions, parameters):


    symbolic_parameters = symbols(' '.join(parameters))
    symbol_dict = dict(zip(parameters, symbolic_parameters))

    symbolic_E_conditions = [sympify(E_condition, locals=symbol_dict, evaluate=False) for E_condition in E_conditions]
    symbolic_N_conditions = [sympify(N_condition, locals=symbol_dict, evaluate=False) for N_condition in N_conditions]


    E_condition = And(*symbolic_E_conditions)
    N_condition = And(*symbolic_N_conditions)

    if not N_conditions: #it sepose to be E\N so if N is empty the result is E
        # return str(format_condition(E_condition))
        return str((E_condition))


    condition = to_dnf(And(E_condition, Not(N_condition)), simplify=True)
    # return str(format_condition(condition))
    return str((condition))

#not useful for not triviL cases that require solving of the parametric conditions.
# def format_condition(expr):
#     # if isinstance(expr, BooleanFunction):
#     if expr.func == And:
#         return ' and '.join(format_condition(arg) for arg in expr.args)
#     elif expr.func == Not:
#         return f'not ({format_condition(expr.args[0])})'
#     elif expr.func in (Eq, Ne, Gt, Ge, Lt, Le):
#         op_map = {
#             Eq: '==',
#             Ne: '!=',
#             Gt: '>',
#             Ge: '>=',
#             Lt: '<',
#             Le: '<=',
#         }
#         lhs = str(expr.lhs)
#         rhs = str(expr.rhs)
#         op = op_map.get(expr.func, '?')
#         return f'{lhs} {op} {rhs}'
#     return str(expr)

def getLinesDevidedToSegments(lines):
    segments_start_indexes = []
    for index, line in enumerate(lines):
        leading_spaces = count_leading_spaces(line)
        if leading_spaces <= 1:
            segments_start_indexes.append(index)

    #now segments_start_indexes contains idx of the starting line of all segments
    return partition_by_indexes(lines, segments_start_indexes)

def partition_by_indexes(arr, indexes):
    indexes = sorted(indexes)
    partitions = []

    for i in range(len(indexes)):
        start = indexes[i]
        end = indexes[i + 1] if i + 1 < len(indexes) else len(arr)
        partitions.append(arr[start:end])

    return partitions



def main():
    equations, Nequations, Wequations, variables, parameters = create_equations()
    output = grobner_cover(equations, Nequations, Wequations, variables, parameters)
    with open("grobcov_raw_output.txt", "w") as f:
        f.write(output)

    data = parse_output_to_json(output, parameters)
    print("data:", data)
    print("got data")
    with open("grobner_cover_base_condition_partition.json", "w") as f:
        json.dump(data, f, indent=4)

    print("✅ Result saved to grobner_cover_base_condition_partition.json")
if __name__ == "__main__":
    main()
    # test_simple_grobcov()
