import streamlit as st
import subprocess

def run_nmap_scan(target):
    command = ["nmap", "-Pn", "-sV", target]  
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    output_placeholder = st.empty()  # Create a placeholder for dynamic updates

    for line in iter(process.stdout.readline, ''):
        output_placeholder.text(line.strip())  # Update the UI with each new line

    process.stdout.close()
    process.wait()
    return "Scan Complete!"

st.title("Automated Pentesting Tool")

target = st.text_input("Enter Target IP/Domain:")

if st.button("Run Nmap Scan"):
    if target:
        run_nmap_scan(target)
    else:
        st.error("Please enter a target IP/domain.")
