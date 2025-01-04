import pandas as pd

# Read the distance data from the file
df_distances = pd.read_excel('NBG branches coordinates results filled.xlsx', index_col=0)

# Read the duration data from the file
df_durations = pd.read_excel('NBG branches coordinates duration.xlsx', index_col=0)
df_durations.index = df_durations.index.astype(str)
df_durations.columns = df_durations.columns.astype(str)

# List of branches to exclude
exclude_branches = ['585', '515', '505']

df_distances = df_distances[~df_distances.index.isin(exclude_branches)]
df_durations = df_durations[~df_durations.index.isin(exclude_branches)]

df_distances = df_distances.loc[:, ~df_distances.columns.isin(exclude_branches)]
df_durations = df_durations.loc[:, ~df_durations.columns.isin(exclude_branches)]

# Initialize an empty dictionary to store the results
top_3_closest = {}

# Iterate over each branch
for branch in df_distances.index:
    # Get the distances for the current branch
    distances = df_distances.loc[branch]

    # Exclude 'Unavailable' values
    distances = distances[distances != 'Unavailable'].dropna()

    # Sort the distances and get the top 3 closest branches (excluding itself)
    closest_branches = distances.sort_values()[1:4]

    # Store the result
    top_3_closest[branch] = closest_branches

# Convert the results into a wide-format DataFrame
output_data = []
for branch, closest_branches in top_3_closest.items():
    row = {'Branch ID': branch}
    for i, (other_branch, distance) in enumerate(closest_branches.items(), start=1):
        # Get the duration for the closest branch
        duration = df_durations.loc[str(other_branch), str(branch)]
        # Replace NaN with 'Unavailable'
        if pd.isna(duration):
            duration = 'Unavailable'
        # Add columns for distance, closest branch, and duration
        row[f'Distance {i}'] = distance
        row[f'Closest Branch {i}'] = other_branch
        row[f'Duration {i}'] = duration
    output_data.append(row)

# Create the output DataFrame
output_df = pd.DataFrame(output_data)

# Save the output DataFrame to a CSV file
output_df.to_excel('top_3_closest_branches_wide_format.xlsx', index=False)

# Print the output DataFrame
print(output_df)