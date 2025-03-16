#!/bin/bash

# Set the time window and request threshold
TIME_WINDOW=60  # in seconds
THRESHOLD=10    # Max allowed requests before blocking

# How long the IP stays blocked
BLOCK_TIME=300  # in seconds (5 minutes)

# Log files for Apache & Nginx
NGINX_LOG="/var/log/nginx/access.log"
APACHE_LOG="/var/log/apache2/access.log"

# File to store blocked IPs
BLOCKED_IP_FILE="blocked_ip_addresses.txt"

# Get the server's IP address
HOST_IP=$(hostname -I | awk '{print $1}')
WHITELISTED_IPS=("127.0.0.1" "$HOST_IP" "YOUR_IP_HERE") # <-- Add your actual IP here

# Function to check if an IP is whitelisted
is_whitelisted() {
    local ip=$1
    for white_ip in "${WHITELISTED_IPS[@]}"; do
        if [[ "$ip" == "$white_ip" ]]; then
            return 0  # Whitelisted
        fi
    done
    return 1  # Not whitelisted
}

# Function to block an IP
block_ip() {
    local ip=$1

    if is_whitelisted "$ip"; then
        echo "Skipping whitelist IP: $ip"
        return
    fi

    echo "Blocking IP: $ip"
    sudo iptables -A INPUT -s "$ip" -j DROP
    echo "$ip" >> "$BLOCKED_IP_FILE"

    # Schedule automatic unblock
    (sleep $BLOCK_TIME && unblock_ip "$ip") &
}

# Function to unblock an IP
unblock_ip() {
    local ip=$1
    echo "Unblocking IP: $ip"
    sudo iptables -D INPUT -s "$ip" -j DROP
    sed -i "/^$ip$/d" "$BLOCKED_IP_FILE"
}

# Function to detect and block abusive IPs
detect_and_block_ips() {
    echo "Checking logs for abusive IPs..."

    for LOG_FILE in "$NGINX_LOG" "$APACHE_LOG"; do
        if [[ -f "$LOG_FILE" ]]; then
            awk '{print $1}' "$LOG_FILE" | sort | uniq -c | while read count ip; do
                if (( count > THRESHOLD )); then
                    block_ip "$ip"
                fi
            done
        fi
    done
}

# Run the script continuously
while true; do
    detect_and_block_ips
    sleep 60
done
