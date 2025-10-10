import streamlit as st

# Page configuration
st.set_page_config(page_title="Home", page_icon="🏠")

st.title("Welcome to the Multi-Page Streamlit App")

# Use session state to store input
if "my_input" not in st.session_state:
    st.session_state["my_input"] = ""

st.session_state["my_input"] = st.text_input("Enter some text:", st.session_state["my_input"])

if st.button("Submit"):
    st.write("You entered:", st.session_state["my_input"])
