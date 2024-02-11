import streamlit as st
import pandas as pd

# Define the time slots for the planner
time_slots = pd.date_range(start='00:00', end='23:59', freq='H')

# Create an empty timetable DataFrame
timetable = pd.DataFrame(index=time_slots, columns=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])

# Function to add task to timetable
def add_task(task_name, deadline, day):
    timetable.loc[deadline, day] = task_name

# Streamlit app
def main():
    st.title("Weekly Planner")
    
    # Sidebar for user input
    st.sidebar.header("Add Task")
    task_name = st.sidebar.text_input("Task Name")
    deadline_day = st.sidebar.selectbox("Deadline Day", ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
    deadline_time = st.sidebar.time_input("Deadline Time")
    deadline_datetime = pd.to_datetime(deadline_time.strftime("%H:%M:%S"))
    
    # Button to add task to timetable
    if st.sidebar.button("Add Task"):
        add_task(task_name, deadline_datetime, deadline_day)
    
    # Display the timetable
    st.subheader("Weekly Timetable")
    st.dataframe(timetable)

if __name__ == "__main__":
    main()
