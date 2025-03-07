import streamlit as st
import subprocess
import shutil
import time

# List of required packages
packages = ["figlet", "lolcat", "nmap", "clamav", "clamav-daemon"]

def is_installed(package):
    """Check if a package is already installed."""
    return shutil.which(package) is not None

def install_package(package, progress_bar, progress_value):
    """Install a package using apt and update the progress bar."""
    if is_installed(package):
        st.write(f"✅ {package} is already installed.")
    else:
        st.write(f"📦 Installing {package}...")
        subprocess.run(["sudo", "apt", "install", "-y", package], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    progress_value += 1
    progress_bar.progress(progress_value / len(packages))
    return progress_value

# Streamlit UI
st.title("NetDefender Installer")
st.subheader("Install Required Dependencies")

if st.button("Start Installation"):
    progress_bar = st.progress(0)
    progress_value = 0
    
    # Update package list
    st.write("🔄 Updating package list...")
    subprocess.run(["sudo", "apt", "update", "-y"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Install packages with progress
    for package in packages:
        progress_value = install_package(package, progress_bar, progress_value)
        time.sleep(0.5)  # Simulate progress
    
    st.success("🎉 All packages installed successfully!")
    
    # Display NetDefender banner
    st.write("🚀 Launching NetDefender...")
    banner = subprocess.run(["figlet", "NetDefender"], stdout=subprocess.PIPE, text=True)
    st.code(banner.stdout)

    st.balloons()
