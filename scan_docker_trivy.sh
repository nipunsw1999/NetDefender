#!/bin/bash

# Check if image name is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <image_name>:<tag>"
  exit 1
fi

# Define the Docker image
DOCKER_IMAGE=$1

# Update and install dependencies
echo "Installing required dependencies..."
sudo apt update && sudo apt install -y curl jq

# Install Docker if not installed
if ! command -v docker &> /dev/null; then
  echo "Docker not found. Installing Docker..."
  curl -fsSL https://get.docker.com | sudo bash
  sudo usermod -aG docker $USER
  newgrp docker
fi

# Install Trivy if not installed
if ! command -v trivy &> /dev/null; then
  echo "Trivy not found. Installing Trivy..."
  sudo apt install -y wget
  wget https://github.com/aquasecurity/trivy/releases/latest/download/trivy_0.51.1_Linux-64bit.tar.gz
  tar zxvf trivy_0.51.1_Linux-64bit.tar.gz
  sudo mv trivy /usr/local/bin/
  rm trivy_0.51.1_Linux-64bit.tar.gz
fi

# Ensure Docker daemon is running
echo "Checking Docker service status..."
sudo systemctl start docker
sudo systemctl enable docker

# Ensure the user has access to Docker daemon
sudo chmod 666 /var/run/docker.sock

# Pull the Docker image (downloads the image from Docker Hub)
echo "Pulling Docker image: $DOCKER_IMAGE..."
docker pull $DOCKER_IMAGE

# Check if docker pull was successful
if [ $? -ne 0 ]; then
  echo "Failed to pull the Docker image: $DOCKER_IMAGE"
  exit 1
fi

# Scan the Docker image for vulnerabilities using Trivy
echo "Scanning Docker image for HIGH and CRITICAL vulnerabilities: $DOCKER_IMAGE..."
trivy image --severity HIGH,CRITICAL --format json $DOCKER_IMAGE | jq '.' > scan_report.json

# Check if the scan was successful
if [ $? -ne 0 ]; then
  echo "Vulnerability scan failed for image: $DOCKER_IMAGE"
  exit 1
fi

# Display summary of HIGH and CRITICAL vulnerabilities
echo "Scan completed. Review 'scan_report.json' for details."
echo "Extracting summary..."
jq '[.Results[].Vulnerabilities[] | {VulnerabilityID, PkgName, InstalledVersion, Severity, Description}]' scan_report.json > high_critical_vulnerabilities.json

echo "Summary of HIGH and CRITICAL vulnerabilities saved to 'high_critical_vulnerabilities.json'"