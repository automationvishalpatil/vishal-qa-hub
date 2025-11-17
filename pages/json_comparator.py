import streamlit as st
import json
from deepdiff import DeepDiff

# --- UI Setup ---
st.set_page_config(
    page_title="JSON Comparator",
    layout="wide"
)

st.title("JSON Response Comparator")
st.markdown("Paste your two JSON payloads below to compare them.")

# --- Helper functions ---

def pretty_print_json(json_string):
    """Formats a JSON string for display."""
    try:
        data = json.loads(json_string)
        return json.dumps(data, indent=4)
    except json.JSONDecodeError:
        return "Invalid JSON"

def get_diff_summary(diff):
    """Generates a readable summary of differences from DeepDiff output."""
    summary = []
    if 'dictionary_item_added' in diff:
        summary.append(f"Keys added: {', '.join(diff['dictionary_item_added'])}")
    if 'dictionary_item_removed' in diff:
        summary.append(f"Keys removed: {', '.join(diff['dictionary_item_removed'])}")
    if 'values_changed' in diff:
        summary.append("Values changed:")
        for key, value in diff['values_changed'].items():
            summary.append(f"- {key}: '{value['old_value']}' -> '{value['new_value']}'")
    if 'type_changes' in diff:
        summary.append("Type changes:")
        for key, value in diff['type_changes'].items():
            summary.append(f"- {key}: '{value['old_type'].__name__}' -> '{value['new_type'].__name__}'")
    return summary

# --- Main App ---

col1, col2 = st.columns(2)

with col1:
    st.subheader("Response 1")
    json1_input = st.text_area("JSON 1", height=400, key="json1")

with col2:
    st.subheader("Response 2")
    json2_input = st.text_area("JSON 2", height=400, key="json2")

st.markdown("---")

if st.button("Compare Now"):
    try:
        json1_data = json.loads(json1_input)
        json2_data = json.loads(json2_input)

        st.subheader("Comparison Results")
        diff = DeepDiff(json1_data, json2_data, ignore_order=True)

        if not diff:
            st.success("The two JSON payloads are identical.")
        else:
            st.error("Differences Found:")
            
            # Display a human-readable summary
            diff_summary = get_diff_summary(diff)
            for item in diff_summary:
                st.write(item)

            st.markdown("---")
            
            # Display pretty-formatted JSONs side-by-side with highlights
            col3, col4 = st.columns(2)
            with col3:
                st.subheader("Pretty-Formatted JSON 1")
                st.json(json1_data)
            with col4:
                st.subheader("Pretty-Formatted JSON 2")
                st.json(json2_data)

    except json.JSONDecodeError:
        st.error("Error: Please enter valid JSON in both text areas.")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")

# Footer
st.markdown("---")
st.markdown("<p style='text-align:center; color:grey;'>JSON Comparator Tool</p>", unsafe_allow_html=True)
