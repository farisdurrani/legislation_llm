# app.py
import streamlit as st
import requests
import json
import ast
import re


def query_llm(query):
    url = "https://us-east4-legistlation-llm.cloudfunctions.net/llm-backend"
    data = {"query": query}
    response = requests.post(
        url, data=json.dumps(data), headers={"Content-Type": "application/json"}
    ).json()
    return response["answer"], response["context"]


def main():
    st.title("Legislation LLM Scanner / Research Assistant")
    st.write(
        """
        The project aims to use NLP to build a ChatGPT-like chatbot, 
        where users can query about recent legislation and get a 
        summary of the bill. The chatbot would also be able to answer 
        questions about the bill, such as "What is the purpose of this bill?" 
        or "What is the impact of this bill?"
        
        Please find more information [here](https://devpost.com/software/legislation-llm).
        
        **Authors: [Nicholas Polimeni](https://www.linkedin.com/in/nickpolimeni/), 
        [Faris Durrani](https://www.linkedin.com/in/farisdurrani/), [Justin Singh](https://www.linkedin.com/in/justin-singh-/)**
        """
    )
    st.divider()
    st.subheader("Enter a query about US legislation")
    user_input = st.text_input("Input", label_visibility="hidden")

    if user_input:
        with st.spinner(
            "Please wait while we analyze thousands of documents (avg response time: 10 sec)..."
        ):
            answer, context = query_llm(user_input)
            context = [ast.literal_eval(item) for item in context]
            st.divider()
            st.subheader("Answer")
            st.write(answer)
            st.write("")
            st.subheader("Related Bills and Sections")
            for bill in context:
                for key, val in bill.items():
                    key = key.replace(".txt", "").upper()

                    exp = r"[^\w\n .()]+"
                    val = re.sub(exp, "", val)

                    with st.expander(f"BILL {key}"):
                        st.text(val)


if __name__ == "__main__":
    main()
