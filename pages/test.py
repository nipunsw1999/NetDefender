import streamlit as st
import subprocess

def get_network_info():
    with st.spinner("Scanning network..."):
        try:
            result = subprocess.run(["nmap -sV -Pn csc.jfn.ac.lk"], capture_output=True, text=True, shell=True,timeout=30)
            return result.stdout if result.stdout else "Command failed or requires sudo."
        except Exception as e:
            return str(e)

st.write(get_network_info())

GROQ_API_KEY = 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