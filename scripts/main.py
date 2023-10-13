"""
 __  __     ______     ______     ______     ______   __   __     ______
/\ \/ /    /\  __ \   /\  == \   /\  ___\   /\__  _\ /\ "-.\ \   /\  ___\
\ \  _"-.  \ \  __ \  \ \  __<   \ \___  \  \/_/\ \/ \ \ \-.  \  \ \___  \
 \ \_\ \_\  \ \_\ \_\  \ \_\ \_\  \/\_____\    \ \_\  \ \_\\"\_\  \/\_____\
  \/_/\/_/   \/_/\/_/   \/_/ /_/   \/_____/     \/_/   \/_/ \/_/   \/_____/

 ______     ______     ______   ______     ______     ______   ______
/\  == \   /\  ___\   /\  == \ /\  __ \   /\  == \   /\__  _\ /\  ___\
\ \  __<   \ \  __\   \ \  _-/ \ \ \/\ \  \ \  __<   \/_/\ \/ \ \___  \
 \ \_\ \_\  \ \_____\  \ \_\    \ \_____\  \ \_\ \_\    \ \_\  \/\_____\
  \/_/ /_/   \/_____/   \/_/     \/_____/   \/_/ /_/     \/_/   \/_____/
         ______     ______     ______     __     ______   ______
        /\  ___\   /\  ___\   /\  == \   /\ \   /\  == \ /\__  _\
        \ \___  \  \ \ \____  \ \  __<   \ \ \  \ \  _-/ \/_/\ \/
         \/\_____\  \ \_____\  \ \_\ \_\  \ \_\  \ \_\      \ \_\
          \/_____/   \/_____/   \/_/ /_/   \/_/   \/_/       \/_/

Simple script that reads file from GitHub Projects and outputs the following:
 - Figure of the actual timeline of the project in .png format.
 - Statistics of system's progress in .csv format.
"""
import os
import shutil
import math
from pathlib import Path
from datetime import date
import pandas as pd
import plotly.express as px

PROJECT_NAME = 'egov-bebs'
DIRECTORY_SEPARATOR = os.path.sep


def generate_project_actual_timeline_as_img(data_frame: pd.DataFrame, project_name: str) -> None:
    """
    This function takes a data frame, processes it, makes a chart showing the actual timeline and saves it.

    :param data_frame: a Pandas DataFrame containing project data.
    :param project_name: The name of the project.
    :return: None
    """
    # Drop unneeded rows and columns
    data_frame = data_frame.drop(["URL"], axis=1)
    data_frame = data_frame[data_frame["Status"] != "On Hold"]
    data_frame = data_frame[data_frame["Status"] != "Todo P1"]
    data_frame = data_frame[data_frame["Status"] != "Todo P2"]
    data_frame = data_frame[data_frame["Status"] != "Todo P3"]
    data_frame = data_frame[data_frame["Status"] != "Todo P4"]

    # Sort data frame by start date
    data_frame = data_frame.sort_values(by=["Date Started"])

    # Add a time difference to the completion date
    data_frame["Date Completed"] = data_frame["Date Completed"] + pd.Timedelta(hours=12)

    # Change description
    data_frame["Title"] = data_frame["Title"].str[:20] + "...".lower()
    data_frame.rename(columns={"Title": "List of features, fixes, chores, etc..."}, inplace=True)

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

    # Creates the directory if it does not exist
    date_today = date.today()
    directory_path = Path(f".{DIRECTORY_SEPARATOR}charts{DIRECTORY_SEPARATOR}{date_today}")

    if not directory_path.exists():
        directory_path.mkdir(parents=True)

    # Save the image inside the directory
    fig.write_image(
        f"{directory_path}{DIRECTORY_SEPARATOR}{project_name}-actual.png",
        width=1024,
        height=720
    )

    # Copy the original file into the folder for viewing purposes
    shutil.copyfile('egov-bebs.tsv', f"{directory_path}{DIRECTORY_SEPARATOR}{project_name}.tsv")


def generate_project_projected_timeline_as_img(data_frame: pd.DataFrame, project_name: str) -> None:
    """
    This function takes a data frame, processes it, makes a chart showing the projected timeline and saves it.

    :param data_frame: a Pandas DataFrame containing project data.
    :param project_name: The name of the project.
    :return: None
    """

    # Have MVP as the first index
    sorted_list = sorted(data_frame["Module Label"].unique(), key=lambda e: (e != "mvp", e))

    # Process the data frame with estimates based on the story points into a json
    json_data = []

    for module in sorted_list:
        module_rows = data_frame[data_frame["Module Label"] == module]
        module_story_points_sum = module_rows["Story Points"].sum()
        earliest_module_start_date = module_rows["Date Started"].min()
        hours_to_working_days = math.ceil(module_story_points_sum / 8)
        rest_days = math.ceil(hours_to_working_days / 22) * 8
        estimated_end_date = earliest_module_start_date + pd.Timedelta(days=hours_to_working_days + rest_days)

        json_data.append(
            {
                "Module": module,
                "Start Date": earliest_module_start_date,
                "End Date": estimated_end_date,
            }
        )

    new_data_frame = pd.DataFrame(json_data)
    print(new_data_frame)

    # Create figure
    fig = px.timeline(
        new_data_frame,
        x_start="Start Date",
        x_end="End Date",
        y="Module",
        color="Module",
    )

    # Update layout
    fig.update_layout(
        title=dict(
            text=f"{project_name} timeline (projected)",
            font=dict(
                size=25,
            ),
            automargin=True,
            x=0.5
        ),
    )

    # Creates the directory if it does not exist
    date_today = date.today()
    directory_path = Path(f".{DIRECTORY_SEPARATOR}charts{DIRECTORY_SEPARATOR}{date_today}")

    if not directory_path.exists():
        directory_path.mkdir(parents=True)

    # Save the image inside the directory
    fig.write_image(
        f"{directory_path}{DIRECTORY_SEPARATOR}{project_name}-projected.png",
        width=1024,
        height=720
    )


def generate_project_statistics(data_frame: pd.DataFrame, project_name: str) -> None:
    """
    Generates and prints out simple statistics for a project.

    :param project_name: name of the project.
    :param data_frame: a Pandas DataFrame containing project data.
    :return: None
    """

    # Generate simple statistics
    tasks_archived_old = len(data_frame[data_frame['Status'] == 'Archived - Old'])
    tasks_archived_new = len(data_frame[data_frame['Status'] == 'Archived - New'])
    tasks_done = len(data_frame[data_frame['Status'] == 'Done'])
    tasks_on_hold = len(data_frame[data_frame['Status'] == 'On Hold'])
    tasks_in_progress = len(data_frame[data_frame['Status'] == 'In Progress'])
    tasks_p1 = len(data_frame[data_frame['Status'] == 'Todo P1'])
    tasks_p2 = len(data_frame[data_frame['Status'] == 'Todo P2'])
    tasks_p3 = len(data_frame[data_frame['Status'] == 'Todo P3'])
    tasks_total = tasks_archived_old + tasks_archived_new + tasks_done + tasks_on_hold + tasks_p1 + tasks_p2 + tasks_p3
    completion_percentage = (tasks_archived_old + tasks_archived_new + tasks_done) / tasks_total

    data_frame_csv = pd.DataFrame(
        {
            'Low priority tasks': [tasks_p3],
            'Moderate priority tasks': [tasks_p2],
            'High priority tasks': [tasks_p1],
            'Tasks on hold': [tasks_on_hold],
            'Tasks in progress': [tasks_in_progress],
            'Tasks done': [tasks_archived_old + tasks_archived_new + tasks_done],
            'Total tasks': [tasks_total],
            'Completion %': [f'{completion_percentage:.0%} Complete']
        },
    )

    # Creates the directory if it does not exist
    date_today = date.today()
    directory_path = Path(f".{DIRECTORY_SEPARATOR}charts{DIRECTORY_SEPARATOR}{date_today}")

    if not directory_path.exists():
        directory_path.mkdir(parents=True)

    data_frame_csv.to_csv(f'{directory_path}{DIRECTORY_SEPARATOR}{project_name}-statistics.csv', index=False)


def main() -> None:
    """
    Main method.

    :return: None
    """

    #  Read the TSV file into a data frame and parse the dates to conform to the proper format
    df = pd.read_table(
        "egov-bebs.tsv",  # Replace with your project
        sep="\t",
        parse_dates=["Date Started", "Date Completed"]
    )

    # Save timeline as image
    generate_project_actual_timeline_as_img(data_frame=df, project_name=PROJECT_NAME)

    # Create project statistics
    generate_project_statistics(data_frame=df, project_name=PROJECT_NAME)

    generate_project_projected_timeline_as_img(data_frame=df, project_name=PROJECT_NAME)


if __name__ == '__main__':
    main()
