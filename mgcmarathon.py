import streamlit as st
import pandas as pd
from datetime import datetime

# Initialize session state to store gun start times and recorded times
if 'gun_start_times' not in st.session_state:
    st.session_state.gun_start_times = {}
if 'recorded_times' not in st.session_state:
    st.session_state.recorded_times = pd.DataFrame(columns=['Bib Number', 'Category', 'Recorded Time'])

# Function to record gun start time
def record_gun_start_time(category, time):
    st.session_state.gun_start_times[category] = time

# Function to record time for a bib number
def record_bib_time(bib_number, category):
    current_time = datetime.now()
    new_record = {'Bib Number': bib_number, 'Category': category, 'Recorded Time': current_time}
    st.session_state.recorded_times = st.session_state.recorded_times.append(new_record, ignore_index=True)

# Streamlit UI
st.title("Marathon Time Recorder")

# Input for gun start time
category = st.text_input("Enter Category for Gun Start Time:")
gun_start_time = st.time_input("Enter Gun Start Time:", datetime.now())
if st.button("Record Gun Start Time"):
    record_gun_start_time(category, gun_start_time)

# Input for race bib number
bib_number = st.text_input("Enter Race Bib Number:")
selected_category = st.selectbox("Select Category:", options=list(st.session_state.gun_start_times.keys()))
if st.button("Record Bib Time"):
    record_bib_time(bib_number, selected_category)

# Display recorded times
st.write("Recorded Times:")
st.write(st.session_state.recorded_times)
