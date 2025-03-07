import streamlit as st
import os
import multiprocessing

st.title("NetDefender - Advanced Security Scanner")

# Function to perform Port Scanning using Nmap
def port_scan(target):
    output_file = "scan_result.txt"
    os.system(f"nmap -sV -Pn {target} -oN {output_file}")
    return output_file

# Function to search for exploits using searchsploit
def exploit_search(service):
    output_file = "exploits.txt"
    os.system(f"searchsploit {service} > {output_file}")
    return output_file

# Function to perform Vulnerability Scan using Nmap NSE
def vuln_scan(target):
    output_file = "vuln_scan.txt"
    os.system(f"nmap --script=vuln {target} -oN {output_file}")
    return output_file

# Function to enumerate subdomains using sublist3r
def subdomain_enum(target):
    output_file = "subdomains.txt"
    os.system(f"sublist3r -d {target} -o {output_file}")
    return output_file

# Function to run web directory brute-force attack using dirsearch
def web_dir_scan(target):
    output_file = "dir_scan.txt"
    os.system(f"dirsearch -u {target} --simple-report={output_file}")
    return output_file

# Function to perform Web Vulnerability Scanning using Nikto
def web_vuln_scan(target):
    output_file = "nikto_scan.txt"
    os.system(f"nikto -h {target} > {output_file}")
    return output_file

# Function to read scan results and display in Streamlit
def display_results(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return f.read()
    return "No results found."

# User input
target = st.text_input("Enter Target IP/Domain")
scan_button = st.button("Start Scan")

if scan_button and target:
    st.header("Scanning Target: " + target)
    
    # Run scans in parallel
    with st.spinner("Scanning in progress... Please wait!"):
        processes = {
            "Port Scan": multiprocessing.Process(target=port_scan, args=(target,)),
            "Vulnerability Scan": multiprocessing.Process(target=vuln_scan, args=(target,)),
            "Subdomain Enumeration": multiprocessing.Process(target=subdomain_enum, args=(target,)),
            "Web Directory Scan": multiprocessing.Process(target=web_dir_scan, args=(target,)),
            "Web Vulnerability Scan": multiprocessing.Process(target=web_vuln_scan, args=(target,))
        }
        
        # Start all processes
        for process in processes.values():
            process.start()
        
        # Wait for all processes to complete
        for process in processes.values():
            process.join()
    
    # Display results
    st.subheader("Scan Results")
    
    st.write("### 🔍 Port Scan Results")
    st.text(display_results("scan_result.txt"))
    
    st.write("### 🔍 Vulnerability Scan Results")
    st.text(display_results("vuln_scan.txt"))
    
    st.write("### 🔍 Subdomain Enumeration")
    st.text(display_results("subdomains.txt"))
    
    st.write("### 🔍 Web Directory Scan")
    st.text(display_results("dir_scan.txt"))
    
    st.write("### 🔍 Web Vulnerability Scan (Nikto)")
    st.text(display_results("nikto_scan.txt"))

    # Exploit Search
    st.write("### 🔥 Exploit Search")
    service = st.selectbox("Select Service", ["Web Server", "Database", "Mail Server"])
    exploit_file = exploit_search(service)
    st.text(display_results(exploit_file))

    # Download results
    st.subheader("Download Reports")
    for file in ["scan_result.txt", "vuln_scan.txt", "subdomains.txt", "dir_scan.txt", "nikto_scan.txt"]:
        if os.path.exists(file):
            with open(file, "rb") as f:
                st.download_button(f"Download {file}", f, file_name=file)