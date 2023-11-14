from ortools.sat.python import cp_model
import pandas as pd


model = cp_model.CpModel()

employees = {
    'Juana Matos': {'available_days': ['Tuesday','Wednesday','Thursday', 'Friday', 'Saturday', 'Sunday'], 'shift_preferences': ['day']},
    'Angela Domingues': {'available_days': ['Monday','Tuesday','Wednesday','Friday'], 'shift_preferences': ['night']},
    'Matilda Morão': {'available_days': ['Monday','Wednesday','Thursday', 'Friday', 'Saturday', 'Sunday'], 'shift_preferences': ['night','day']}
}

patients = {
    'Mappy Carino': {'care_days': ['Monday', 'Tuesday','Wednesday','Thursday', 'Friday', 'Saturday', 'Sunday'], 'care_shifts': ['day', 'night']}
}

shift_vars = {}
for employee in employees:
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        for shift in ['day', 'night']:
            var_id = (employee, day, shift)
            shift_vars[var_id] = model.NewBoolVar(str(var_id))

# New Patient Care Requirements
for patient, care_details in patients.items():
    for day in care_details['care_days']:
        for shift in ['day', 'night']:
            # Check if this shift is required for the patient
            if shift in care_details['care_shifts']:
                available_employees = [shift_vars[(employee, day, shift)] 
                                       for employee, details in employees.items()
                                       if day in details['available_days'] and shift in details['shift_preferences']]
                if available_employees:
                    model.Add(sum(available_employees) >= 1)
                else:
                    print(f"No available employees for {shift} shift on {day}")



# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Solution found, now create a more structured schedule table
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print("Solution found!")

    # Initialize a dictionary to store the schedule
    schedule_dict = {employee: {day: '' for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']} for employee in employees}

    # Populate the schedule dictionary
    for var_id, var in shift_vars.items():
        if solver.Value(var):
            employee, day, shift = var_id
            patient_shift_info = f"{list(patients.keys())[0]} {shift}"  # Assuming one patient for now
            schedule_dict[employee][day] = patient_shift_info

    # Convert the schedule dictionary into a pandas DataFrame for display
    schedule_df = pd.DataFrame.from_dict(schedule_dict, orient='index')

    # Print the DataFrame
    print(schedule_df)

    csv_file_path = '/home/gmbleasdale/Desktop/schedule.csv'

    # Export the DataFrame to a CSV file
    schedule_df.to_csv(csv_file_path, index=True)

    print(f"Schedule exported to {csv_file_path}")
else:
    print("No solution found.")
