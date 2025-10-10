import streamlit as st

st.title("Projects Page")

st.write("Here, you'll find details of all our awesome projects!")

# Access the session state variable
st.write(f"You entered on the homepage: {st.session_state.get('my_input', 'Nothing yet!')}")