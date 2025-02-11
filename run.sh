#!/bin/bash

# Function to display a spinner while the Nmap scan is running
spinner() {
    local pid=$1
    local delay=0.1
    local spinstr='|/-\'
    while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
        local temp=${spinstr#?}
        printf " [%c] Scanning... " "$spinstr"
        local spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b"
    done
    printf "                    \b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b"
}

#Nmap scan
echo "Starting Nmap scan..."
timeout 30s nmap -p0- -v -A -T4 scanme.nmap.org > output.txt 2>&1 &
nmap_pid=$!

#Show spinner
spinner $nmap_pid &

wait $nmap_pid

#Stop spinner
kill $! 2>/dev/null

if [ $? -eq 0 ]; then
    echo -e "\nNmap scan completed."
else
    echo -e "\nNmap scan was interrupted or timed out."
fi