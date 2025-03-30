import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd
import numpy as np

data_impacts = pd.read_csv('data\impakty.csv')

# Convert 'Age' and 'Diameter km' columns to numeric values
data_impacts['Age'] = data_impacts['Age'].str.replace(',', '.').astype(float)
data_impacts['Diameter km'] = data_impacts['Diameter km'].str.replace(',', '.').astype(float)

# Normalize the diameter to the maximum value
data_impacts['Normalized Diameter'] = data_impacts['Diameter km'] / data_impacts['Diameter km'].max()

# Create a figure and axis
fig, ax = plt.subplots(figsize=(10, 6))
ax.set_xlim(data_impacts['Age'].min() - 10, data_impacts['Age'].max() + 10)
ax.set_ylim(0, 1)
ax.set_xlabel('Age')
ax.set_ylabel('Random Y Position')
ax.set_title('Impact Animation')

# Generate random Y positions for each impact
data_impacts['Random Y'] = np.random.rand(len(data_impacts))

# Scatter plot for animation
sc = ax.scatter([], [], alpha=0.5)

# Update function for animation
def update(frame):
    current_data = data_impacts.iloc[:frame + 1]
    sc.set_offsets(np.c_[current_data['Age'], current_data['Random Y']])
    sc.set_sizes(current_data['Normalized Diameter'] * 1000)  # Scale sizes for better visibility
    return sc,

# Create the animation
ani = animation.FuncAnimation(fig, update, frames=len(data_impacts), interval=100, blit=True)

plt.show()