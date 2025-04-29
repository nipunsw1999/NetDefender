#!/bin/bash

# Check for URL input
if [ -z "$1" ]; then
  echo "Usage: $0 <url>"
  echo "Please provide a URL to scan."
  exit 1
fi

# Define the URL to scan
URL=$1

# Generate a unique report filename based on timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_FILE="wapiti_report_${TIMESTAMP}.html"

# Generate the report (in HTML format)
echo "Running wapiti3 on URL: $URL"
wapiti -u $URL -f html -o $REPORT_FILE

# Check if the report was generated
if [ -f "$REPORT_FILE" ]; then
  echo "Report generated: $REPORT_FILE"
  # Open the report in the default browser
  xdg-open $REPORT_FILE
else
  echo "Failed to generate the report."
  exit 1
fi
