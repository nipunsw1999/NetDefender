#!/bin/bash

# Function to install dependencies
install_dependencies() {
  echo "Installing required packages..."
  sudo apt update
  sudo apt install -y docker.io clamav clamav-daemon wget
  sudo systemctl start docker
  sudo systemctl enable docker

  echo "Updating ClamAV database..."
  sudo freshclam
}

# Ensure Docker and ClamAV are installed
install_dependencies

# Set a default known malware Docker image
MALWARE_IMAGE="nginx:latest"

# Pull the malware Docker image from a research repository
echo "Pulling malware Docker image: $MALWARE_IMAGE..."
docker pull $MALWARE_IMAGE

# Create a temporary container from the image
echo "Creating a temporary container from the image..."
docker create --name temp_container $MALWARE_IMAGE

# Export the container filesystem to a tarball
echo "Exporting the container filesystem..."
docker export temp_container -o /tmp/container_filesystem.tar

# Remove the temporary container
docker rm temp_container

# Extract the tarball
echo "Extracting the container filesystem..."
mkdir -p /tmp/extracted_files
tar -xf /tmp/container_filesystem.tar -C /tmp/extracted_files

# Scan the extracted files with ClamAV
echo "Scanning the extracted files for malware..."
SCAN_REPORT="/tmp/scan_report.txt"
clamscan -r /tmp/extracted_files | tee $SCAN_REPORT

# Generate a summary of the scan
echo "Scan Summary:"
grep -E "Infected files|FOUND" $SCAN_REPORT || echo "No malware found."

# Clean up extracted files and tarball
echo "Cleaning up temporary files..."
rm -rf /tmp/extracted_files /tmp/container_filesystem.tar

echo "Malware scanning completed!"
