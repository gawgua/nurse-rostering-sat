from pysat.solvers import Solver
from pysat.formula import CNF

from cardinality_constraint import cardinality_constraint
from util import Counter
from ladder_encoding import ladder_constraint


class NurseRosteringSolver:
    def __init__(
        self,
        num_nurses,
        num_days,
        min_shift,
        min_shift_per,
        max_shift,
        max_shift_per,
        off_day,
        off_day_per,
        min_night_shift,
        min_night_shift_per,
        max_night_shift,
        max_night_shift_per,
        min_evening_shift,
        min_evening_shift_per,
        max_evening_shift,
        max_evening_shift_per,
        min_evening_night_shift,
        min_evening_night_shift_per,
        max_evening_night_shift,
        max_evening_night_shift_per,
    ):
        self.num_nurses = num_nurses
        self.num_days = num_days

        # constraints parameters
        self.min_shift = min_shift
        self.min_shift_per = min_shift_per
        self.max_shift = max_shift
        self.max_shift_per = max_shift_per
        self.off_day = off_day
        self.off_day_per = off_day_per
        self.min_night_shift = min_night_shift
        self.min_night_shift_per = min_night_shift_per
        self.max_night_shift = max_night_shift
        self.max_night_shift_per = max_night_shift_per
        self.min_evening_shift = min_evening_shift
        self.min_evening_shift_per = min_evening_shift_per
        self.max_evening_shift = max_evening_shift
        self.max_evening_shift_per = max_evening_shift_per
        self.min_evening_night_shift = min_evening_night_shift
        self.min_evening_night_shift_per = min_evening_night_shift_per
        self.max_evening_night_shift = max_evening_night_shift
        self.max_evening_night_shift_per = max_evening_night_shift_per

        self.schedule = [["O"] * num_days for _ in range(self.num_nurses)]
        self.counter = Counter(start=self.num_nurses * self.num_days * 4)  # i * j * 4
        self.cnf = self._build_cnf([1,2,3,4,5,6,7,8,9,10,11])
        self.solver = Solver(bootstrap_with=self.cnf, name="g3")

    def _get_nurse_day_var(self, nurse, day, shift):
        match shift:
            case "D":
                shift_idx = 0
            case "E":
                shift_idx = 1
            case "N":
                shift_idx = 2
            case "O":
                shift_idx = 3

        # mang 3 chieu nurse, day, shift
        return nurse * self.num_days * 4 + day * 4 + shift_idx + 1

    def _build_cnf(self, constraints):
        cnf = CNF()

        for nurse in range(self.num_nurses):
            if 1 in constraints:
                # constraint 1: each nurse can only work one shift per day or off (Exactly 1 state)
                for day in range(self.num_days):
                    shift_vars = [
                        self._get_nurse_day_var(nurse, day, shift)
                        for shift in ["D", "E", "N", "O"]
                    ]
                    cnf.append(shift_vars)  # at least one
                    for i, var_i in enumerate(shift_vars):
                        for var_j in shift_vars[i + 1 :]:
                            cnf.append([-var_i, -var_j])  # at most one

            if 2 in constraints:
                # constraint 2: at least k shift per n days (<= k-1 off days per n days)
                bool_vars = [
                    self._get_nurse_day_var(nurse, day, "O") for day in range(self.num_days)
                ]
                # cnf.extend(
                #     ladder_constraint(
                #         bool_vars, self.min_shift_per, self.min_shift, self.counter, mode="atleast"
                #     )
                # )
                for day in range(0, self.num_days - self.min_shift_per + 1):
                    cnf.extend(
                        cardinality_constraint(
                            bool_vars[day : day + self.min_shift_per],
                            self.min_shift_per - self.min_shift,
                            self.counter,
                            mode="atmost",
                        )[0]
                    )

            if 3 in constraints:
                # constraint 3: at least k off days per n days (<= n-k work days per n days)
                # => at most n-k shift per n days
                bool_vars = [
                    -self._get_nurse_day_var(nurse, day, "O") for day in range(self.num_days)
                ]
                cnf.extend(
                    ladder_constraint(
                        bool_vars, self.off_day_per, self.off_day_per - self.off_day, self.counter, mode="atmost"
                    )
                )
                # for day in range(0, self.num_days - self.off_day_per + 1):
                #     cnf.extend(
                #         cardinality_constraint(
                #             bool_vars[day : day + self.off_day_per],
                #             self.off_day_per - self.off_day,
                #             self.counter,
                #             mode="atmost",
                #         )[0]
                #     )

            if 4 in constraints:
                # constraint 4: at least k N shift per n days
                bool_vars = [
                    self._get_nurse_day_var(nurse, day, "N") for day in range(self.num_days)
                ]
                cnf.extend(
                    ladder_constraint(
                        bool_vars, self.min_night_shift_per, self.min_night_shift, self.counter, mode="atleast"
                    )
                )

            if 5 in constraints:
                # constraint 5: at most k N shift per n days
                bool_vars = [
                    self._get_nurse_day_var(nurse, day, "N") for day in range(self.num_days)
                ]
                cnf.extend(
                    ladder_constraint(
                        bool_vars, self.max_night_shift_per, self.max_night_shift, self.counter, mode="atmost"
                    )
                )

            if 6 in constraints:
                # constraint 6: at least k E shift per N days
                # => at most n-k non E shift per n days
                bool_vars = [
                    -self._get_nurse_day_var(nurse, day, "E") for day in range(self.num_days)
                ]
                cnf.extend(
                    ladder_constraint(
                        bool_vars, self.min_evening_shift_per, self.min_evening_shift_per - self.min_evening_shift, self.counter, mode="atmost"
                    )
                )
                # for day in range(0, self.num_days - self.min_evening_shift_per + 1):
                #     cnf.extend(
                #         cardinality_constraint(
                #             bool_vars[day : day + self.min_evening_shift_per],
                #             self.min_evening_shift_per - self.min_evening_shift,
                #             self.counter,
                #             mode="atmost",
                #         )[0]
                #     )


            if 7 in constraints:
                # constraint 7: at most k E shift per n days
                bool_vars = [
                    self._get_nurse_day_var(nurse, day, "E") for day in range(self.num_days)
                ]
                cnf.extend(
                    ladder_constraint(
                        bool_vars, self.max_night_shift_per, self.max_night_shift, self.counter, mode="atmost"
                    )
                )

            if 8 in constraints:
                # constraint 8: no E shift on consecutive days
                bool_vars = [
                    self._get_nurse_day_var(nurse, day, "E") for day in range(self.num_days)
                ]
                for day in range(self.num_days - 1):
                    cnf.append([-bool_vars[day], -bool_vars[day + 1]])

            if 9 in constraints:
                # constraint 9: at least k E or N shift per n days
                bool_vars_evening = [
                    self._get_nurse_day_var(nurse, day, "E") for day in range(self.num_days)
                ] 
                bool_vars_night = [
                    self._get_nurse_day_var(nurse, day, "N") for day in range(self.num_days)
                ]

                bool_vars = []
                for day in range(self.num_days):
                    bool_vars.append(bool_vars_evening[day])
                    bool_vars.append(bool_vars_night[day])

                cnf.extend(
                    ladder_constraint(
                        bool_vars, self.min_evening_night_shift_per, self.min_evening_night_shift, self.counter, mode="atleast"
                    )
                )

            if 10 in constraints:
                # constraint 10: at most k E or N shift per n days
                bool_vars_evening = [
                    self._get_nurse_day_var(nurse, day, "E") for day in range(self.num_days)
                ]
                bool_vars_night = [
                    self._get_nurse_day_var(nurse, day, "N") for day in range(self.num_days)
                ]

                # bool_vars = []
                # for day in range(self.num_days):
                #     bool_vars.append(bool_vars_evening[day])
                #     bool_vars.append(bool_vars_night[day])
                
                # cnf.extend(
                #     ladder_constraint(
                #         bool_vars, self.max_evening_night_shift_per, self.max_evening_night_shift, self.counter, mode="atmost"
                #     )
                # )
                for day in range(0, self.num_days - self.max_evening_night_shift_per + 1):
                    cnf.extend(
                        cardinality_constraint(
                            bool_vars_evening[day : day + self.max_evening_night_shift_per] + bool_vars_night[day : day + self.max_evening_night_shift_per],
                            self.max_evening_night_shift,
                            self.counter,
                            mode="atmost",
                        )[0]
                    )

            if 11 in constraints:
                # constraint 11: at most k shift per n days (>= n-k off days per n days)
                bool_vars = [
                    self._get_nurse_day_var(nurse, day, "O") for day in range(self.num_days)
                ]
                cnf.extend(
                    ladder_constraint(
                        bool_vars, self.max_shift_per, self.max_shift_per - self.max_shift, self.counter, mode="atleast"
                    )
                )

        # cnf

        return cnf

    def _test_constraints(self, model):
        # print(model[:10])
        # assert sum(1 for var in model[:10] if var > 0) <= 2
        for nurse in range(self.num_nurses):
            # constraint 1
            for day in range(self.num_days):
                shift_vars = [
                    self._get_nurse_day_var(nurse, day, shift)
                    for shift in ["D", "E", "N", "O"]
                ]
                assert sum(1 for var in shift_vars if var in model) == 1

            # constraint 2
            # get all work day (not O) variables for this nurse
            for day in range(0, self.num_days - self.min_shift_per + 1):
                work_days_cnt = 0
                for d in range(day, day + self.min_shift_per):
                    if (
                        self._get_nurse_day_var(nurse, d, "D") in model
                        or self._get_nurse_day_var(nurse, d, "E") in model
                        or self._get_nurse_day_var(nurse, d, "N") in model
                    ):
                        work_days_cnt += 1
                assert work_days_cnt >= self.min_shift, f"Nurse {nurse + 1}: Work day count from day {day} to {day + self.min_shift_per - 1} is {work_days_cnt}, expected at least {self.min_shift}"
                
            # constraint 3
            for day in range(0, self.num_days - self.off_day_per + 1):
                off_days_cnt = 0
                for d in range(day, day + self.off_day_per):
                    if self._get_nurse_day_var(nurse, d, "O") in model:
                        off_days_cnt += 1
                assert off_days_cnt >= self.off_day, f"Nurse {nurse + 1}: Off day count from day {day} to {day + self.off_day_per - 1} is {off_days_cnt}, expected at least {self.off_day}"

            # constraint 4
            for day in range(0, self.num_days - self.min_night_shift_per + 1):
                night_shift_cnt = 0
                for d in range(day, day + self.min_night_shift_per):
                    if self._get_nurse_day_var(nurse, d, "N") in model:
                        night_shift_cnt += 1
                assert night_shift_cnt >= self.min_night_shift, f"Nurse {nurse + 1}: Night shift count from day {day} to {day + self.min_night_shift_per - 1} is {night_shift_cnt}, expected at least {self.min_night_shift}"

            # constraint 5
            for day in range(0, self.num_days - self.max_night_shift_per + 1):
                night_shift_cnt = 0
                for d in range(day, day + self.max_night_shift_per):
                    if self._get_nurse_day_var(nurse, d, "N") in model:
                        night_shift_cnt += 1
                assert night_shift_cnt <= self.max_night_shift, f"Nurse {nurse + 1}: Night shift count from day {day} to {day + self.max_night_shift_per - 1} is {night_shift_cnt}, expected at most {self.max_night_shift}"

            # constraint 6
            for day in range(0, self.num_days - self.min_evening_shift_per + 1):
                evening_shift_cnt = 0
                for d in range(day, day + self.min_evening_shift_per):
                    if self._get_nurse_day_var(nurse, d, "E") in model:
                        evening_shift_cnt += 1
                assert evening_shift_cnt >= self.min_evening_shift, f"Nurse {nurse + 1}: Evening shift count from day {day} to {day + self.min_evening_shift_per - 1} is {evening_shift_cnt}, expected at least {self.min_evening_shift}"
            
            # constraint 7
            for day in range(0, self.num_days - self.max_evening_shift_per + 1):
                evening_shift_cnt = 0
                for d in range(day, day + self.max_evening_shift_per):
                    if self._get_nurse_day_var(nurse, d, "E") in model:
                        evening_shift_cnt += 1
                assert evening_shift_cnt <= self.max_evening_shift, f"Nurse {nurse + 1}: Evening shift count from day {day} to {day + self.max_evening_shift_per - 1} is {evening_shift_cnt}, expected at most {self.max_evening_shift}"

            # constraint 8
            for day in range(self.num_days - 1):
                assert not (
                    self._get_nurse_day_var(nurse, day, "E") in model
                    and self._get_nurse_day_var(nurse, day + 1, "E") in model
                ), f"Nurse {nurse + 1} has E shift on consecutive days {day} and {day + 1}"

            # constraint 9
            for day in range(0, self.num_days - self.min_evening_night_shift_per + 1):
                evening_night_shift_cnt = 0
                for d in range(day, day + self.min_evening_night_shift_per):
                    if (
                        self._get_nurse_day_var(nurse, d, "E") in model
                        or self._get_nurse_day_var(nurse, d, "N") in model
                    ):
                        evening_night_shift_cnt += 1
                assert evening_night_shift_cnt >= self.min_evening_night_shift, f"Nurse {nurse + 1}: Evening or Night shift count from day {day} to {day + self.min_evening_night_shift_per - 1} is {evening_night_shift_cnt}, expected at least {self.min_evening_night_shift}"
            
            # constraint 10
            for day in range(0, self.num_days - self.max_evening_night_shift_per + 1):
                evening_night_shift_cnt = 0
                for d in range(day, day + self.max_evening_night_shift_per):
                    if (
                        self._get_nurse_day_var(nurse, d, "E") in model
                        or self._get_nurse_day_var(nurse, d, "N") in model
                    ):
                        evening_night_shift_cnt += 1
                assert evening_night_shift_cnt <= self.max_evening_night_shift, f"Nurse {nurse + 1}: Evening or Night shift count from day {day} to {day + self.max_evening_night_shift_per - 1} is {evening_night_shift_cnt}, expected at most {self.max_evening_night_shift}"

            # constraint 11
            for day in range(0, self.num_days - self.max_shift_per + 1):
                work_days_cnt = 0
                for d in range(day, day + self.max_shift_per):
                    if (
                        self._get_nurse_day_var(nurse, d, "D") in model
                        or self._get_nurse_day_var(nurse, d, "E") in model
                        or self._get_nurse_day_var(nurse, d, "N") in model
                    ):
                        work_days_cnt += 1
                assert work_days_cnt <= self.max_shift, f"Nurse {nurse + 1}: Work day count from day {day} to {day + self.max_shift_per - 1} is {work_days_cnt}, expected at most {self.max_shift}"


    def solve(self):
        solved = False
        while self.solver.solve():
            solved = True
            model = self.solver.get_model()
            ban_clause = [-lit for lit in model[: self.num_nurses * self.num_days * 4]]
            self.solver.add_clause(ban_clause)
            for i in range(self.num_nurses):
                for j in range(self.num_days):
                    for shift in ["D", "E", "N", "O"]:
                        var = self._get_nurse_day_var(i, j, shift)
                        if var in model:
                            self.schedule[i][j] = shift
            self.print_schedule()
            self._test_constraints(model)
            
        if not solved:
            print("unsat")

    def print_schedule(self):
        weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        col_width = 3
        header = [weekdays[d % 7].ljust(col_width) for d in range(self.num_days)]
        print("Nurse  : " + " ".join(header).rstrip())
        for nurse in range(self.num_nurses):
            row = " ".join(
                (
                    self.schedule[nurse][day]
                    if self.schedule[nurse][day] != "O"
                    else " "
                ).ljust(col_width)
                for day in range(self.num_days)
            ).rstrip()
            print(f"Nurse {nurse + 1:2d}: {row}")
