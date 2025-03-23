import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import seaborn as sns
import numpy as np

# Load the CSV file
data = pd.read_csv('./data/filtered_data3.csv')

# Parameters for the sliding window
N = 50  # Length of the sliding window
step = 1  # Step size for the sliding window

# Ensure the data is numeric
data = data.select_dtypes(include=[np.number])

# Exclude the 'age' variable
if 'age' in data.columns:
    data = data.drop(columns=['age'])

# Set dark mode style
plt.style.use('dark_background')

# Create a figure for the animation
fig, ax = plt.subplots(figsize=(8, 6))

def update(frame):
    ax.clear()
    start = frame * step
    end = start + N
    if end > len(data):
        return  # Stop if the window exceeds the data length
    window_data = data.iloc[start:end]
    corr_matrix = window_data.corr()
    sns.heatmap(
        corr_matrix, 
        ax=ax,
        cbar=False,
        cmap="coolwarm", 
        annot=False,  # Set to True if you want numerical values displayed
        fmt=".2f", 
        linewidths=0.5, 
        vmin=-1, vmax=1,  # Ensure full correlation range is shown
        square=True,  # Keeps it visually uniform
        cbar_kws={"shrink": 0.8},  # Adjust colorbar size
    )
    ax.set_title(f"Correlation Matrix (Window: {start}-{end})", color='white')
    ax.tick_params(colors='white')  # Set tick colors to white

# Number of frames for the animation
num_frames = (len(data) - N) // step + 1

# Create the animation
ani = FuncAnimation(fig, update, frames=num_frames, interval=50)

# Show the animation
plt.show()
