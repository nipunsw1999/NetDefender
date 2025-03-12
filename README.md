# Docker Image Vulnerability Scanner

This script scans Docker images for vulnerabilities using Trivy and generates a report of high and critical vulnerabilities.

## Prerequisites

- Docker
- Trivy
- jq

## Installation

1. **Install Docker**: Follow the instructions on the [Docker website](https://docs.docker.com/get-docker/) to install Docker on your system.

2. **Install Trivy**: Follow the instructions on the [Trivy GitHub page](https://github.com/aquasecurity/trivy) to install Trivy on your system.

3. **Install jq**: You can install jq using the following command:

    ```sh
    sudo apt-get install jq
    ```

## Usage

1. **Run the script**: Replace `<image_name>:<tag>` with the name and tag of the Docker image you want to scan.

    ```sh
    ./scan_docker_trivy.sh <image_name>:<tag>
    ```

## Script Details

### Check if Image Name is Provided

The script starts by checking if an image name is provided as an argument. If not, it displays a usage message and exits.

```bash
if [ -z "$1" ]; then
  echo "Usage: $0 <image_name>:<tag>"
  exit 1
fi
```

### Define the Docker Image

The script assigns the provided image name to the `DOCKER_IMAGE` variable.

```bash
DOCKER_IMAGE=$1
```

### Update and Install Dependencies

The script updates the package list and installs `curl` and `jq`.

```bash
sudo apt update && sudo apt install -y curl jq
```

### Install Docker if Not Installed

The script checks if Docker is installed. If not, it installs Docker and adds the current user to the Docker group.

```bash
if ! command -v docker &> /dev/null; then
  echo "Docker not found. Installing Docker..."
  curl -fsSL https://get.docker.com | sudo bash
  sudo usermod -aG docker $USER
  newgrp docker
fi
```

### Install Trivy if Not Installed

The script checks if Trivy is installed. If not, it installs Trivy.

```bash
if ! command -v trivy &> /dev/null; then
  echo "Trivy not found. Installing Trivy..."
  sudo apt install -y wget
  wget https://github.com/aquasecurity/trivy/releases/latest/download/trivy_0.51.1_Linux-64bit.tar.gz
  tar zxvf trivy_0.51.1_Linux-64bit.tar.gz
  sudo mv trivy /usr/local/bin/
  rm trivy_0.51.1_Linux-64bit.tar.gz
fi
```

### Ensure Docker Daemon is Running

The script starts and enables the Docker service.

```bash
echo "Checking Docker service status..."
sudo systemctl start docker
sudo systemctl enable docker
```

### Ensure User Access to Docker Daemon

The script grants the current user access to the Docker daemon.

```bash
sudo chmod 666 /var/run/docker.sock
```

### Pull the Docker Image

The script pulls the specified Docker image from Docker Hub.

```bash
echo "Pulling Docker image: $DOCKER_IMAGE..."
docker pull $DOCKER_IMAGE
```

### Check if Docker Pull was Successful

The script checks if the Docker image was pulled successfully. If not, it exits with an error message.

```bash
if [ $? -ne 0 ]; then
  echo "Failed to pull the Docker image: $DOCKER_IMAGE"
  exit 1
fi
```

### Scan the Docker Image for Vulnerabilities

The script scans the Docker image for high and critical vulnerabilities using Trivy and saves the output to `scan_report.json`.

```bash
echo "Scanning Docker image for HIGH and CRITICAL vulnerabilities: $DOCKER_IMAGE..."
trivy image --severity HIGH,CRITICAL --format json $DOCKER_IMAGE | jq '.' > scan_report.json
```

### Check if the Scan was Successful

The script checks if the vulnerability scan was successful. If not, it exits with an error message.

```bash
if [ $? -ne 0 ]; then
  echo "Vulnerability scan failed for image: $DOCKER_IMAGE"
  exit 1
fi
```

### Extract Summary of High and Critical Vulnerabilities

The script extracts a summary of high and critical vulnerabilities from the scan report and saves it to `high_critical_vulnerabilities.json`.

```bash
echo "Extracting summary..."
jq '[.Results[].Vulnerabilities[] | {VulnerabilityID, PkgName, InstalledVersion, Severity, Description}]' scan_report.json > high_critical_vulnerabilities.json
```

### Display Completion Message

The script displays a message indicating that the scan is complete and the summary is saved.

```bash
echo "Summary of HIGH and CRITICAL vulnerabilities saved to 'high_critical_vulnerabilities.json'"
```

## Example

To scan the `nginx:latest` Docker image:

1. Run the script:

    ```sh
    ./scan_docker_trivy.sh nginx:latest
    ```

2. Review the scan report in `scan_report.json` and the summary in `high_critical_vulnerabilities.json`.

## License

This project is licensed under the MIT License.