import streamlit as st

# --- UI Setup ---
st.set_page_config(
    page_title="Automation Portal",
    layout="wide"
)

# --- Floating Welcome Message ---
# Using HTML and CSS for a floating animation
st.markdown("""
<style>
@keyframes floatRightToLeft {
    0% { transform: translateX(100%); }
    50% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
}

.floating-text {
    font-size: 2em;
    font-weight: bold;
    color: #0072C6;
    text-align: center;
    overflow: hidden;
    white-space: nowrap;
    animation: floatRightToLeft 28s linear infinite;
    padding: 20px;
}
</style>
<div class="floating-text">Welcome to Vishal's Automation Runner Portal</div>
""", unsafe_allow_html=True)

# --- Company Logo ---
# st.image("https://placehold.co/600x150/0072C6/ffffff?text=VMO2+Logo", caption="VMO2 Automation Portal")
st.image("image.png", caption="Vishal's Automation Portal")
# --- Horizontal Rule ---
st.markdown("---")

# --- Navigation Links ---
st.subheader("Choose an Automation Tool")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.page_link("pages/json_comparator.py", label="Paper Testing Utility", icon="🤖")

with col2:
    st.page_link("pages/Static_Testing.py", label="API Test", icon="⚙️")

with col3:
    st.page_link("pages/Test_Data_Dashboard.py", label="FMCT Test Data Portal", icon="⚙️")

with col4:
    st.page_link("pages/json_comparator.py", label="Paper Testing Tool", icon="⚙️")


# --- Horizontal Rule ---
st.markdown("---")

# --- Copyright Message ---
st.markdown("<p style='text-align:center; color:grey;'>© 2025 VMO2 Automation. All Rights Reserved.</p>", unsafe_allow_html=True)




