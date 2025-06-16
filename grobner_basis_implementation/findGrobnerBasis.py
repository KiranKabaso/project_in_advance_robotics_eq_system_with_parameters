from sympy import symbols, Eq, Matrix, expand, diff, Add, simplify, cancel, Poly, QQ
import copy




def findGroebnerBasis(pols, variables, lexOrder):
  polynomials_as_lists = extract_lists(pols)
  polynomials_as_lists = [order_pol(poly, variables, lexOrder) for poly in polynomials_as_lists]
  polynomials_as_lists = order_pols(polynomials_as_lists, variables, lexOrder)
  processed_pairs = set()
  groebnerBasis = polynomials_as_lists
  while True:
    lastGroebnerBasis = groebnerBasis[:]
    pairs = get_all_non_identical_pairs(lastGroebnerBasis, variables, lexOrder) #returns pairs where pair[0] is different from pair[1]
    for pair in pairs:
      pair_tuple = tuple(sorted([str(pair[0]), str(pair[1])]))
      if pair_tuple in processed_pairs:
        continue

      s_poly_as_list = calculate_s(pair[0], pair[1], variables, lexOrder)
      r = calculate_remainder(s_poly_as_list, groebnerBasis, variables, lexOrder) #putting here groebnerBasis instead of lastGroebnerBasis i more efficient.
      if (not is_zero_equation(r, variables, lexOrder)):
        print(1)
        groebnerBasis.append(r)
        groebnerBasis = order_pols(groebnerBasis, variables, lexOrder)
      else:
        processed_pairs.add(pair_tuple)
    if (is_same_basis(lastGroebnerBasis, groebnerBasis, variables, lexOrder)):
      return groebnerBasis


def extract_lists(polynomials):
  for i in range(len(polynomials)):
    if isinstance(polynomials[i], Eq):
      polynomials[i] = expand(polynomials[i]) #changes the inputted list to, but sense it only expands the equations inside, it doesn't matter.
      polynomials[i] = list(polynomials[i].lhs.as_ordered_terms())
  return polynomials

def is_same_basis(pols_list_1, pols_list_2, variables, lexOrder):
  if len(pols_list_1) != len(pols_list_2):
    return False


  for i in range(len(pols_list_1)):
    if not are_lists_equal(pols_list_1[i], pols_list_2[i]):
      return False
  return True

def calculate_remainder(s_poly_as_ordered_list, groebnerBasis, variables, lexOrder):
  r = []
  while not is_zero_equation(s_poly_as_ordered_list, variables, lexOrder):
    is_divided = False
    for basis_element in groebnerBasis:

      if can_be_divided_by(s_poly_as_ordered_list[0], basis_element[0], variables, lexOrder): #a devision is posible
        term_difference = (find_term_difference(s_poly_as_ordered_list[0], basis_element[0])) #returns expression
        multiplied_basis_element = [term_difference*element for element in basis_element]
        s_poly_as_ordered_list = subtract(s_poly_as_ordered_list, multiplied_basis_element, variables, lexOrder)
        is_divided = True
        break #exits the for loop


    if (not is_divided):
      r.append(s_poly_as_ordered_list[0])
      s_poly_as_ordered_list.pop(0)

  # remainder = Poly(sum(s_poly_as_ordered_list), *variables,domain=QQ)
  # new_basis = [Poly(sum(poly), *variables,domain=QQ) for poly in groebnerBasis]
  # for divisor in new_basis:
  #   remainder = remainder.rem(divisor)
  # remainder_as_list = list(remainder.as_expr().args)

  print("1 : ", r)
  r = order_pol(r, variables, lexOrder) #ne need we always append the stronger terms first.
  print("2 : ", r)
  return r

def subtract(pol1_as_list, pol2_as_list, variables, lexOrder):
  combined_list = order_two_pols(pol1_as_list, [-1*element for element in pol2_as_list], variables, lexOrder)
  return combined_list



def can_be_divided_by(term1, term2, variables, lexOrder):
  if is_zero_equation([term2], variables, lexOrder):
    return False

  term1_LM = get_LM_from_LT(term1, variables, lexOrder)
  term2_LM = get_LM_from_LT(term2, variables, lexOrder)

  for var in lexOrder:
    if var not in variables:
      continue

    var_power_in_1 = term1_LM.as_coeff_exponent(var)[1] if var in term1_LM.free_symbols else 0
    var_power_in_2 = term2_LM.as_coeff_exponent(var)[1] if var in term2_LM.free_symbols else 0
    if var_power_in_1 < var_power_in_2:
      return False
  return True


def find_term_difference(term1, term2):
    return term1 / term2





def is_zero_equation(eq_as_list, variables, lexOrder):
  #should handel [] case and [0], simplefied to [0] case is unended as we reorder in some function before calling this function

  # Case 1: Empty list means it's already zero (no terms)
    if not eq_as_list:
      return True

    # Case 2: If there's only one term and it's 0, it's a zero equation
    if len(eq_as_list) == 1 and eq_as_list[0] == 0:
      return True

    # Case 3: Check if all terms are zero after simplification
    # simplified_eq = [simplify(cancel(term)) for term in eq_as_list]  # Simplify each term
    for term in eq_as_list:
      #notice: !!!!!!!! this case is dependent on the parameters, if the parameters reduce it to zero for sertain numbers we could get a simpler basis
      if term != 0:
        return False  # If any term is not zero after simplification, it's not a zero equation

    return True  # If all terms are zero after simplification, return True


def calculate_s(eq1_as_list, eq2_as_list, variables, lexOrder):
  eq1_as_list_LM = get_LM_from_LT(eq1_as_list[0], variables, lexOrder)
  eq2_as_list_LM = get_LM_from_LT(eq2_as_list[0], variables, lexOrder)
  LCM = get_LCM(eq1_as_list_LM, eq2_as_list_LM, variables, lexOrder)
  eq1_as_list_copy = copy.deepcopy(eq1_as_list)
  eq2_as_list_copy = copy.deepcopy(eq2_as_list)

  for i, element in enumerate(eq1_as_list_copy):
    eq1_as_list_copy[i] = element * LCM / eq1_as_list[0]

  for i, element in enumerate(eq2_as_list_copy):
    eq2_as_list_copy[i] = -1 * element * LCM / eq2_as_list[0]

  ordered_s = order_two_pols(eq1_as_list_copy, eq2_as_list_copy, variables, lexOrder)
  return ordered_s #returns s_poly as ordered list according to lexOrder


def get_LM_from_LT(LT, variables, lexOrder):
  LM = 1
  for var in lexOrder:
    if var not in variables:
      continue

    var_power = LT.as_coeff_exponent(var)[1] if var in LT.free_symbols else 0
    LM *= var**var_power
  return LM

def get_LCM(LM1, LM2, variables, lexOrder):
  LCM = 1
  for var in lexOrder:
    if var not in variables:
      continue

    LM1_var_power = LM1.as_coeff_exponent(var)[1] if var in LM1.free_symbols else 0
    LM2_var_power = LM2.as_coeff_exponent(var)[1] if var in LM2.free_symbols else 0
    LCM *= var**max(LM1_var_power, LM2_var_power)
  return LCM



def get_all_non_identical_pairs(equations, variables, lexOrder):
  non_identical_pairs = []
  for i in range(len(equations)-1, -1, -1):
    for j in range(i -1, -1,-1):
      eq_a, eq_b = equations[i], equations[j]

      # Ensure no equation appears twice in a pair
      if ((not are_lists_equal(eq_a, eq_b)) and (not is_zero_equation(eq_a, variables, lexOrder)) and (not is_zero_equation(eq_b, variables, lexOrder))):
        non_identical_pairs.append((eq_a, eq_b))
  return non_identical_pairs


def sort_pairs(pairs, variables, lexOrder):
  for i in range(len(pairs)):
    for j in range(len(pairs)):
      if i != j:
        mon_1_1 = get_LM_from_LT(pairs[i][0][0], variables, lexOrder)
        mon_1_2 = get_LM_from_LT(pairs[i][1][0], variables, lexOrder)
        max_pair_1 = mon_1_1 if is_stronger(mon_1_1, mon_1_2, lexOrder, variables) else mon_1_2
        mon_2_1 = get_LM_from_LT(pairs[j][0][0], variables, lexOrder)
        mon_2_2 = get_LM_from_LT(pairs[j][1][0], variables, lexOrder)
        max_pair_2 = mon_2_1 if is_stronger(mon_2_1, mon_2_2, lexOrder, variables) else mon_2_2
        if not is_stronger(max_pair_1, max_pair_2, lexOrder, variables):
          pairs[i], pairs[j] = pairs[j], pairs[i]  # Swap the pairs
  return pairs
def are_lists_equal(eq_a, eq_b):
    if len(eq_a) != len(eq_b):
        return False  # Lists have different lengths, they can't be equal

    for i in range(len(eq_a)):  # Compare corresponding elements
      if eq_a[i] != eq_b[i]:  # Check if elements are not equal
        return False

    return True  # All elements are equal



def order_two_pols(eq_a, eq_b, variables, lexOrder):
  ordered_pol = merge(eq_a, eq_b, is_stronger, lexOrder, variables)
  return combine_components(ordered_pol, variables, lexOrder)

def order_pols(pols, variables, lexOrder):
  pols_copy = copy.deepcopy(pols)

  #now we want to order the pols in lexOrder and we know the LT is first in each polynomial, so we want to compare the first term. notice is_stronger would have worked fine for comparing between two polynomials to. And merge sort simply divides the inputted list so we can call merge_sort to order the list of polynomials to.
  ordered_pols = merge_sort(pols_copy, is_stronger, lexOrder, variables)
  return ordered_pols

def order_pol(eq_as_list, variables, lexOrder):
  ordered_pol = merge_sort(eq_as_list, is_stronger, lexOrder, variables)
  return combine_components(ordered_pol, variables, lexOrder) #combine expressions that have the same variables but have different parameters


def combine_components(ordered_pol_as_list, variables, lexOrder): #combine expressions that have the same variables but have different parameters
  combined_pol = []
  last_exression_LM = None
  for expression in ordered_pol_as_list:
    if (get_LM_from_LT(expression, variables, lexOrder) != last_exression_LM):
      combined_pol.append(expression)
      last_exression_LM = get_LM_from_LT(expression, variables, lexOrder)
    else:
      combined_pol[-1] = (combined_pol[-1]/last_exression_LM + expression/last_exression_LM)*last_exression_LM

  combined_pol = [(simplify(cancel(term))) for term in combined_pol]
  combined_pol = [pol for pol in combined_pol if pol != 0]
  return combined_pol


def merge_sort(terms, is_stronger, lexOrder, variables):
    """ Sorts terms using merge sort based on the `is_stronger()` function. """
    if len(terms) <= 1:
        return terms

    mid = len(terms) // 2
    left_half = merge_sort(terms[:mid], is_stronger, lexOrder, variables)
    right_half = merge_sort(terms[mid:], is_stronger, lexOrder, variables)

    return merge(left_half, right_half, is_stronger, lexOrder, variables)

def merge(left, right, is_stronger, lexOrder, variables):
    """ Merges two sorted lists using `is_stronger()` for comparison. """
    sorted_terms = []
    i = j = 0

    while i < len(left) and j < len(right):
        if is_stronger(left[i], right[j], lexOrder, variables):
            sorted_terms.append(left[i])
            i += 1
        else:
            sorted_terms.append(right[j])
            j += 1

    sorted_terms.extend(left[i:])  # Append remaining left-side elements
    sorted_terms.extend(right[j:])  # Append remaining right-side elements

    return sorted_terms


def is_stronger(term1, term2, lexOrder, variables):
  leading_t1 = term1[0] if isinstance(term1, list) else term1

  leading_t2 = term2[0] if isinstance(term2, list) else term2

  for var in lexOrder:
    if var not in variables:
      continue #if from some reason the parameters are before the variable in lexOrder


    # Get exponent of var in both terms
    power1 = leading_t1.as_coeff_exponent(var)[1] if var in leading_t1.free_symbols else 0
    power2 = leading_t2.as_coeff_exponent(var)[1] if var in leading_t2.free_symbols else 0

    if (power1 > power2):
      return True
    elif (power1 < power2):
      return False

  return False #terms are lexOrder equal.

def is_groebner_basis(groebnerBasis, variables, lexOrder):
    """
    Checks if a given basis is a valid Gröbner Basis by ensuring that
    every S-polynomial reduces to zero.
    """
    for i in range(len(groebnerBasis)):
        for j in range(i + 1, len(groebnerBasis)):
            s_poly = calculate_s(groebnerBasis[i], groebnerBasis[j], variables, lexOrder)
            remainder = calculate_remainder(s_poly, groebnerBasis, variables, lexOrder)
            if not is_zero_equation(remainder, variables, lexOrder):
                return False  # Not a Gröbner Basis if any remainder ≠ 0
    return True  # Valid Gröbner Basis

def test1():
  x, y, z = symbols("x y z")

  # Define lexicographic order
  lexOrder = [y, x, z]
  variables = [x, y]

  # Example equations with more terms and complexity
  polynomials = [
      Eq(x**2+y**2-1, 0),  # Equation with higher degree
      Eq(x**2+y, 0),  # More terms and higher powers
  ]

  # Run the function to order the polynomials
  grob_basis = findGroebnerBasis(polynomials, variables, lexOrder)
  if (is_groebner_basis(grob_basis, variables, lexOrder)):
    print("The given polynomials form a Gröbner Basis.")

  # Print results
  print("\nOriginal Polynomials:\n")
  for eq in polynomials:
      print(eq)

  print("grob_basis:")
  for eq in grob_basis:
      print(eq)

def test_groebner_basis():
    # Define variables and parameters
    x, y, z = symbols("x y z")  # 'a' is a parameter, not a variable

    # Define lexicographic order
    lexOrder = [x, y, z]  # Lexicographic order prioritizing 'y' over 'x'
    variables = [x, y, z]  # Only 'x' and 'y' are considered variables

    # Polynomial equations with a parameter 'a'
    polynomials = [
    Eq(x**3 + y**2 - z**2 + x*y, 0),   # Cubic in 'x', quadratic in 'y' and 'z'
    Eq(y**3 - x*z + y*z**2 - x*y, 0),  # Cubic in 'y', mixed terms
    Eq(z**4 - x**2*y + y*z - x*y*z, 0), # Quartic in 'z', mixed interactions
    Eq(x*y*z - x**2 + y**2 - z**2, 0)  # Fully mixed with quadratic and linear terms
    ]

    # Compute the Gröbner basis
    groebner_basis = findGroebnerBasis(polynomials, variables, lexOrder)

    # Print results
    print("\nOriginal Polynomials:")
    for eq in polynomials:
        print(eq)

    print("\nComputed Gröbner Basis:")
    for eq in groebner_basis:
        print(eq)

    # Additional checks (optional):
    assert all(isinstance(eq, list) for eq in groebner_basis), "Basis elements should be lists of terms."
    assert is_same_basis(groebner_basis, order_pols(groebner_basis, variables, lexOrder), variables, lexOrder), "Gröbner basis should be sorted correctly."

    if is_groebner_basis(groebner_basis, variables, lexOrder):
      print("\nTest passed!")
    else:
      print("\nTest failed!")

if __name__ == "__main__":
  test1()
  # test_groebner_basis()

