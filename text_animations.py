import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Load the CSV file
data = pd.read_csv('./data/filtered_data3.csv')

# Ensure the data has the correct structure
if data.empty or len(data.columns) < 2:
    raise ValueError("The CSV file must have at least two columns: 'Age' and at least one value column.")

# Prepare the figure with a dark style
plt.style.use('dark_background')
fig, (ax_text, ax_plot) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [2, 2]})
ax_text.axis('off')  # Turn off the axes for the text area
ax_plot.set_xlabel('Age')
ax_plot.set_ylabel('Value')
ax_plot.grid(color='gray', linestyle='--', linewidth=0.5)

# Initialize text objects and lines
text_objects = []
lines = []
spacing = 0.05
left_margin = 0
top_margin = 0.95

def init():
    global text_objects, lines
    text_objects = []
    lines = []
    for i, column in enumerate(data.columns):
        text = ax_text.text(left_margin, top_margin - i * spacing, '', fontsize=6.5, fontfamily='monospace', color='white', transform=ax_text.transAxes)
        text_objects.append(text)
    
    # Create a line for each column except 'Age'
    for column in data.columns[1:]:
        line, = ax_plot.plot([], [], lw=1, label=column)
        lines.append(line)
    
    ax_plot.set_xlim(252, 0)  # Set the x-axis range from 252 to 0
    #ax_plot.legend(loc='upper right', fontsize=6)
    return text_objects + lines

# Update function for animation
def update(frame):
    for i, column in enumerate(data.columns):
        if frame < len(data):
            text_objects[i].set_text(f"{column}: {round(data[column].iloc[frame], 2)}")      
        else:
            text_objects[i].set_text(f"{column}: N/A")
    
    # Update the line plots
    if 'Age' in data.columns and frame < len(data):
        x = data['Age'][:frame + 1]
        for i, column in enumerate(data.columns[1:]):
            y = data[column][:frame + 1]
            lines[i].set_data(x, y)
        
        # Dynamically adjust the y-axis limits
        all_y_values = [data[column][:frame + 1] for column in data.columns[1:]]
        y_min = min([y.min() for y in all_y_values])
        y_max = max([y.max() for y in all_y_values])
        ax_plot.set_ylim(y_min, y_max)
    return text_objects + lines

# Create the animation
frames = len(data)
interval = 600 / frames  # Calculate interval for 1 minute duration
ani = FuncAnimation(fig, update, frames=frames, init_func=init, blit=True, interval=interval)

# Show the animation
plt.tight_layout()
plt.show()