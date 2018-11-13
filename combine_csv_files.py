import csv, os, pandas as pd

#------------------Enter these parameters------------------
# Path to source video - find here: https://drive.google.com/open?id=0B7QqDexrxSfwVXgwWlRUcDBiVFk
source_folder = '/home/stephen/Desktop/data/'
# Path to source data - find here: https://drive.google.com/open?id=0B7QqDexrxSfwVXgwWlRUcDBiVFk
output_path = '/home/stephen/Desktop/ss60_id_151.csv'

# Get all the data
# Create a master list
data = []
# Iterate through each file in the folder
for path in os.listdir(source_folder):
    print(path)
    # Read the data into a data frame
    df = pd.read_csv(source_folder + path)
    # Add the data for the ball to the master list
    data.append(df.values)

# Find the shortest column
min_length = len(data[0])
for col in data:
    if len(col) < min_length: min_length = len(col)

# Create a list for the positions
positions = []
# Make a subList for each ball
for ball in range(len(data)*2): positions.append([])

# Iterate through each frame
for frame in range(min_length):
    ball_num = 0
    # Iterate through each ball
    for ball in data:
        # Add the position to the appropriate sub list in positions
        positions[ball_num*2].append(ball[frame][0])
        positions[ball_num*2+1].append(ball[frame][1])
        ball_num += 1
        
# Write data
with open(output_path, 'w') as csvfile:
    # Create a list of fieldnames based on the number of balls
    fieldnames = []
    ball_num = 0
    for ball in range(2*len(data)):
        fieldnames.append(str(ball_num))
        ball_num += 1
    # Create a writer to write data to file
    writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
    writer.writeheader()

    # Iterate though each frame
    for frame in range(min_length):
        ball_num = 0
        # Create a new row for this frame
        row = {}
        # Iterate through each ball
        while ball_num < len(data)*2:
            # Get the data for this coordinate component (x or y) of this ball
            ball = positions[ball_num]
            # Add the position of the ball in this frame to the row
            row[fieldnames[ball_num]] = ball[frame]
            # Increment ball number
            ball_num += 1
        writer.writerow(row)
