import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Initialize session state to store event details and recorded times
if 'events' not in st.session_state:
    st.session_state.events = {}
if 'current_event' not in st.session_state:
    st.session_state.current_event = None
if 'recorded_times' not in st.session_state:
    st.session_state.recorded_times = pd.DataFrame(columns=['Event', 'Bib Number', 'Category', 'Recorded Time'])

# Function to create a new event
def create_event(event_name):
    st.session_state.events[event_name] = {'categories': {}, 'gun_start_times': {}, 'cut_off_times': {}}
    st.session_state.current_event = event_name

# Function to add a category to the current event
def add_category(category, cut_off_time):
    if st.session_state.current_event:
        st.session_state.events[st.session_state.current_event]['categories'][category] = cut_off_time

# Function to record gun start time for a category
def record_gun_start_time(category, time):
    if st.session_state.current_event:
        st.session_state.events[st.session_state.current_event]['gun_start_times'][category] = time
        cut_off_time = st.session_state.events[st.session_state.current_event]['categories'][category]
        st.session_state.events[st.session_state.current_event]['cut_off_times'][category] = time + timedelta(minutes=cut_off_time)

# Function to record time for a bib number
def record_bib_time(bib_number, category):
    current_time = datetime.now()
    new_record = {
        'Event': st.session_state.current_event,
        'Bib Number': bib_number,
        'Category': category,
        'Recorded Time': current_time
    }
    st.session_state.recorded_times = st.session_state.recorded_times.append(new_record, ignore_index=True)

# Streamlit UI with tabs
st.title("Marathon Time Recorder")

tab1, tab2, tab3, tab4 = st.tabs(["Ongoing Time", "Records", "Add Event", "Event List"])

with tab1:
    st.header("Ongoing Time")
    if st.session_state.current_event:
        st.write(f"Current Event: {st.session_state.current_event}")
        selected_category = st.selectbox("Select Category for Gun Start Time:", options=list(st.session_state.events[st.session_state.current_event]['categories'].keys()))
        gun_start_time = st.time_input("Enter Gun Start Time:", datetime.now().time())
        if st.button("Record Gun Start Time"):
            record_gun_start_time(selected_category, datetime.combine(datetime.today(), gun_start_time))
            st.success(f"Gun start time recorded for '{selected_category}'!")

        bib_number = st.text_input("Enter Race Bib Number:")
        if st.button("Record Bib Time"):
            record_bib_time(bib_number, selected_category)
            st.success(f"Time recorded for bib number '{bib_number}'!")
    else:
        st.write("No ongoing event. Please create or select an event.")

with tab2:
    st.header("Records")
    if st.session_state.current_event:
        st.write("Recorded Times:")
        st.write(st.session_state.recorded_times[st.session_state.recorded_times['Event'] == st.session_state.current_event])
    else:
        st.write("No event selected. Please create or select an event to view records.")

with tab3:
    st.header("Add Event")
    event_name = st.text_input("Enter Event Name:")
    if st.button("Create Event"):
        create_event(event_name)
        st.success(f"Event '{event_name}' created!")

    if st.session_state.current_event:
        category = st.text_input("Enter Category (e.g., 5k, 10k):")
        cut_off_time = st.number_input("Enter Cut-Off Time (in minutes):", min_value=0)
        if st.button("Add Category"):
            add_category(category, cut_off_time)
            st.success(f"Category '{category}' added with cut-off time {cut_off_time} minutes!")

with tab4:
    st.header("Event List")
    if st.session_state.events:
        selected_event = st.selectbox("Select Event:", options=list(st.session_state.events.keys()))
        if st.button("Select Event"):
            st.session_state.current_event = selected_event
            st.success(f"Event '{selected_event}' selected!")
    else:
        st.write("No events created yet. Please create an event.")
