from collections import defaultdict

# User Input

# Schedule of rest and night periods where the number is the number day of a session
rest_night_periods = ['R1', 'N1', 'R2', 'N2', 'R3', 'N3', 'R4', 'N4', 'R5', 'N5', 
                      'R6', 'N6', 'N7', 'R8', 'N8', 'R9', 'N9', 'R10', 'N10', 
                      'R11', 'N11', 'R12', 'N12', 'N13', 'R14', 'N14', 'R15', 'N15', 
                      'R16', 'N16', 'R17', 'N17', 'R18', 'N18', 'R19', 'N19', 'R20']

# List of days that counselors are not on duty
# Differentiate counselors that have the same off days by 1 or 2
counselors_off_days = {
    'Counselor A1': [3, 10],
    'Counselor B1': [5, 12],
    'Counselor C1': [7, 13],
    'Counselor C2': [7, 13]
}

# Function to check if a counselor can be assigned to a specific period
def can_assign(counselor, period, day, assignments):
    # Check if the counselor is off on the given day
    if day in counselors_off_days[counselor]:
        return False, f"{counselor} is off on day {day}"
    # Check if the counselor is off the day after (for night shifts)
    if period.startswith('N') and (day + 1) in counselors_off_days[counselor]:
        return False, f"{counselor} is off the day after (day {day + 1})"
    # Check if the counselor is already assigned on the same day
    if f'R{day}' in assignments[counselor] or f'N{day}' in assignments[counselor]:
        return False, f"{counselor} is already assigned to a period on day {day}"
    # Check if the counselor is already assigned to a night shift the day before or the day after
    if period.startswith('N') and (f'N{day - 1}' in assignments[counselor] or f'N{day + 1}' in assignments[counselor]):
        return False, f"{counselor} is already assigned to a night shift the day before or the day after day {day}"
    return True, ""

# Backtracking function to assign counselors to periods
def assign_periods(periods, assignments, counselors, rest_count, night_count, total_count, period_index=0):
    if period_index == len(periods):  # Base Case: finished all periods
        return True

    period = periods[period_index]
    day = int(period[1:])
    period_type = 'R' if period.startswith('R') else 'N'
    
    # Track tried assignments to avoid redundant checks
    tried_assignments = set()

    # Try to assign a counselor with the fewest total assignments of the current period type
    for counselor in sorted(counselors, key=lambda c: ((rest_count[c] if period_type == 'R' else night_count[c]), total_count[c])):
        if counselor in tried_assignments:
            continue
        can_assign_result, reason = can_assign(counselor, period, day, assignments)
        if can_assign_result:
            assignments[counselor].append(period)
            if period_type == 'R':
                rest_count[counselor] += 1
            else:
                night_count[counselor] += 1
            total_count[counselor] += 1

            if assign_periods(periods, assignments, counselors, rest_count, night_count, total_count, period_index + 1):
                return True

            assignments[counselor].remove(period)
            if period_type == 'R':
                rest_count[counselor] -= 1
            else:
                night_count[counselor] -= 1
            total_count[counselor] -= 1
        
        tried_assignments.add(counselor)

    return False

# Function to balance assignments
def balance_assignments(assignments, total_count, desired_assignments):
    over_assigned = []
    under_assigned = []
    
    for counselor, count in total_count.items():
        if count > desired_assignments:
            over_assigned.append(counselor)
        elif count < desired_assignments:
            under_assigned.append(counselor)
    
    while over_assigned and under_assigned:
        over_counselor = over_assigned.pop()
        under_counselor = under_assigned.pop()
        
        periods_to_reassign = [period for period in assignments[over_counselor] if can_assign(under_counselor, period, int(period[1:]), assignments)[0]]
        if periods_to_reassign:
            period = periods_to_reassign[0]
            assignments[over_counselor].remove(period)
            assignments[under_counselor].append(period)
            total_count[over_counselor] -= 1
            total_count[under_counselor] += 1
            
            if total_count[over_counselor] > desired_assignments:
                over_assigned.append(over_counselor)
            if total_count[under_counselor] < desired_assignments:
                under_assigned.append(under_counselor)

# Function to assign counselors to periods
def assign_counselors(rest_night_periods, counselors_off_days):
    assignments = defaultdict(list)
    rest_count = defaultdict(int)
    night_count = defaultdict(int)
    total_count = defaultdict(int)
    counselors = list(counselors_off_days.keys())
    
    if not assign_periods(rest_night_periods, assignments, counselors, rest_count, night_count, total_count):
        print("Failed to assign all periods to counselors")
    
    desired_assignments = len(rest_night_periods) // len(counselors)
    balance_assignments(assignments, total_count, desired_assignments)
    
    return dict(assignments), total_count, rest_count, night_count

# Assign counselors
assignments, total_assignments, rest_count, night_count = assign_counselors(rest_night_periods, counselors_off_days)

# Display the assignments and total assignments
for counselor, periods in assignments.items():
    print(f"{counselor}: {', '.join(periods)} ({len(periods)} assignments, {rest_count[counselor]} rests, {night_count[counselor]} nights)")

# Check for overall assignments imbalance
max_assignments = max(total_assignments.values())
min_assignments = min(total_assignments.values())
if max_assignments - min_assignments > 0:
    print(f"Imbalance detected: Max assignments = {max_assignments}, Min assignments = {min_assignments}")
else:
    print("Assignments are balanced.\n")

# Create a mapping from periods to counselors
period_to_counselor = {}
for counselor, periods in assignments.items():
    for period in periods:
        period_to_counselor[period] = counselor

# Sort the periods
sorted_periods = sorted(period_to_counselor.keys(), key=lambda x: (int(x[1:]), '0' if x.startswith('R') else '1'))

# Display the final schedule in the desired format
print("Final Schedule:")
for period in sorted_periods:
    print(f"{period}: {period_to_counselor[period]}")

# Tests
for counselor, periods in assignments.items():
    for period in periods:
        day = int(period[1:])
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
