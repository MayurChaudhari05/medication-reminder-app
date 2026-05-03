import tkinter as tk
from tkinter import messagebox
import sqlite3
import schedule
import time
from plyer import notification
import threading
import re


# Initialize the SQLite Database
def init_db():
    conn = sqlite3.connect('medication.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            time TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


# Function to Validate Time Format (HH:MM - 24hr Format)
def validate_time_format(time_str):
    if re.match(r'^\d{2}:\d{2}$', time_str):
        hour, minute = map(int, time_str.split(':'))
        if 0 <= hour < 24 and 0 <= minute < 60:
            return True
    return False


# Schedule Notifications for Medications
def schedule_notifications(name, time_str):
    def notify():
        print(f"Notification triggered for {name} at {time_str}")  # Debug Line
        try:
            notification.notify(
                title="Medication Reminder",
                message=f"Time to take your medication: {name}",
                timeout=10
            )
            print("Notification sent successfully!")  # Debug Line
        except Exception as e:
            print(f"Error in notification: {e}")  # Debug Line

    schedule.every().day.at(time_str).do(notify)
    print(f"Scheduled {name} at {time_str}")  # Debug Line


# GUI Class for the Application
class MedicationTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Medication Tracker")
        self.root.geometry("400x400")

        # Input Variables
        self.name_var = tk.StringVar()
        self.time_var = tk.StringVar()

        # Medication Name Input
        tk.Label(root, text="Medication Name:").pack(pady=5)
        tk.Entry(root, textvariable=self.name_var).pack(pady=5)

        # Medication Time Input
        tk.Label(root, text="Time (HH:MM - 24hr format):").pack(pady=5)
        tk.Entry(root, textvariable=self.time_var).pack(pady=5)

        # Buttons
        tk.Button(root, text="Add Medication", command=self.add_medication).pack(pady=10)
        tk.Button(root, text="View Schedule", command=self.view_schedule).pack(pady=5)

    # Function to Add Medication to Database and Schedule Notification
    def add_medication(self):
        name = self.name_var.get().strip()
        time_str = self.time_var.get().strip()

        # Validate Inputs
        if not name or not time_str:
            messagebox.showerror("Error", "All fields are required!")
            return
        if not validate_time_format(time_str):
            messagebox.showerror("Error", "Invalid time format! Use HH:MM in 24-hour format.")
            return

        # Save to Database
        try:
            conn = sqlite3.connect('medication.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO medications (name, time) VALUES (?, ?)", (name, time_str))
            conn.commit()
            conn.close()
            schedule_notifications(name, time_str)
            messagebox.showinfo("Success", f"Medication '{name}' scheduled at {time_str}.")
        except Exception as e:
            messagebox.showerror("Database Error", f"Error saving data: {e}")

    # Function to View Scheduled Medications
    def view_schedule(self):
        conn = sqlite3.connect('medication.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM medications")
        rows = cursor.fetchall()
        conn.close()

        schedule_window = tk.Toplevel(self.root)
        schedule_window.title("Medication Schedule")

        if rows:
            for idx, row in enumerate(rows):
                tk.Label(schedule_window, text=f"{row[1]} - {row[2]}").pack()
        else:
            tk.Label(schedule_window, text="No medications scheduled.").pack()


# Scheduler Function to Run in Background
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)


# Main Program Execution
if __name__ == "__main__":
    # Initialize Database
    init_db()

    # Create Main Window
    root = tk.Tk()
    app = MedicationTrackerApp(root)

    # Start Scheduler in Background Thread
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()

    # Run Tkinter Main Loop
    root.mainloop()
