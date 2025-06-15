import os
import pandas as pd
import subprocess
from collections import defaultdict

# Path to folder containing Excel files
folder_path = input("Enter the file directory: ")  # change this

# Dictionary to store votes by role -> candidate -> total_votes
vote_counter = defaultdict(lambda: defaultdict(int))

# Loop through all Excel files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith('.xlsx') or filename.endswith('.xls'):
        file_path = os.path.join(folder_path, filename)
        try:
            df = pd.read_excel(file_path)

            # Ensure expected columns exist
            if {'Role', 'Contestant', 'Votes'}.issubset(df.columns):
                for _, row in df.iterrows():
                    role = str(row['Role']).strip()
                    candidate = str(row['Contestant']).strip()
                    votes = int(row['Votes'])
                    vote_counter[role][candidate] += votes
            else:
                print(f"Skipping {filename}: Missing expected columns.")
        except Exception as e:
            print(f"Error reading {filename}: {e}")

# Prepare final output DataFrame
final_data = []

for role, candidates in vote_counter.items():
    final_data.append([role, '', ''])  # Blank row as header
    for candidate, total_votes in candidates.items():
        final_data.append([role, candidate, total_votes])

# Create DataFrame
final_df = pd.DataFrame(final_data, columns=['Role', 'Contestant', 'Total Votes'])

# Save to Final Count.xlsx
output_path = os.path.join(folder_path, 'Final Count.xlsx')
final_df.to_excel(output_path, index=False)
print(f"Final vote count saved to: {output_path}")

subprocess.Popen(f'explorer "{folder_path}"')
