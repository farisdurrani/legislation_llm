# app.py
import streamlit as st

def main():
    st.title("Simple Streamlit App with Text Input")

    # Add a text input widget
    user_input = st.text_input("Enter some text:")

    # Display the entered text
    st.write("You entered:", user_input)

if __name__ == "__main__":
    main()
