
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from pathlib import Path

# Load dataset
project_folder = Path(__file__).resolve().parent
df = pd.read_csv(project_folder / "coffee_shops_clean.csv")

# Convert times to hours
df["Time Hour"] = pd.to_datetime(
    df["Time"], format="%I:%M %p"
).dt.hour

# Define time periods
def get_period(hour):
    if hour < 12:
        return "Morning"
    elif hour < 17:
        return "Afternoon"
    else:
        return "Evening"

df["Period"] = df["Time Hour"].apply(get_period)

shops = sorted(df["Coffee Shop"].unique())
hours = sorted(df["Time Hour"].unique())

# Calculate average people counted
all_data = df.pivot_table(
    index="Coffee Shop",
    columns="Time Hour",
    values="People Counted",
    aggfunc="mean"
).reindex(index=shops, columns=hours)

period_data = {}

for period in ["Morning", "Afternoon", "Evening"]:
    filtered = df[df["Period"] == period]

    pivot = filtered.pivot_table(
        index="Coffee Shop",
        columns="Time Hour",
        values="People Counted",
        aggfunc="mean"
    ).reindex(index=shops)

    period_data[period] = pivot

# Consistent color scale
color_max = all_data.max().max()

colorscale = [
    [0, "#D73027"],
    [0.5, "#FFFFBF"],
    [1, "#1A9850"]
]

def format_hours(hours):
    return [
        f"{hour % 12 or 12} {'AM' if hour < 12 else 'PM'}"
        for hour in hours
    ]

def make_trace(pivot):
    return go.Heatmap(
        x=format_hours(pivot.columns),
        y=shops,
        z=pivot.values,
        colorscale=colorscale,
        zmin=0,
        zmax=color_max,
        colorbar=dict(title="Average People Counted"),
        text=np.where(
            pivot.isna(),
            "",
            pivot.applymap(
                lambda value: f"{value:.1f}" if pd.notna(value) else ""
            ).values
        ),
        texttemplate="%{text}",
        textfont=dict(color="black", size=12),
        hovertemplate=(
            "Coffee Shop: %{y}<br>"
            "Time: %{x}<br>"
            "Average People: %{z:.1f}"
            "<extra></extra>"
        ),
        xgap=2,
        ygap=2
    )

fig = go.Figure()

fig.add_trace(make_trace(all_data))

buttons = [
    dict(
        label="All Day",
        method="update",
        args=[
            {
                "x": [format_hours(all_data.columns)],
                "z": [all_data.values],
                "text": [make_trace(all_data).text]
            },
            {"title": "Average Number of People by Coffee Shop and Time"}
        ]
    )
]

for period, pivot in period_data.items():
    pivot = pivot.dropna(axis=1, how="all")

    buttons.append(
        dict(
            label=period,
            method="update",
            args=[
                {
                    "x": [format_hours(pivot.columns)],
                    "z": [pivot.values],
                    "text": [make_trace(pivot).text]
                },
                {
                    "title": f"Average Number of People by Coffee Shop - {period}"
                }
            ]
        )
    )

fig.update_layout(
    title="Average Number of People by Coffee Shop and Time",
    xaxis_title="Time of Day",
    yaxis_title="Coffee Shop",
    updatemenus=[
        dict(
            buttons=buttons,
            direction="down",
            showactive=True,
            x=1,
            xanchor="right",
            y=1.2,
            yanchor="top"
        )
    ],
    height=550,
    margin=dict(t=120)
)

fig.write_html(
    project_folder / "interactive_heatmap.html",
    auto_open=True
)

print("Interactive heatmap created successfully!")
