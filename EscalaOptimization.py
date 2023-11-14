from ortools.sat.python import cp_model
import pandas as pd


model = cp_model.CpModel()

employees = {
    'Juana Matos': {'available_days': ['Monday','Tuesday','Wednesday','Thursday', 'Friday', 'Saturday', 'Sunday'], 'shift_preferences': ['day']},
    'Angela Domingues': {'available_days': ['Monday','Tuesday','Wednesday','Thursday', 'Friday'], 'shift_preferences': ['night','day']},
    'Matilda Morão': {'available_days': ['Monday','Tuesday','Wednesday','Thursday', 'Friday', 'Saturday', 'Sunday'], 'shift_preferences': ['night','day']}
}

patients = { 
    'Boni': {'care_days': ['Monday', 'Tuesday','Wednesday','Thursday', 'Friday'], 'care_shifts': ['night']},
    'Mappy Carino': {'care_days': ['Monday', 'Tuesday','Wednesday','Thursday', 'Friday', 'Saturday', 'Sunday'], 'care_shifts': ['day', 'night']},

}

# Create shift_vars including patient name
# Create shift_vars including patient name
shift_vars = {}
for patient in patients:
    for employee in employees:
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            for shift in ['day', 'night']:
                var_id = (patient, employee, day, shift)
                shift_vars[var_id] = model.NewBoolVar(str(var_id))

# Define employee capacity (1 shift per day)
employee_capacity = {employee: 1 for employee in employees}

# Define shift cost (1 for each assigned shift)
shift_cost = 1

# Create shift_vars and employee daily capacity constraints
for employee in employees:
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        daily_shifts = []
        for patient in patients:
            for shift in ['day', 'night']:
                var_id = (patient, employee, day, shift)
                shift_vars[var_id] = model.NewBoolVar(str(var_id))
                daily_shifts.append(shift_vars[var_id])
        # Ensure the sum of shifts for each employee each day does not exceed capacity
        model.Add(sum(daily_shifts) * shift_cost <= employee_capacity[employee])

# Adjusted Patient Care Requirements for each patient separately
for patient, care_details in patients.items():
    for day in care_details['care_days']:
        for shift in care_details['care_shifts']:
            available_employees = [shift_vars[(patient, employee, day, shift)]
                                   for employee in employees
                                   if day in employees[employee]['available_days'] and shift in employees[employee]['shift_preferences']]
            if available_employees:
                model.Add(sum(available_employees) >= 1)
            else:
                print(f"No available employees for {patient} on {day} for {shift} shift")

# [Code to solve the model and create the schedule table]

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Solution found, now create a more structured schedule table
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print("Solution found!")
    schedule_dict = {}
    for var_id, var in shift_vars.items():
        if solver.Value(var):
            patient, employee, day, shift = var_id
            if day not in schedule_dict:
                schedule_dict[day] = {}
            schedule_dict[day][employee] = f"{patient} {shift}"

    # Create DataFrame from schedule_dict
    schedule_df = pd.DataFrame.from_dict(schedule_dict, orient='index')

    # Print and export the DataFrame
    print(schedule_df)
    schedule_df.to_csv('/home/gmbleasdale/Desktop/schedule.csv', index=True)
else:
    print("No solution found.")