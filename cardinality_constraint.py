import pprint

from pysat.formula import CNF


def cardinality_constraint(vars, k, counter, mode):
    if mode == "atmost":
        return cardinality_constraint_AMK(vars, k, counter)
    elif mode == "atleast":
        return cardinality_constraint_ALK(vars, k, counter)
    elif mode == "exact":
        cnf_amk, temp_amk = cardinality_constraint_AMK(vars, k, counter)
    else:
        raise ValueError("Invalid mode. Mode should be 'atmost', 'atleast', or 'exact'.")

def cardinality_constraint_ALK(vars, k, counter):
    cnf = CNF()
    N = len(vars)
    temp_var_table = [[0 for _i in range(k + 1)] for _j in range(N + 1)]
    # populate the temp_var_table
    for i in range(1, N + 1):
        for j in range(1, min(i, k) + 1):
            temp_var_table[i][j] = counter.next()
    
    for j in range(1, N + 1):
        cnf.append([-vars[j - 1], temp_var_table[j][1]])

    for j in range(2, N + 1):
        for s in range(1, min(j - 1, k) + 1):
            cnf.append([-temp_var_table[j - 1][s], temp_var_table[j][s]])

    for j in range(2, N + 1):
        for s in range(2, min(j, k) + 1):
            cnf.append([-vars[j - 1], -temp_var_table[j - 1][s - 1], temp_var_table[j][s]])

    for j in range(1, min(k, N) + 1):
        cnf.append([vars[j - 1], -temp_var_table[j][j]])

    for j in range(2, N + 1):
        for s in range(2, min(j, k) + 1):
            cnf.append([temp_var_table[j - 1][s - 1], -temp_var_table[j][s]])

    for j in range(2, N + 1):
        for s in range(1, min(j - 1, k) + 1):
            cnf.append([vars[j - 1], temp_var_table[j - 1][s], -temp_var_table[j][s]])

    cnf.append([temp_var_table[N][min(N, k)]])

    return (cnf, temp_var_table)

def cardinality_constraint_AMK(vars, k, counter):
    cnf = CNF()
    N = len(vars)
    temp_var_table = [[0 for _i in range(k + 1)] for _j in range(N + 1)]
    # populate the temp_var_table
    for i in range(1, N + 1):
        for j in range(1, min(i, k) + 1):
            temp_var_table[i][j] = counter.next()
    
    for j in range(1, N):
        cnf.append([-vars[j - 1], temp_var_table[j][1]])

    for j in range(2, N):
        for s in range(1, min(j - 1, k) + 1):
            cnf.append([-temp_var_table[j - 1][s], temp_var_table[j][s]])

    for j in range(2, N):
        for s in range(2, min(j, k) + 1):
            cnf.append([-vars[j - 1], -temp_var_table[j - 1][s - 1], temp_var_table[j][s]])

    for j in range(1, min(k, N) + 1):
        cnf.append([vars[j - 1], -temp_var_table[j][j]])

    for j in range(2, N):
        for s in range(2, min(j, k) + 1):
            cnf.append([temp_var_table[j - 1][s - 1], -temp_var_table[j][s]])

    for j in range(2, N):
        for s in range(1, min(j - 1, k) + 1):
            cnf.append([vars[j - 1], temp_var_table[j - 1][s], -temp_var_table[j][s]])
    
    for j in range(k + 1, N + 1):
        cnf.append([-vars[j - 1], -temp_var_table[j - 1][k]])

    return (cnf, temp_var_table)


def _test_cardinality_constraint():
    from pysat.solvers import Solver
    from util import Counter

    def count(model):
        return sum(1 for var in model if var > 0)

    def check_cardinality_constraint(var, k, mode):
        counter = Counter(start=len(var))
        cnf, _ = cardinality_constraint(var, k, counter, mode)
        with Solver() as solver:
            solver.append_formula(cnf)
            solver.solve()
            for model in solver.enum_models():
                model_count = count(model[: len(var)])
                if mode == "atleast":
                    assert model_count >= k
                elif mode == "atmost":
                    assert model_count <= k
                elif mode == "exact":
                    assert model_count == k

    var = [1, 2, 3, 4, 5]
    check_cardinality_constraint(var, 2, "atmost")
    check_cardinality_constraint(var, 4, "atleast")
    # check_cardinality_constraint(var, 1, "exact")


if __name__ == "__main__":
    _test_cardinality_constraint()
    print("All tests passed!")
