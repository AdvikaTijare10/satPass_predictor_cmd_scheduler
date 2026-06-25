
# import streamlit as st
# import pandas as pd
# import requests

# FASTAPI_URL = "http://127.0.0.1:8000"  # Your local FastAPI bridge

# st.set_page_config(page_title="Satellite Mission Planner", layout="wide")
# st.title("🛰️ Satellite Ground Station - Mission Planner")

# # --- REFRESH BUTTON ---
# if st.button("🔄 Refresh System Data"):
#     st.rerun()

# col1, col2 = st.columns([3, 2], gap="large")

# with col1:
#     st.subheader("🗓️ Upcoming Passes")
#     # Fetch from your new /passes/future endpoint
#     try:
#         response = requests.get(f"{FASTAPI_URL}/passes/future")
#         if response.status_code == 200:
#             if response.status_code == 200:
#                 passes_df = pd.DataFrame(response.json())
                
#                 # 🔥 Reorder columns here:
#                 cols_order = ["id", "satellite_name", "start_time", "end_time", "available_duration_secs", "status"]
#                 # Check if columns exist to avoid errors
#                 existing_cols = [c for c in cols_order if c in passes_df.columns]
#                 passes_df = passes_df[existing_cols]
                
#                 st.dataframe(passes_df, use_container_width=True)
#         else:
#             st.error("Could not load passes from backend.")
#     except:
#         st.error("Backend offline.")

# with col2:
#     st.subheader("🎮 Create Command")
#     with st.form("command_form", clear_on_submit=True):
#         command_type = st.selectbox("Command Type", ["PING_BEACON", "TRIGGER_CAMERA_PAYLOAD", "FETCH_TELEMETRY"])
#         priority = st.selectbox("Priority Level", [1, 2, 3, 4, 5])
#         submit_btn = st.form_submit_button("🚀 Submit")
        
#         if submit_btn:
#             payload = {"command_type": command_type, "priority": priority}
#             res = requests.post(f"{FASTAPI_URL}/commands", json=payload)
#             if res.status_code == 200:
#                 st.success("Command queued!")
#             else:
#                 st.error("Failed to queue command.")

# # --- BOTTOM SECTION ---
# st.markdown("---")
# st.subheader("📋 Scheduled Commands Timeline")

# # Add a button to trigger the scheduler you just wrote!
# if st.button("⚙️ Run Scheduler Engine"):
#     with st.spinner("Packing timeline..."):
#         res = requests.post(f"{FASTAPI_URL}/scheduler/run")
#         if res.status_code == 200:
#             st.success("Timeline optimized!")
#         else:
#             st.error("Scheduler failed.")

# # Load the timeline from the /commands/timeline endpoint
# try:
#     res = requests.get(f"{FASTAPI_URL}/commands/timeline")
#     if res.status_code == 200:
#         timeline_df = pd.DataFrame(res.json())
        
#         # 🔥 Reorder columns here:
#         # Assuming you want: id, command_type, priority, pass_window_id, scheduled_start_offset_sec, etc.
#         cols_order = ["id", "command_type", "priority", "pass_window_id", "execution_log","created_at","scheduled_start_offset_sec", "scheduled_end_offset_sec", "status"]
#         existing_cols = [c for c in cols_order if c in timeline_df.columns]
#         timeline_df = timeline_df[existing_cols]
        
#         st.dataframe(timeline_df, use_container_width=True)
# except:
#     st.warning("No data found.")



import streamlit as st
import pandas as pd
import requests

FASTAPI_URL = "http://127.0.0.1:8000"  # Your local FastAPI bridge

st.set_page_config(page_title="Satellite Mission Planner", layout="wide")
st.title("🛰️ Satellite Ground Station - Mission Planner")

# --- REFRESH BUTTON ---
if st.button("🔄 Refresh System Data"):
    st.rerun()

col1, col2 = st.columns([3, 2], gap="large")

with col1:
    st.subheader("🗓️ Upcoming Passes")
    
    # --- NEW CALCULATION BUTTON ---
    if st.button("🚀 Calculate Future Passes"):
        with st.spinner("Calculating orbital mechanics..."):
            res = requests.post(f"{FASTAPI_URL}/calculate-passes")
            if res.status_code == 200:
                st.success("Passes updated! Refreshing data...")
                st.rerun()
            else:
                st.error("Failed to calculate passes.")

    # Fetch from your new /passes/future endpoint
    try:
        response = requests.get(f"{FASTAPI_URL}/passes/future")
        if response.status_code == 200:
            if response.status_code == 200:
                passes_df = pd.DataFrame(response.json())
                
                # 🔥 Reorder columns here:
                cols_order = ["id", "satellite_name", "start_time", "end_time", "available_duration_secs", "status"]
                # Check if columns exist to avoid errors
                existing_cols = [c for c in cols_order if c in passes_df.columns]
                passes_df = passes_df[existing_cols]
                
                st.dataframe(passes_df, use_container_width=True)
        else:
            st.error("Could not load passes from backend.")
    except:
        st.error("Backend offline.")

with col2:
    st.subheader("🎮 Create Command")
    with st.form("command_form", clear_on_submit=True):
        command_type = st.selectbox("Command Type", ["PING_BEACON", "TRIGGER_CAMERA_PAYLOAD", "FETCH_TELEMETRY"])
        priority = st.selectbox("Priority Level", [1, 2, 3, 4, 5])
        submit_btn = st.form_submit_button("🚀 Submit")
        
        if submit_btn:
            payload = {"command_type": command_type, "priority": priority}
            res = requests.post(f"{FASTAPI_URL}/commands", json=payload)
            if res.status_code == 200:
                st.success("Command queued!")
            else:
                st.error("Failed to queue command.")

# --- BOTTOM SECTION ---
st.markdown("---")
st.subheader("📋 Scheduled Commands Timeline")

# Add a button to trigger the scheduler you just wrote!
if st.button("⚙️ Run Scheduler Engine"):
    with st.spinner("Packing timeline..."):
        res = requests.post(f"{FASTAPI_URL}/scheduler/run")
        if res.status_code == 200:
            st.success("Timeline optimized!")
        else:
            st.error("Scheduler failed.")

# Load the timeline from the /commands/timeline endpoint
try:
    res = requests.get(f"{FASTAPI_URL}/commands/timeline")
    if res.status_code == 200:
        timeline_df = pd.DataFrame(res.json())
        
        # 🔥 Reorder columns here:
        # Assuming you want: id, command_type, priority, pass_window_id, scheduled_start_offset_sec, etc.
        cols_order = ["id", "command_type", "priority", "pass_window_id", "execution_log","created_at","scheduled_start_offset_sec", "scheduled_end_offset_sec", "status"]
        existing_cols = [c for c in cols_order if c in timeline_df.columns]
        timeline_df = timeline_df[existing_cols]
        
        st.dataframe(timeline_df, use_container_width=True)
except:
    st.warning("No data found.")