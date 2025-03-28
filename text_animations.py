import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.animation import FFMpegWriter
import matplotlib.colors as mcolors
import textwrap

# Load the CSV file
data = pd.read_csv('./data/filtered_data3.csv')
df_text = pd.read_csv('data/texts.csv')
#Select variables from the list
data = data[['Age', 'BIO_ExtinctionIntensity (%)', 'BIO_OriginationIntensity(%)', 
             'BIO_Difference_Cubic', 'SEA_Modern land sea level  (C = 176.6 106km2/km)',
             'TEM_GAT', 'TEM_dT', 'CO2_pCO2 (ppm)', 'O2_Mid O2%',
             'SR_87Sr/86Sr Mean', 'LIP_LIP_PDF', 'MAG_INT_mean', 'MAG_POL_FREQUENCY',
             'ZIR_Interpolated_mean_d18O', 'ZIR_Interpolated_mean_Hf']]

# Define events and quantities for each epoch and texts for each epoch

events = [[225,220],[210,205],[202,201]]
 
#define the quantities for each epoch   
quantities = [['BIO_ExtinctionIntensity (%)', 'BIO_OriginationIntensity(%)', 'BIO_Difference_Cubic'],
              ['SEA_Modern land sea level  (C = 176.6 106km2/km)', 'TEM_GAT', 'TEM_dT'],
              ['CO2_pCO2 (ppm)', 'O2_Mid O2%'],
              ['SR_87Sr/86Sr Mean'],
              ['LIP_LIP_PDF'],
              ['MAG_INT_mean', 'MAG_POL_FREQUENCY'],
              ['ZIR_Interpolated_mean_d18O', 'ZIR_Interpolated_mean_Hf']]

# Create a separate dataframe for opacity
maxwidth = 2.5
style_data = pd.DataFrame(1.0, index=data.index, columns=[f"{col}_alpha" for col in data.columns[1:]])
style_data = pd.concat([style_data, pd.DataFrame(0.1, index=data.index, columns=[f"{col}_alpha2" for col in data.columns[1:]])], axis=1)
style_data = pd.concat([style_data, pd.DataFrame(1.0, index=data.index, columns=[f"{col}_width" for col in data.columns[1:]])], axis=1)


# Update opacity values based on events and quantities
for epoch, quantity_group in zip(events, quantities):
    start, end = epoch
    for column in data.columns[1:]:
        alpha_column_name = f"{column}_alpha"
        alpha2_column_name = f"{column}_alpha2"
        width_column_name = f"{column}_width"
        if column in quantity_group:
            # Keep related quantities fully visible during the event
            style_data.loc[(data['Age'] <= start) & (data['Age'] >= end), alpha_column_name] = 1.0
            style_data.loc[(data['Age'] <= start) & (data['Age'] >= end), alpha2_column_name] = 1.0
            style_data.loc[(data['Age'] <= start) & (data['Age'] >= end), width_column_name] = maxwidth
        else:
            # Dim unrelated quantities during the event
            style_data.loc[(data['Age'] <= start) & (data['Age'] >= end), alpha_column_name] = 0.1
            style_data.loc[(data['Age'] <= start) & (data['Age'] >= end), alpha2_column_name] = 0.1
            
#smooth the opacity data
smoothness = 10
style_data = style_data.rolling(window=smoothness, min_periods=1).mean() # Smooth the opacity data

# Ensure the data has the correct structure
if data.empty or len(data.columns) < 2:
    raise ValueError("The CSV file must have at least two columns: 'Age' and at least one value column.")

# Prepare the figure with a dark style
plt.style.use('dark_background')
dpi = 100  # Dots per inch
width_in_pixels = 1920  # Desired width in pixels
height_in_pixels = 1080  # Desired height in pixels
fig, (ax_text, ax_plot) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [2, 2]},figsize=(width_in_pixels / dpi, height_in_pixels / dpi), dpi=dpi)
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
leftTitlePos = 0.5
topTitlePos = 0.95
box_width = 50  # Maximum number of characters per line

norm = mcolors.Normalize(vmin=0, vmax=len(data.columns) - 2)
def init():
    global text_objects, lines, lines2, lineT, text_title, event_text_box
    text_objects = []
    lines = []
    lines2 = []
    for i, column in enumerate(data.columns):
        if i == 0:
            color = 'white'  # Use white for 'Age'
        else:
        # Normalize the index to the range [0, 1] for the colormap
            color = plt.cm.tab20(norm(i - 1))  # Use normalized index for colormap
        text = ax_text.text(left_margin, top_margin - i * spacing, '', fontsize=7, fontfamily='monospace', color=color, transform=ax_text.transAxes)
        text_objects.append(text)
    
    # Create a line for each column except 'Age'
    for i, column in enumerate(data.columns[1:]):
        line, = ax_plot.plot([], [], lw=1, label=column, color=plt.cm.tab20(norm(i)))
        line2, = ax_plot.plot([], [], lw=1, label=column, color=plt.cm.tab20(norm(i)))
        lines.append(line)
        lines2.append(line2)
        line2.set_alpha(0.1)  # Set the alpha value for the second set of lines
        line2.set_data(data['Age'], data[column])  # Set the data for the second set of lines
    text_title = ax_text.text(leftTitlePos, topTitlePos, '', fontsize=12, fontfamily='monospace', color='white', transform=ax_text.transAxes)
    text_title.set_text('Trias')
    event_text_box = ax_text.text(0.5, 0.1, '', fontsize=10, color='white', fontfamily='monospace',
                                  bbox=dict(facecolor='black', alpha=0.7, boxstyle='round,pad=0.5'),
                                  transform=ax_text.transAxes, ha='center')
    lineT = ax_plot.axvline(x=0, color='grey', linewidth=1, linestyle='-')
    ax_plot.set_xlim(252, 0)  # Set the x-axis range from 252 to 0
    return text_objects + lines + lines2 + [lineT] + [text_title] + [event_text_box]    

# Update function for animation
def update(frame):
    for i, column in enumerate(data.columns):
        if frame < len(data):
            text_objects[i].set_text(f"{column}: {round(data[column].iloc[frame], 2)}")
            if i > 0:  # Skip 'Age' column
                alpha_column_name = f"{column}_alpha"
                if alpha_column_name in style_data.columns and frame < len(style_data):
                    text_objects[i].set_alpha(style_data[alpha_column_name].iloc[frame])
        else:
            text_objects[i].set_text(f"{column}: N/A")
    
    # Update the line plots
    if 'Age' in data.columns and frame < len(data):
        x = data['Age'][:frame + 1]
        current_age = data['Age'].iloc[frame]
        current_event = df_text['Event_text'].iloc[frame]
        current_event= "\n".join(textwrap.wrap(current_event, width=box_width))
        # Check if the current age is within any of the events
        in_epoch = any(start >= current_age >= end for start, end in events)
        
        for i, column in enumerate(data.columns[1:]):
            y = data[column][:frame + 1]
            lines[i].set_data(x, y)
            
            # Apply the prepared alpha values from style_data
            alpha_column_name = f"{column}_alpha"
            if alpha_column_name in style_data.columns and frame < len(style_data):
                lines[i].set_alpha(style_data[alpha_column_name].iloc[frame])
                lines2[i].set_alpha(style_data[f"{column}_alpha2"].iloc[frame])
                lines[i].set_linewidth(style_data[f"{column}_width"].iloc[frame])
        lineT.set_xdata([current_age, current_age])
        text_title.set_text(df_text['Title'].iloc[frame])
        #lineT.set_ydata([0, 1])  
        event_text_box.set_text(current_event)     
        # Dynamically adjust the y-axis limits
        all_y_values = [data[column][:frame + 1] for column in data.columns[1:]]
        y_min = min([y.min() for y in all_y_values])
        y_max = max([y.max() for y in all_y_values])
        ax_plot.set_ylim(y_min, y_max)
    return text_objects + lines + lines2 + [lineT] + [text_title] + [event_text_box]    

# Create the animation
frames = len(data)
frames = 1500
interval = 600 / frames  # Calculate interval for 1 minute duration
ani = FuncAnimation(fig, update, frames=frames, init_func=init, blit=True, interval=25)

# Export the animation to an MP4 file
# duration_seconds=4844
# fps = frames / duration_seconds # Calculate the frames per second
#writer = FFMpegWriter(fps=10, metadata=dict(artist='Me'), bitrate=2500)
#ani.save('./output/animation.mp4', writer=writer)

# Show the animation
plt.tight_layout()
plt.show()
