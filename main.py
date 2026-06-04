# """
# VD: Nurse Rostering	            14 ngay y tá nghỉ At Least 4
# 								7 ngày y tá trực At Most 5
# 								1 ngày exact 2 y tá trực
# """

from solve import NurseRosteringSolver

if __name__ == "__main__":
    NUM_NURSES = 5
    NUM_DAYS = 31

    MIN_SHIFT = 20
    MIN_SHIFT_PER = 28
    MAX_SHIFT = 6
    MAX_SHIFT_PER = 7
    OFF_DAY = 4
    OFF_DAY_PER = 14
    MIN_NIGHT_SHIFT = 1
    MIN_NIGHT_SHIFT_PER = 14
    MAX_NIGHT_SHIFT = 4
    MAX_NIGHT_SHIFT_PER = 14
    MIN_EVENING_SHIFT = 4
    MIN_EVENING_SHIFT_PER = 14
    MAX_EVENING_SHIFT = 8
    MAX_EVENING_SHIFT_PER = 14
    MIN_EVENING_NIGHT_SHIFT = 2
    MIN_EVENING_NIGHT_SHIFT_PER = 7
    MAX_EVENING_NIGHT_SHIFT = 4
    MAX_EVENING_NIGHT_SHIFT_PER = 7
    solver = NurseRosteringSolver(
        NUM_NURSES,
        NUM_DAYS,
        MIN_SHIFT,
        MIN_SHIFT_PER,
        MAX_SHIFT,
        MAX_SHIFT_PER,
        OFF_DAY,
        OFF_DAY_PER,
        MIN_NIGHT_SHIFT,
        MIN_NIGHT_SHIFT_PER,
        MAX_NIGHT_SHIFT,
        MAX_NIGHT_SHIFT_PER,
        MIN_EVENING_SHIFT,
        MIN_EVENING_SHIFT_PER,
        MAX_EVENING_SHIFT,
        MAX_EVENING_SHIFT_PER,
        MIN_EVENING_NIGHT_SHIFT,
        MIN_EVENING_NIGHT_SHIFT_PER,
        MAX_EVENING_NIGHT_SHIFT,
        MAX_EVENING_NIGHT_SHIFT_PER,
    )
    solver.solve()
