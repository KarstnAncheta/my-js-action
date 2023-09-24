import plotly.express as px
import pandas as pd
from datetime import date
from pathlib import Path
import os

DIRECTORY_SEPARATOR = os.path.sep


def create_gantt_chart(data_frame: pd.DataFrame, project_name: str) -> None:
    """
    This function takes a data frame and makes a chart showing the actual timeline.

    Args:
        data_frame: A Pandas DataFrame containing the Gantt chart data.
        project_name: The name of the project.

    Returns:
          None
    """
    # Create figure
    fig = px.timeline(
        data_frame,
        x_start="Date Started",
        x_end="Date Completed",
        y="List of features, fixes, chores, etc...",
        color="Module Label",
    )

    # Sorts y-axis properly from Date Started to Date Completed
    fig.update_yaxes(autorange="reversed")

    # Update layout
    fig.update_layout(
        title=dict(
            text=f"{project_name} timeline (actual)",
            font=dict(
                size=25,
            ),
            automargin=True,
            x=0.5
        ),
    )

    # Save the figure as an image
    date_today = date.today()
    directory_path = Path(f".{DIRECTORY_SEPARATOR}charts{DIRECTORY_SEPARATOR}{date_today}")

    # Creates the directory if it does not exist
    if not directory_path.exists():
        directory_path.mkdir(parents=True)

    # Save the image inside the directory
    fig.write_image(
        f"{directory_path}{DIRECTORY_SEPARATOR}{project_name}-{date_today}.png",
        width=1024,
        height=720
    )

    print("Successfully ran the script.")


def main():
    #  Read the TSV file into a data frame and parse the dates to conform to the proper format
    df = pd.read_table("egov-bebs.tsv", sep="\t", parse_dates=["Date Started", "Date Completed"])
    df_clone = df.copy()

    # Drop unneeded rows and columns
    df = df.drop(["URL"], axis=1)
    df = df[df["Status"] != "On Hold"]
    df = df[df["Status"] != "Todo P1"]
    df = df[df["Status"] != "Todo P2"]
    df = df[df["Status"] != "Todo P3"]
    df = df[df["Status"] != "Todo P4"]

    # Sort data frame by start date
    df = df.sort_values(by=["Date Started"])

    # Add a time difference to the completion date
    df["Date Completed"] = df["Date Completed"] + pd.Timedelta(hours=12)

    # Change description
    df["Title"] = df["Title"].str[:20] + "...".lower()
    df.rename(columns={"Title": "List of features, fixes, chores, etc..."}, inplace=True)

    # Create chart
    print("Starting the script...")
    create_gantt_chart(data_frame=df, project_name="egov-bebs")


if __name__ == "__main__":
    main()


