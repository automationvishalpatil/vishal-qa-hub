import streamlit as st
import pandas as pd
import os
# import numpy as np # Removed numpy as it is no longer needed

# --- Configuration ---
FILE_PATH = 'data/premise_data_N.xlsx' # Updated file path
USER_CREDENTIALS = {'admin': 'admin'}

# --- Data Initialization and Setup ---
# CRITICAL FIX: Removed @st.cache_resource to prevent old file states from being cached.
def setup_data_file():
    """
    Checks for the data directory and returns True if the required Excel file exists and contains data.
    """
    os.makedirs('data', exist_ok=True)
    
    if not os.path.exists(FILE_PATH):
        # Do NOT create the file. Inform the user and return False.
        st.error(f"🚨 Required data file not found: '{FILE_PATH}'")
        st.markdown("Please ensure the Excel file is placed in the `data/` directory.")
        return False
        
    # If the file exists, perform a robustness check (adding 'Test_Case_ID' if missing)
    try:
        # IMPORTANT: Explicitly read the first sheet (index 0) to prevent issues with sheet names
        df = pd.read_excel(FILE_PATH, sheet_name=0)
        
        if df.empty:
            st.error(f"🚨 Successfully found '{FILE_PATH}' but the first sheet (Sheet 0) appears to be **empty** or could not be read.")
            st.markdown("Please verify that the first sheet of your Excel file contains the data.")
            return False

        # Add 'Test_Case_ID' and utilization columns if they are missing (for legacy files)
        required_util_cols = ['Utilized_PID', 'Utilized_Dev', 'Test_Case_ID']
        needs_save = False
        
        for col in required_util_cols:
            if col not in df.columns:
                 df[col] = '' if col == 'Test_Case_ID' else 'No'
                 needs_save = True
                 st.info(f"Added missing required column: '{col}' to the data file.")

        if needs_save:
             df.to_excel(FILE_PATH, index=False)

        # Check if critical columns are present (optional, but good practice)
        required_cols_to_check = ['Premise_ID', 'Post_Code','Street_Name', 'Street_Number', 'UPRN', 'Network_Type', 'Network_Owner', 'Cabinet', 'Dummy_Device_ID']
        if not all(col in df.columns for col in required_cols_to_check):
            missing_cols = [col for col in required_cols_to_check if col not in df.columns]
            #st.warning(f"Missing core columns: {', '.join(missing_cols)}. Data retrieval may fail.")
            # We don't return False here, allowing the app to run but with a warning

    except Exception as e:
         st.error(f"Error reading or validating existing Excel file: {e}")
         return False

    return True

# --- Core Functions for Data Management ---
def get_and_update_id(id_type):
    """
    Reads the data from the disk, picks the first unutilized ID of the specified type,
    updates the 'Utilized' column for that row and sets the Test_Case_ID, 
    and saves the file. Returns the full updated row (as a Series).
    """
    try:
        # No cache here, forcing read from disk every time
        df = pd.read_excel(FILE_PATH, sheet_name=0)
    except FileNotFoundError:
        return "Data file not found. Please check setup."
    except Exception as e:
        return f"Error reading data file: {e}"

    # Determine which columns to use based on the request type
    if id_type == 'Premise ID / Post Code':
        id_col = 'Premise_ID'
        util_col = 'Utilized_PID'
    elif id_type == 'Dummy device':
        id_col = 'Dummy_Device_ID'
        util_col = 'Utilized_Dev'
    else:
        return "Invalid ID type specified."

    # Check if utilization column exists (safety check)
    if util_col not in df.columns:
        return f"Error: Column '{util_col}' not found in the Excel data. Run setup_data_file again."


    # Find the first row index where the ID is not utilized
    unutilized_row_index = df[df[util_col].astype(str).str.upper() == 'NO'].index
    
    if unutilized_row_index.empty:
        return f"No unutilized {id_col} found."
    
    # Get the index of the row to update
    row_index_to_update = unutilized_row_index[0]
    
    # Get the required Test Case ID
    test_case_id_val = st.session_state.get('test_case_id_input', 'N/A')

    # Update the Utilized column and Test_Case_ID in the DataFrame
    df.loc[row_index_to_update, util_col] = 'Yes'
    df.loc[row_index_to_update, 'Test_Case_ID'] = test_case_id_val

    # Capture the updated row data before saving (as a Series)
    updated_row_series = df.loc[row_index_to_update]

    # Save the updated DataFrame back to the Excel file
    try:
        df.to_excel(FILE_PATH, index=False)
    except Exception as e:
        st.error(f"Error updating Excel file: {e}")
        return None

    # Return the updated row data (Series)
    return updated_row_series

# --- UI Functions ---

def login_page():
    """Displays the login form and handles authentication."""
    st.title("🔐 Login to Data Request Portal")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.rerun() # Refresh to move to the home page
            else:
                st.error("Invalid Username or Password")

def home_page():
    """Displays the main application UI."""
    
    st.sidebar.title("User Options")
    st.sidebar.write(f"Logged in as: **{st.session_state['username']}**")
    
    # Cache clear button for troubleshooting
    if st.sidebar.button("⚠️ Clear Streamlit Cache"):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.rerun()
        
    if st.sidebar.button("Logout"):
        del st.session_state['logged_in']
        del st.session_state['username']
        st.rerun()

    # Main content
    st.title("🏠 Data Request Portal")
    st.subheader("Select a Request Type")

    # Option selection 
    options = [
        "Premise ID / Post Code", 
        "Dummy device"
    ]
    
    selected_option = st.radio(
        "What data do you need?", 
        options,
        key="request_option_radio"
    )

    # Show test case ID input only if an option is selected
    if selected_option:
        test_case_id = st.text_input("Enter **Test Case ID** (Mandatory)", key="test_case_id_input")
        if test_case_id:
            if st.button(f"Submit Request for: {selected_option}", key="submit_request"):
                # Call the function to get and update the ID
                result = get_and_update_id(selected_option) # result is now a Series or an error string

                if result is not None:
                    if isinstance(result, str): # Error or No unutilized IDs message
                        st.warning(f"⚠️ {result}")
                    else: # Success: result is a pandas Series (the updated row)
                        st.success(f"✅ Successfully retrieved and marked as utilized!")
                        
                        # Identify the main ID that was requested
                        id_col = 'Premise_ID' if selected_option == 'Premise ID / Post Code' else 'Dummy_Device_ID'
                        requested_id = result[id_col]

                        st.markdown(f"### Requested ID: **{requested_id}**")
                        
                        # Convert the single Series (row) into a DataFrame for display
                        # We transpose (.T) and reset index to make it look like a single-row table
                        df_result = pd.DataFrame(result).T.reset_index(drop=True)
                        
                        # Display the result in a table format
                        st.markdown("---")
                        st.subheader("FMCT Premise Details are as follows:")
                        # use_container_width=True ensures the table fills the screen width
                        st.dataframe(df_result, use_container_width=True, hide_index=True)
                else:
                    st.error("An error occurred during data retrieval/update.")
        else:
            st.info("Please enter a **Test Case ID** to proceed.")

# --- Main Application Logic ---
if __name__ == "__main__":
    
    setup_ok = setup_data_file()

    # Initialize session state for login
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    # Stop execution if setup failed (i.e., file is missing or empty)
    if not setup_ok:
        st.stop()
        
    if st.session_state['logged_in']:
        home_page()
    else:
        login_page()