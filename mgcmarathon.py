import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time

# Initialize session state to store event details and recorded times
if 'events' not in st.session_state:
    st.session_state.events = {}
if 'current_event' not in st.session_state:
    st.session_state.current_event = None
if 'recorded_times' not in st.session_state:
    st.session_state.recorded_times = pd.DataFrame(columns=['Event', 'Bib Number', 'Category', 'Recorded Time'])
if 'show_event_modal' not in st.session_state:
    st.session_state.show_event_modal = False
if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False
if 'show_event_details' not in st.session_state:
    st.session_state.show_event_details = None
if 'timers' not in st.session_state:
    st.session_state.timers = {}
if 'fullscreen_timer' not in st.session_state:
    st.session_state.fullscreen_timer = None

# Function to create a new event
def create_event(event_name, event_date, categories):
    st.session_state.events[event_name] = {
        'date': event_date,
        'categories': categories,
        'gun_start_times': {},
        'cut_off_times': {}
    }
    st.session_state.current_event = event_name

# Function to edit an event
def edit_event(event_name, event_date, categories):
    if event_name in st.session_state.events:
        st.session_state.events[event_name]['date'] = event_date
        st.session_state.events[event_name]['categories'] = categories
        st.session_state.current_event = event_name

# Function to delete an event
def delete_event(event_name):
    if event_name in st.session_state.events:
        del st.session_state.events[event_name]
        st.session_state.current_event = None
        st.session_state.show_event_details = None

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

tab1, tab2, tab3 = st.tabs(["Events", "Records", "Timer"])

with tab1:
    st.header("Events")
    today = datetime.today().date()

    # Button to open the event creation modal
    if st.button("Create New Event"):
        st.session_state.show_event_modal = True
        st.session_state.edit_mode = False

    # Event creation/edit modal using expander
    if st.session_state.show_event_modal:
        with st.expander("Enter Event Details", expanded=True):
            st.markdown("### Event Details")
            event_name = st.text_input("Enter Event Name:", key="event_name", value=st.session_state.current_event if st.session_state.edit_mode else "")
            event_date = st.date_input("Enter Event Date:", value=st.session_state.events[st.session_state.current_event]['date'] if st.session_state.edit_mode else datetime.today())

            st.markdown("### Add/Edit Categories")
            num_categories = st.number_input("Number of Categories:", min_value=1, value=len(st.session_state.events[st.session_state.current_event]['categories']) if st.session_state.edit_mode else 1, key="num_categories")
            categories = {}
            for i in range(num_categories):
                default_category_name = list(st.session_state.events[st.session_state.current_event]['categories'].keys())[i] if st.session_state.edit_mode else f"Category {i+1}"
                default_cut_off_time = list(st.session_state.events[st.session_state.current_event]['categories'].values())[i] if st.session_state.edit_mode else 0
                category = st.text_input(f"Category {i+1} Name (e.g., 5k, 10k):", key=f"category_{i}", value=default_category_name)
                cut_off_time = st.number_input(f"Cut-Off Time for {category} (in minutes):", min_value=0, key=f"cut_off_{i}", value=default_cut_off_time)
                categories[category] = cut_off_time

            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("Save Event"):
                    if st.session_state.edit_mode:
                        edit_event(event_name, event_date, categories)
                        st.success(f"Event '{event_name}' edited successfully!")
                    else:
                        create_event(event_name, event_date, categories)
                        st.success(f"Event '{event_name}' created for {event_date} with categories!")
                    st.session_state.show_event_modal = False  # Close the modal

            with col2:
                if st.button("Cancel"):
                    st.session_state.show_event_modal = False  # Close the modal without saving

    # List all events as tiles
    if st.session_state.events:
        for event_name, event_details in st.session_state.events.items():
            event_date = event_details['date']
            label = "Ongoing" if event_date == today else "Upcoming"
            if st.button(f"{event_name} - {event_date} ({label})", key=f"event_{event_name}"):
                st.session_state.show_event_details = event_name

        # Show event details
        if st.session_state.show_event_details:
            event_name = st.session_state.show_event_details
            event_details = st.session_state.events[event_name]
            with st.expander(f"Event Details: {event_name}", expanded=True):
                st.write(f"**Event Name:** {event_name}")
                st.write(f"**Event Date:** {event_details['date']}")
                st.write("**Categories and Cut-Off Times:**")
                for category, cut_off_time in event_details['categories'].items():
                    st.write(f"- {category}: {cut_off_time} minutes")

                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("Edit Event", key=f"edit_{event_name}"):
                        st.session_state.show_event_modal = True
                        st.session_state.edit_mode = True
                with col2:
                    if st.button("Delete Event", key=f"delete_{event_name}"):
                        delete_event(event_name)
                        st.success(f"Event '{event_name}' deleted!")
    else:
        st.write("No events created yet. Please create an event.")

with tab2:
    st.header("Records")
    if st.session_state.current_event:
        st.write("Recorded Times:")
        st.write(st.session_state.recorded_times[st.session_state.recorded_times['Event'] == st.session_state.current_event])
    else:
        st.write("No event selected. Please create or select an event to view records.")

with tab3:
    st.header("Timer")
    today = datetime.today().date()

    # Dropdown to select an ongoing event
    ongoing_events = [event for event, details in st.session_state.events.items() if details['date'] == today]
    selected_event = st.selectbox("Select Ongoing Event", options=ongoing_events)

    if selected_event:
        st.session_state.current_event = selected_event
        categories = st.session_state.events[selected_event]['categories'].keys()

        for category in categories:
            st.write(f"**Category:** {category}")
            if category not in st.session_state.timers:
                st.session_state.timers[category] = {'start_time': None, 'elapsed_time': 0, 'running': False}

            timer = st.session_state.timers[category]
            if timer['running']:
                timer['elapsed_time'] += time.time() - st.session_state.last_update
                st.session_state.last_update = time.time()

            col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
            with col1:
                if st.button("Start", key=f"start_{category}"):
                    if not timer['running']:
                        timer['start_time'] = datetime.now() - timedelta(seconds=timer['elapsed_time'])
                        timer['running'] = True
                        st.session_state.last_update = time.time()
            with col2:
                if st.button("Pause", key=f"pause_{category}"):
                    if timer['running']:
                        timer['elapsed_time'] = (datetime.now() - timer['start_time']).total_seconds()
                        timer['running'] = False
            with col3:
                if st.button("Stop", key=f"stop_{category}"):
                    if timer['running']:
                        timer['elapsed_time'] = (datetime.now() - timer['start_time']).total_seconds()
                        timer['running'] = False
                        st.session_state.timers[category] = {'start_time': None, 'elapsed_time': 0, 'running': False}
            with col4:
                if st.button("Fullscreen", key=f"fullscreen_{category}"):
                    st.session_state.fullscreen_timer = category

            elapsed_time = timer['elapsed_time']
            hours, remainder = divmod(elapsed_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            milliseconds = int((elapsed_time - int(elapsed_time)) * 1000)
            st.write(f"Elapsed Time: {int(hours)}:{int(minutes)}:{int(seconds)}.{milliseconds:03d}")

        if st.session_state.fullscreen_timer:
            category = st.session_state.fullscreen_timer
            timer = st.session_state.timers[category]
            elapsed_time = timer['elapsed_time']
            hours, remainder = divmod(elapsed_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            milliseconds = int((elapsed_time - int(elapsed_time)) * 1000)
            st.write(f"# Fullscreen Timer: {category}")
            st.write(f"## {int(hours)}:{int(minutes)}:{int(seconds)}.{milliseconds:03d}")
            if st.button("Exit Fullscreen"):
                st.session_state.fullscreen_timer = None
