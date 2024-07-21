from collections import defaultdict

# User Input
# Schedule of rest and night periods where the number is the number day of a session
rest_night_periods = ['R1', 'N1O','N1E', 'R2', 'N2O', 'N2E', 'R3', 'N3O', 'N3E', 'R4', 'N4O', 'N4E', 'R5', 'N5O', 'N5E', 
                      'R6', 'N6O', 'N7O', 'N7E', 'R8', 'N8O', 'N8E', 'R9', 'N9O', 'N9E', 'R10', 'N10O', 'N10E',
                      'R11', 'N11O', 'N11E', 'R12', 'N12O', 'N13O', 'N13E', 'R14', 'N14O', 'N14E',
                      'R15', 'N15O', 'N15E', 'R16', 'N16O', 'N16E', 'R17', 'N17O', 'N17E', 'R18', 'N18O', 'N18E',
                      'R19', 'N19O', 'N19E', 'R20']

# List of days that counselors are not on duty
# Differentiate counselors that have the same off days by 1 or 2
counselors_off_days = {
    'Counselor A1': [3, 10],
    'Counselor B1': [5, 12],
    'Counselor B2': [5, 12],
    'Counselor C1': [7, 13],
    'Counselor C2': [7, 13],
    'Counselor C3': [7, 13],
    'Counselor C4': [7, 13]
}

# 7 counselors rotating through rest periods
rest_counselors = ['Counselor A1', 'Counselor B1', 'Counselor B2', 'Counselor C1', 'Counselor C2', 'Counselor C3', 'Counselor C4']

# 4 counselors for night shifts in cabin O
night_counselors_O = ['Counselor A1', 'Counselor B1', 'Counselor C1', 'Counselor C3']

# 3 counselors for night shifts in cabin E
night_counselors_E = ['Counselor B2', 'Counselor C2', 'Counselor C4']

# Function to check if a counselor can be assigned to a specific period
def can_assign(counselor, period, day, assignments):
    if day in counselors_off_days[counselor]:
        return False, f"{counselor} is off on day {day}"
    if period.startswith('N') and (day + 1) in counselors_off_days[counselor]:
        return False, f"{counselor} is off the day after (day {day + 1})"
    if f'R{day}' in assignments[counselor] or any(f'N{day}' in p for p in assignments[counselor]):
        return False, f"{counselor} is already assigned to a period on day {day}"
    # Check if the counselor is already assigned to a night shift the day before or the day after
    if period.startswith('N') and (f'N{day - 1}' in assignments[counselor] or f'N{day + 1}' in assignments[counselor]):
        return False, f"{counselor} is already assigned to a night shift the day before or the day after day {day}"
    # Check if the counselor is already assigned to a night shift on the same day but different cabin
    if period.startswith('N') and any(f'N{day}' in p for p in assignments[counselor]):
        return False, f"{counselor} is already assigned to a night shift on day {day}"
    # Check for back-to-back night shifts
    if period.startswith('N') and (f'N{day - 1}O' in assignments[counselor] or f'N{day - 1}E' in assignments[counselor] or f'N{day + 1}O' in assignments[counselor] or f'N{day + 1}E' in assignments[counselor]):
        return False, f"{counselor} is assigned to back-to-back night shifts on day {day}"
    return True, ""

# Backtracking function to assign counselors to periods
def assign_periods(periods, assignments, rest_counselors, night_counselors_O, night_counselors_E, rest_count, night_count_O, night_count_E, total_count, period_index=0):
    if period_index == len(periods):
        return True

    period = periods[period_index]
    day = int(''.join(filter(str.isdigit, period)))
    period_type = 'R' if period.startswith('R') else ('O' if period.endswith('O') else 'E')

    if period_type == 'R':
        counselors = rest_counselors
        count = rest_count
    elif period_type == 'O':
        counselors = night_counselors_O
        count = night_count_O
    else:
        counselors = night_counselors_E
        count = night_count_E

    for counselor in sorted(counselors, key=lambda c: (count[c], total_count[c])):
        can_assign_result, reason = can_assign(counselor, period, day, assignments)
        if can_assign_result:
            assignments[counselor].append(period)
            count[counselor] += 1
            total_count[counselor] += 1

            if assign_periods(periods, assignments, rest_counselors, night_counselors_O, night_counselors_E, rest_count, night_count_O, night_count_E, total_count, period_index + 1):
                return True

            assignments[counselor].remove(period)
            count[counselor] -= 1
            total_count[counselor] -= 1
        else:
            print(f"Cannot assign {counselor} to {period}: {reason}")

    return False

# Function to assign counselors to periods
def assign_counselors(rest_night_periods, counselors_off_days):
    assignments = defaultdict(list)
    rest_count = defaultdict(int)
    night_count_O = defaultdict(int)
    night_count_E = defaultdict(int)
    total_count = defaultdict(int)

    if not assign_periods(rest_night_periods, assignments, rest_counselors, night_counselors_O, night_counselors_E, rest_count, night_count_O, night_count_E, total_count):
        print("Failed to assign all periods to counselors")

    return dict(assignments), rest_count, night_count_O, night_count_E, total_count

# Assign counselors
assignments, rest_count, night_count_O, night_count_E, total_assignments = assign_counselors(rest_night_periods, counselors_off_days)

# Create a mapping from periods to counselors
period_to_counselor = {}
for counselor, periods in assignments.items():
    for period in periods:
        period_to_counselor[period] = counselor

# Sort the periods
sorted_periods = sorted(period_to_counselor.keys(), key=lambda x: (int(''.join(filter(str.isdigit, x))), '0' if x.startswith('R') else '1', x))

# Display the final schedule in the desired format
print("Final Schedule:")
for period in sorted_periods:
    print(f"{period}: {period_to_counselor[period]}")

# Display the count of rest and night shifts for each counselor
print("\nCounselor Assignments:")
for counselor in sorted(rest_count.keys()):
    print(f"{counselor}: {rest_count[counselor]} rests, {night_count_O[counselor]} nights in Cabin O, {night_count_E[counselor]} nights in Cabin E")

# Tests
for counselor, periods in assignments.items():
    for period in periods:
        day = int(''.join(filter(str.isdigit, period)))
        # Check that counselors are not assigned to off days
        if day in counselors_off_days[counselor]:
            print(f"{counselor} is assigned to off day {day}")
        # Check that counselors are not assigned on the night before a day off
        if period.startswith('N') and (day + 1) in counselors_off_days[counselor]:
            print(f"{counselor} is off the day after (day {day + 1})")
        # Check if the counselor is already assigned to both rest and night shifts on the same day
        if f'R{day}' in periods and f'N{day}' in periods:
            print(f"{counselor} is already assigned to both rest and night shifts on day {day}")
        # Check if the counselor is already assigned to a night shift the day before or the day after
        if (f'N{day - 1}' in assignments[counselor] and f'N{day}' in assignments[counselor]) or (f'N{day + 1}' in assignments[counselor] and f'N{day}' in assignments[counselor]):
            print(f"{counselor} is already assigned to a night shift the day before or the day after day {day}")
print("Schedule looks good!")
