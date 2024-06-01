#!/bin/bash

# Get the initial node name from the command-line argument
input_node=$(hostname)

# Create the node_file (overwriting if it exists)
output_file="node_file"

# Loop to generate the node names
for i in {0..4}; do
  # Perform text substitution, replacing the number in the input node
  node_name=$(echo "$input_node" | sed "s/[0-9]\+/$i/") 
  echo "$node_name" >> "$output_file"  # Append to the output file
done