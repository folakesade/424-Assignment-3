
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load cleaned dataset
df = pd.read_csv("coffee_shops_clean.csv")

# Convert observation times into time periods
df["Time"] = pd.to_datetime(df["Time"], format="mixed")

def get_time_period(time):
    hour = time.hour

    if hour < 12:
        return "Morning"
    elif hour < 17:
        return "Afternoon"
    else:
        return "Evening"

df["Time Period"] = df["Time"].apply(get_time_period)

# Calculate average people counted for each shop and time period
heatmap_data = df.pivot_table(
    values="People Counted",
    index="Coffee Shop",
    columns="Time Period",
    aggfunc="mean"
)

# Set the order of time periods
heatmap_data = heatmap_data.reindex(
    columns=["Morning", "Afternoon", "Evening"]
)

# Create figure
fig, ax = plt.subplots(figsize=(9, 5))

# Create heat map
im = ax.imshow(
    heatmap_data,
    cmap="RdYlGn",
    aspect="auto",
    vmin=0,
    vmax=df["People Counted"].max()
)

# Add labels to axes
ax.set_xticks(range(len(heatmap_data.columns)))
ax.set_xticklabels(heatmap_data.columns)

ax.set_yticks(range(len(heatmap_data.index)))
ax.set_yticklabels(heatmap_data.index)

ax.set_xlabel("Time of Day")
ax.set_ylabel("Coffee Shop")
ax.set_title("Average Customer Activity by Coffee Shop and Time of Day")

# Add numerical values inside each cell
for i in range(len(heatmap_data.index)):
    for j in range(len(heatmap_data.columns)):
        value = heatmap_data.iloc[i, j]

        if pd.notna(value):
            ax.text(
                j, i,
                f"{value:.1f}",
                ha="center",
                va="center",
                color="black",
                fontsize=12
            )

# Add color bar
cbar = plt.colorbar(im, ax=ax)
cbar.set_label("Average Number of People")

plt.tight_layout()

# Save static visualization
plt.savefig("static_heatmap.png", dpi=300, bbox_inches="tight")

plt.show()
