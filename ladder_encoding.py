from pysat.formula import CNF
from cardinality_constraint import cardinality_constraint


def join_blocks_AMK(blocks, n, k):
    cnf = CNF()
    for i in range(0, len(blocks) - 1, 2):
        block_a = blocks[i]
        block_b = blocks[i + 1]

        # (8) of section 3.3
        for j in range(
            2, min(n, len(block_b)) + 1
        ):  # if block_b has less than n variables, run to n will Out of index
            for p in range(1, k + 1):
                if p >= len(block_b):
                    break
                if block_a[n - j + 1][k - p + 1] and block_b[j - 1][p]:
                    cnf.append([-block_a[n - j + 1][k - p + 1], -block_b[j - 1][p]])
    return cnf


def join_blocks_ALK(blocks, n, k):
    cnf = CNF()
    for i in range(0, len(blocks) - 1, 2):
        block_a = blocks[i]
        block_b = blocks[i + 1]

        # (8) of section 3.3
        for m in range(
            1, min(n, len(block_b)) + 1
        ):  # if block_b has less than n variables, run to n will Out of index
            for i in range(1, k + 1):
                if block_a[m][i] and block_b[min(len(block_b), n) - m][k - i + 1]:
                    cnf.append(
                        [block_a[m][i], block_b[min(len(block_b), n) - m][k - i + 1]]
                    )
    return cnf


def ladder_constraint(bool_vars, block_size, k, counter, mode):
    cnf = CNF()
    n = len(bool_vars)
    blocks_temp_vars = []

    for i in range(0, n, block_size):
        if i == 0:
            block = bool_vars[i : i + block_size][::-1]
            constraint, temp_vars = cardinality_constraint(block, k, counter, mode)
            cnf.extend(constraint)
            blocks_temp_vars.append(temp_vars)
        elif i + block_size >= n:
            block = bool_vars[i:n]
            constraint, temp_vars = cardinality_constraint(
                block, k, counter, mode
            )
            cnf.extend(constraint)
            blocks_temp_vars.append(temp_vars)
        else:
            block = bool_vars[i : i + block_size]
            constraint, temp_vars = cardinality_constraint(block, k, counter, mode)
            cnf.extend(constraint)
            blocks_temp_vars.append(temp_vars)

            block = bool_vars[i : i + block_size][::-1]
            constraint, temp_vars = cardinality_constraint(block, k, counter, mode)
            cnf.extend(constraint)
            blocks_temp_vars.append(temp_vars)

    if mode in ("atmost", "exact"):
        cnf.extend(join_blocks_AMK(blocks_temp_vars, block_size, k))
    if mode in ("atleast", "exact"):
        cnf.extend(join_blocks_ALK(blocks_temp_vars, block_size, k))

    return cnf


def _test_ladder_constraint():
    from pysat.solvers import Solver
    from util import Counter

    def count(model):
        return sum(1 for var in model if var > 0)

    def check_ladder_constraint(var, block_size, k, mode):
        tested_case = 0

        counter = Counter(len(var))
        cnf = ladder_constraint(var, block_size, k, counter, mode)
        with Solver() as solver:
            solver.append_formula(cnf)
            solver.solve()
            for model in solver.enum_models():
                for i in range(0, len(var) - block_size):
                    cnt = count(model[i : i + block_size])
                    if mode == "atmost":
                        assert cnt <= k, f"{cnt} {model[i : i + block_size]}"
                    if mode == "atleast":
                        assert cnt >= k, f"{cnt} {model[i : i + block_size]}"

                tested_case += 1
                if tested_case >= 10000:
                    break

    var = [i for i in range(1, 11)]
    # check_ladder_constraint(var, 6, 4, "atmost")
    check_ladder_constraint(var, 4, 2, "atmost")
    # check_ladder_constraint(var, 4, 2, "exact")


if __name__ == "__main__":
    _test_ladder_constraint()
    print("Ladder constraint test passed!")
