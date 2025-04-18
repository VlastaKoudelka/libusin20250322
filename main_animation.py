import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.animation import FFMpegWriter
import matplotlib.colors as mcolors
import textwrap
import numpy as np
import seaborn as sns

outputPath = 'C:/Users/Koudy/Documents/projects/4.5Ga/output/'
# Load the CSV file
data = pd.read_csv('./data/filtered_data3.csv')
df_text = pd.read_csv('data/texts.csv')
df_events = pd.read_csv('data\Events_textsV3.csv')
data_impacts = pd.read_csv('data\impakty.csv')

#Select variables from the list
data = data[['Age', 'BIO_ExtinctionIntensity (%)', 'BIO_OriginationIntensity(%)', 
             'BIO_Difference_Cubic', 'SEA_Modern land sea level  (C = 176.6 106km2/km)',
             'TEM_GAT', 'TEM_dT', 'CO2_pCO2 (ppm)', 'O2_Mid O2%',
             'SR_87Sr/86Sr Mean', 'LIP_LIP_PDF', 'MAG_INT_mean', 'MAG_POL_FREQUENCY',
             'ZIR_Interpolated_mean_d18O', 'ZIR_Interpolated_mean_Hf']]

columnsDict={
    'Age': 'Věk (Ma)',
    'BIO_ExtinctionIntensity (%)': 'Míra vymírání druhů',
    'BIO_OriginationIntensity(%)': 'Míra vzniku nových druhů',
    'BIO_Difference_Cubic': 'Počet druhů mořské fauny',
    'SEA_Modern land sea level  (C = 176.6 106km2/km)': 'Hladina moře oproti dnešku',
    'TEM_GAT': 'Globální průměrná teplota',
    'TEM_dT': 'Rozdíl teplot mezi rovníkem a póly',
    'CO2_pCO2 (ppm)': 'Koncentrace CO2 v atmosféře',
    'O2_Mid O2%': 'Koncentrace kyslíku v atmosféře',
    'SR_87Sr/86Sr Mean': 'Izotop stroncia v moř. usazeninách',
    'LIP_LIP_PDF': 'Rozsáhlé vulkanické oblasti',
    'MAG_INT_mean': 'Intensita magnetického pole Země',
    'MAG_POL_FREQUENCY': 'Frekvence změny magnetického pole',
    'ZIR_Interpolated_mean_d18O': 'Poměr izotopů kyslíku v zrnech zirkonu',
    'ZIR_Interpolated_mean_Hf': 'Poměr izotopů hafnia v zrnech zirkonu'
}

# Convert 'Age' and 'Diameter km' columns to numeric values
data_impacts['Age'] = data_impacts['Age'].str.replace(',', '.').astype(float)
data_impacts['Diameter km'] = data_impacts['Diameter km'].str.replace(',', '.').astype(float)

# Normalize the diameter to the maximum value
data_impacts['Normalized Diameter'] = data_impacts['Diameter km'] / data_impacts['Diameter km'].max()
# Generate random Y positions for each impact
data_impacts['Random Y'] = np.random.rand(len(data_impacts))

#select specific age
ageBegin  = 23.05
ageEnd = 0 
data = data[(data['Age'] >= ageEnd) & (data['Age'] <= ageBegin)]
data_impacts = data_impacts[(data_impacts['Age'] >= ageEnd) & (data_impacts['Age'] <= ageBegin)]

# Define events and quantities for each epoch and texts for each epoch
events = [[float(onset.replace(',', '.')), float(offset.replace(',', '.'))] for onset, offset in zip(df_events['Onset'], df_events['Offset'])]

#define the quantities for each epoch
quantities = [eval(row) if pd.notna(row) else [] for row in df_events['Quantities']]   


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
#2K 2048 × 1080; 4K 3840 × 2160; 8K 7680 × 4320
dpi = 100  # Dots per inch
width_in_pixels = 1920  # Desired width in pixels
height_in_pixels = 1080  # Desired height in pixels
fig, (ax_text, ax_plot) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [2, 2]},figsize=(width_in_pixels / dpi, height_in_pixels / dpi), dpi=dpi)
fig.subplots_adjust(left=0.05, right=0.95, top=0.98, bottom=0.07)
ax_text.axis('off')  # Turn off the axes for the text area
ax_plot.set_xlabel('Věk (Ma)', color='white', fontfamily='monospace', fontsize=12)
ax_plot.set_ylabel('Normalizovaná hodnota', color='white', fontfamily='monospace', fontsize=12)
ax_plot.grid(color='gray', linestyle='--', linewidth=0.5)


# Set tick parameters for dark mode
ax_plot.tick_params(colors='white', labelsize=12)
for label in ax_plot.get_xticklabels() + ax_plot.get_yticklabels():
    label.set_fontfamily('monospace')

# Initialize text objects and lines
text_objects = []
lines = []
spacing = 0.065
left_margin = 0
top_margin = 0.90
leftTitlePos = 0.475
topTitlePos = 0.95
box_width = 45  # Maximum number of characters per line

norm = mcolors.Normalize(vmin=0, vmax=len(data.columns) - 2)
def init():
    global text_objects, lines, lines2, lineT, text_title, event_text_box, current_title, sc
    text_objects = []
    lines = []
    lines2 = []
    for i, column in enumerate(data.columns):
        if i == 0:
            color = 'white'  # Use white for 'Age'
        else:
        # Normalize the index to the range [0, 1] for the colormap
            color = plt.cm.tab20(norm(i - 1))  # Use normalized index for colormap
        text = ax_text.text(left_margin, top_margin - i * spacing, '', fontsize=15, fontfamily='monospace', color=color, transform=ax_text.transAxes)
        text_objects.append(text)
    
    # Create a line for each column except 'Age'
    for i, column in enumerate(data.columns[1:]):
        line, = ax_plot.plot([], [], lw=1, label=column, color=plt.cm.tab20(norm(i)))
        line2, = ax_plot.plot([], [], lw=1, label=column, color=plt.cm.tab20(norm(i)))
        lines.append(line)
        lines2.append(line2)
        line2.set_alpha(0.1)  # Set the alpha value for the second set of lines
        line2.set_data(data['Age'], data[column])  # Set the data for the second set of lines
    text_title = ax_text.text(leftTitlePos, topTitlePos, '', fontsize=18, fontfamily='monospace', color='white', transform=ax_text.transAxes)
    current_title = ' '
    text_title.set_text(current_title)
    event_text_box = ax_text.text(0.5, 0.1, '', fontsize=14, color='white', fontfamily='monospace',
                                  bbox=dict(facecolor='black', alpha=0.7, boxstyle='round,pad=0.5'),
                                  transform=ax_text.transAxes, ha='center')
    lineT = ax_plot.axvline(x=0, color='grey', linewidth=1, linestyle='-')
    ax_plot.set_xlim(ageBegin, ageEnd)  # Set the x-axis
    ax_plot.set_ylim(0, 1.0)  # Set the y-axis limits
    sc = ax_plot.scatter([], [], alpha=0.5,color='cyan')    

    # Add a legend for size representation
    legend_sizes = [0.192]  # Example normalized sizes
    legend_labels = [f'{size * data_impacts["Diameter km"].max():.1f} km' for size in legend_sizes]
    legend_handles = [
        plt.scatter([], [], s=size * 1000, alpha=0.5, label=label, color='cyan')
        for size, label in zip(legend_sizes, legend_labels)
    ]
    #ax_text.legend(handles=legend_handles, title="Dopady planetek (velikost kráteru)", loc="lower right", fontsize=14, facecolor='black', edgecolor='white', framealpha=0, prop={'family': 'monospace'}, title_fontproperties={'family': 'monospace'})
    ax_text.legend(
    handles=legend_handles,
    title="Dopady planetek (velikost kráteru)",
    loc="lower left",  # Keep the anchor point in the lower right
    bbox_to_anchor=(left_margin, -0.2),  # Move the legend lower (x=1, y=-0.1)
    fontsize=18,
    facecolor='black',
    edgecolor='white',
    framealpha=0,
    prop={'family': 'monospace',  'size': 15},
    title_fontproperties={'family': 'monospace', 'size': 15}
    )
    return text_objects + lines + lines2 + [lineT] + [text_title] + [event_text_box] + [sc]   

# Update function for animation
def update(frame):
    global current_title
    for i, column in enumerate(data.columns):
        if frame < len(data):
            text_objects[i].set_text(f"{columnsDict[column]}: {round(data[column].iloc[frame], 2)}")
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
        # Check if the current age is within any of the events
        epoch_index = next((i for i, (start, end) in enumerate(events) if start >= current_age >= end), None)
        if epoch_index is not None:
            current_title = df_events['Title'].iloc[epoch_index]
            current_event = df_events['Text'].iloc[epoch_index]
            current_event= "\n".join(textwrap.wrap(current_event, width=box_width))
        else:
            current_event = ''

        
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
        text_title.set_text(current_title)
        #lineT.set_ydata([0, 1])  
        event_text_box.set_text(current_event)     
        #update the scatter plot for impacts
        current_data = data_impacts[data_impacts['Age'] >= current_age]
        sc.set_offsets(np.c_[current_data['Age'], current_data['Random Y']])
        sc.set_sizes(current_data['Normalized Diameter'] * 1000)  # Scale sizes for better visibility
    return text_objects + lines + lines2 + [lineT] + [text_title] + [event_text_box] + [sc]

# Create the animation
frames = len(data)
#frames = 5041
#frames = 10
interval = 600 / frames  # Calculate interval for 1 minute duration
ani = FuncAnimation(fig, update, frames=frames, init_func=init, blit=True, interval=25)

# Export the animation to an MP4 file
duration_seconds=4842
duration_seconds = 30
fps = frames / duration_seconds # Calculate the frames per second
writer = FFMpegWriter(fps=fps, metadata=dict(artist='Me'), bitrate=5000)
ani.save('./output/NEOGEN.mp4', writer=writer)
#ani.save(outputPath + '252MaFullHDWarp45v2.mp4', writer=writer)

# Show the animation
plt.tight_layout()
plt.show()
