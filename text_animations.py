import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.colors as mcolors

# Load the CSV file
data = pd.read_csv('./data/filtered_data3.csv')

#Select variables from the list
data = data[['Age', 'BIO_ExtinctionIntensity (%)', 'BIO_OriginationIntensity(%)', 
             'BIO_Difference_Cubic', 'SEA_Modern land sea level  (C = 176.6 106km2/km)',
             'TEM_GAT', 'TEM_dT', 'CO2_pCO2 (ppm)', 'O2_Mid O2%',
             'SR_87Sr/86Sr Mean', 'LIP_LIP_PDF', 'MAG_INT_mean', 'MAG_POL_FREQUENCY',
             'ZIR_Interpolated_mean_d18O', 'ZIR_Interpolated_mean_Hf']]

epochs = [[245, 235], [220, 210], [200, 190], [185, 175], [170, 160], [155, 145], [140, 130]]
quantities = [['BIO_ExtinctionIntensity (%)', 'BIO_OriginationIntensity(%)', 'BIO_Difference_Cubic'],
              ['SEA_Modern land sea level  (C = 176.6 106km2/km)', 'TEM_GAT', 'TEM_dT'],
              ['CO2_pCO2 (ppm)', 'O2_Mid O2%'],
              ['SR_87Sr/86Sr Mean'],
              ['LIP_LIP_PDF'],
              ['MAG_INT_mean', 'MAG_POL_FREQUENCY'],
              ['ZIR_Interpolated_mean_d18O', 'ZIR_Interpolated_mean_Hf']]

# Create a separate dataframe for opacity
opacity_data = pd.DataFrame(1.0, index=data.index, columns=[f"{col}_alpha" for col in data.columns[1:]])

# Update opacity values based on epochs and quantities
for epoch, quantity_group in zip(epochs, quantities):
    start, end = epoch
    for column in data.columns[1:]:
        alpha_column_name = f"{column}_alpha"
        if column in quantity_group:
            # Keep related quantities fully visible during the event
            opacity_data.loc[(data['Age'] <= start) & (data['Age'] >= end), alpha_column_name] = 1.0
        else:
            # Dim unrelated quantities during the event
            opacity_data.loc[(data['Age'] <= start) & (data['Age'] >= end), alpha_column_name] = 0.1
            
#smooth the opacity data
opacity_data = opacity_data.rolling(window=5, min_periods=1).mean() # Smooth the opacity data




# Ensure the data has the correct structure
if data.empty or len(data.columns) < 2:
    raise ValueError("The CSV file must have at least two columns: 'Age' and at least one value column.")

# Prepare the figure with a dark style
plt.style.use('dark_background')
fig, (ax_text, ax_plot) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [2, 2]})
ax_text.axis('off')  # Turn off the axes for the text area
ax_plot.set_xlabel('Age', color='white', fontfamily='monospace')
ax_plot.set_ylabel('Value', color='white', fontfamily='monospace')
ax_plot.grid(color='gray', linestyle='--', linewidth=0.5)

# Set tick parameters for dark mode
ax_plot.tick_params(colors='white', labelsize=8)
for label in ax_plot.get_xticklabels() + ax_plot.get_yticklabels():
    label.set_fontfamily('monospace')

# Initialize text objects and lines
text_objects = []
lines = []
spacing = 0.06
left_margin = 0
top_margin = 0.95

norm = mcolors.Normalize(vmin=0, vmax=len(data.columns) - 2)
def init():
    global text_objects, lines
    text_objects = []
    lines = []
    for i, column in enumerate(data.columns):
        if i == 0:
            color = 'white'  # Use white for 'Age'
        else:
        # Normalize the index to the range [0, 1] for the colormap
            color = plt.cm.viridis(norm(i - 1))  # Use normalized index for colormap
        text = ax_text.text(left_margin, top_margin - i * spacing, '', fontsize=7, fontfamily='monospace', color=color, transform=ax_text.transAxes)
        text_objects.append(text)
    
    # Create a line for each column except 'Age'
    for i, column in enumerate(data.columns[1:]):
        line, = ax_plot.plot([], [], lw=1, label=column, color=plt.cm.viridis(norm(i)))
        lines.append(line)
    
    ax_plot.set_xlim(252, 0)  # Set the x-axis range from 252 to 0
    return text_objects + lines

# Update function for animation
def update(frame):
    for i, column in enumerate(data.columns):
        if frame < len(data):
            text_objects[i].set_text(f"{column}: {round(data[column].iloc[frame], 2)}")
            if i > 0:  # Skip 'Age' column
                alpha_column_name = f"{column}_alpha"
                if alpha_column_name in opacity_data.columns and frame < len(opacity_data):
                    text_objects[i].set_alpha(opacity_data[alpha_column_name].iloc[frame])
        else:
            text_objects[i].set_text(f"{column}: N/A")
    
    # Update the line plots
    if 'Age' in data.columns and frame < len(data):
        x = data['Age'][:frame + 1]
        current_age = data['Age'].iloc[frame]
        
        # Check if the current age is within any of the epochs
        in_epoch = any(start >= current_age >= end for start, end in epochs)
        
        for i, column in enumerate(data.columns[1:]):
            y = data[column][:frame + 1]
            lines[i].set_data(x, y)
            
            # Apply the prepared alpha values from opacity_data
            alpha_column_name = f"{column}_alpha"
            if alpha_column_name in opacity_data.columns and frame < len(opacity_data):
                lines[i].set_alpha(opacity_data[alpha_column_name].iloc[frame])
        
        # Dynamically adjust the y-axis limits
        all_y_values = [data[column][:frame + 1] for column in data.columns[1:]]
        y_min = min([y.min() for y in all_y_values])
        y_max = max([y.max() for y in all_y_values])
        ax_plot.set_ylim(y_min, y_max)
    return text_objects + lines

# Create the animation
frames = len(data)
interval = 600 / frames  # Calculate interval for 1 minute duration
ani = FuncAnimation(fig, update, frames=frames, init_func=init, blit=True, interval=25)

# Show the animation
plt.tight_layout()
plt.show()
