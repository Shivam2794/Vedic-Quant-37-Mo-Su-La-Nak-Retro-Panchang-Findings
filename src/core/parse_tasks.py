import subprocess
import csv
import io

print("Querying Windows Task Scheduler...")
result = subprocess.run(["schtasks", "/query", "/v", "/fo", "CSV"], capture_output=True, text=True)

if result.returncode != 0:
    print(f"Error: {result.stderr}")
else:
    reader = csv.DictReader(io.StringIO(result.stdout))
    for row in reader:
        task_name = row.get("TaskName", "")
        if "Antigravity" in task_name:
            action = row.get("Task To Run", "")
            schedule = row.get("Schedule Type", "")
            start_time = row.get("Start Time", "")
            print(f"Task: {task_name}\n  Action: {action}\n  Schedule: {schedule} at {start_time}\n")
