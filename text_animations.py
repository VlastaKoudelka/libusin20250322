import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Load the CSV file
data = pd.read_csv('./data/filtered_data3.csv')

# Ensure the data has the correct structure
if data.empty or len(data.columns) < 2:
    raise ValueError("The CSV file must have at least two columns with data.")

# Prepare the figure with a dark style
plt.style.use('dark_background')
fig, ax = plt.subplots()
ax.axis('off')  # Turn off the axes

# Initialize text objects
text_objects = []
spacing = 0.04
def init():
    global text_objects
    text_objects = []
    for i, column in enumerate(data.columns):
        text = ax.text(0.1, 0.9 - i * spacing, '', fontsize=8, fontfamily='monospace', color='white', transform=ax.transAxes)
        text_objects.append(text)
    return text_objects

# Update function for animation
def update(frame):
    for i, column in enumerate(data.columns):
        if frame < len(data):
            text_objects[i].set_text(f"{column}: {round(data[column].iloc[frame], 2)}")      
        else:
            text_objects[i].set_text(f"{column}: N/A")
    return text_objects

# Create the animation
frames = len(data)
interval = 60000 / frames  # Calculate interval for 1 minute duration
ani = FuncAnimation(fig, update, frames=frames, init_func=init, blit=True, interval=interval)

# Show the animation
plt.show()