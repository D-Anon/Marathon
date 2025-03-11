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
def create_event(event_name, event_date):
    st.session_state.events[event_name] = {
        'date': event_date,
        'categories': {},
        'gun_start_times': {},
        'cut_off_times': {}
    }
    st.session_state.current_event = event_name

# Function to add categories to the current event
def add_categories(categories):
    if st.session_state.current_event:
        for category, cut_off_time in categories.items():
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

tab1, tab2 = st.tabs(["Events", "Records"])

with tab1:
    st.header("Events")
    today = datetime.today().date()

    # Event creation form
    with st.expander("Create New Event"):
        event_name = st.text_input("Enter Event Name:", key="new_event_name")
        event_date = st.date_input("Enter Event Date:", datetime.today(), key="new_event_date")
        if st.button("Create Event"):
            create_event(event_name, event_date)
            st.success(f"Event '{event_name}' created for {event_date}!")

    # List all events
    if st.session_state.events:
        for event_name, event_details in st.session_state.events.items():
            event_date = event_details['date']
            label = "Ongoing" if event_date == today else "Upcoming"
            st.write(f"{event_name} - {event_date} ({label})")
            if st.button(f"Select {event_name}", key=f"select_{event_name}"):
                st.session_state.current_event = event_name
                st.success(f"Event '{event_name}' selected!")

            # Manage categories for the selected event
            if st.session_state.current_event == event_name:
                st.write("Add Categories:")
                num_categories = st.number_input("Number of Categories:", min_value=1, value=1, key=f"num_categories_{event_name}")
                categories = {}
                for i in range(num_categories):
                    category = st.text_input(f"Category {i+1} Name (e.g., 5k, 10k):", key=f"category_{i}_{event_name}")
                    cut_off_time = st.number_input(f"Cut-Off Time for {category} (in minutes):", min_value=0, key=f"cut_off_{i}_{event_name}")
                    categories[category] = cut_off_time

                if st.button("Add Categories", key=f"add_categories_{event_name}"):
                    add_categories(categories)
                    st.success("Categories added successfully!")
    else:
        st.write("No events created yet. Please create an event.")

with tab2:
    st.header("Records")
    if st.session_state.current_event:
        st.write("Recorded Times:")
        st.write(st.session_state.recorded_times[st.session_state.recorded_times['Event'] == st.session_state.current_event])
    else:
        st.write("No event selected. Please create or select an event to view records.")
