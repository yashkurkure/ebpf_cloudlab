#!/bin/bash

echo "My PID is: $$"  # Print the script's Process ID

# Tell ebpf service to start recording counts
python3 client.py $$


make      # Compile the program
./hello   # Run the executable
make clean  # Clean up

# Tell ebpf service to stop recording counts
python3 client.py $$