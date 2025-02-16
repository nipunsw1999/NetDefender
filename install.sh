#!/bin/bash

{
    sudo apt update -y > /dev/null 2>&1
    sudo apt install -y figlet > /dev/null 2>&1
    sudo apt install -y lolcat > /dev/null 2>&1
    sudo apt install -y nmap > /dev/null 2>&1
    sudo apt install -y clamav > /dev/null 2>&1
    sudo apt install -y clamav-daemon> /dev/null 2>&1
} &

echo -ne 'Installing... ['
for i in {1..100}; do
    clear
    echo "It will get few munites and wait until it is completed"
    echo "Installing... $i% Completed"
    sleep 0.05
done
echo -e "] Done!\n"

clear  

echo -e "\e[31m$(figlet NetDefender)\e[0m"
echo "Necessary packages installed successfully"