#!/bin/bash
echo "Starting Gasmet Gas Flux Analyzer..."
python3 gasmet_analyzer.py

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Failed to start application"
    echo ""
    echo "Possible solutions:"
    echo "1. Make sure Python 3 is installed"
    echo "2. Install required packages: pip3 install pandas numpy matplotlib scipy openpyxl"
    echo ""
    read -p "Press enter to continue"
fi
