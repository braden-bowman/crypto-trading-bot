import os

# Define the path to the problematic file
file_path = os.path.expanduser("~/.pyenv/versions/crypto-trading/lib/python3.10/site-packages/pandas_ta/momentum/squeeze_pro.py")

# Read the contents of the file
with open(file_path, 'r') as file:
    lines = file.readlines()

# Modify the incorrect import statement
new_lines = []
for line in lines:
    if 'from numpy import NaN as npNaN' in line:
        new_lines.append('from numpy import nan as npNaN\n')
    else:
        new_lines.append(line)

# Write the changes back to the file
with open(file_path, 'w') as file:
    file.writelines(new_lines)

print("Fixed the import issue in squeeze_pro.py")
