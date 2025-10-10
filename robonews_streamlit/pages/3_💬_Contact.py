import streamlit as st

st.title("Contact Us")

st.write("Feel free to reach out to us via the form below!")

st.text_input("Your Name")
st.text_area("Your Message")

if st.button("Submit"):
    st.success("Thank you for reaching out!")
