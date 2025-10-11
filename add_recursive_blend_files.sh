#!/bin/bash
find . -iname "*.blend" > blendfiles.txt

# Specify the path to your file
FILE="blendfiles.txt"

pwddir=$(pwd)

# Check if the file exists
if [ ! -f "$FILE" ]; then
    echo "Error: File '$FILE' not found."
    exit 1
fi

# Loop through each line of the file
while IFS= read -r line; do
    # Perform operations on each 'line'
    echo "Processing line: $line"
    blq -m anim --searchpath="$pwddir/$line"
    # Example: You can store the line in an array, perform text manipulation, etc.
    # my_array+=("$line")
done < "$FILE"
