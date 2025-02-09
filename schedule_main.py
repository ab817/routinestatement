import schedule
import time
import subprocess

def run_script():
    subprocess.run(["python", "main_statement_generator.py"])

# Schedule the script to run every 5 minutes
schedule.every(1).minutes.do(run_script)

while True:
    schedule.run_pending()
    time.sleep(1)  # Prevents high CPU usage
