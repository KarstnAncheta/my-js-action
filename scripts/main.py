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

Simple script that reads a file from GitHub Projects and outputs the following:
 - Projected timeline in .png format.
 - Actual timeline in .png format.
 - Simple statistics of system's progress in .csv format.
 - Accomplishment Report.
"""
import os
import shutil
import math
from pathlib import Path
from datetime import date, datetime
import calendar
import pandas as pd
import plotly.express as px
from docxtpl import DocxTemplate, InlineImage

PROJECT_NAME = 'eGov-BEBS'
PROJECT_TSV_FILE_PATH = 'egov-bebs.tsv'
PROJECT_DETAILS = 'To design, build, test, and deploy a system for the Budgeting Office that will digitize a part of their current process.'
DEVELOPER_DETAILS = {
    'name': 'Karstn Paul P. Ancheta',
    'position': 'Information Systems Analyst I',
    'date_hired': datetime(2023, 1, 16)
}
RENDER_DATES = [
    datetime(2023, 10, 21)
]
REVIEWER_DETAILS = {
    'name': 'Patrick V. Vinluan',
    'position': 'Information Systems Analyst III',
}
DIRECTORY_SEPARATOR = os.path.sep


def generate_accomplishment_report(data_frame: pd.DataFrame, project_name: str) -> None:
    """
    Generates Accomplishment Report by getting data from the project's tsv file.

    :param data_frame:
    :param project_name:
    :return:
    """

    def get_cutoff_period():
        # Get the current date
        current_date = datetime.now()

        # Determine the first day of the current month
        first_day_of_month = current_date.replace(day=1)

        # Determine the last day of the current month
        last_day_of_month = calendar.monthrange(current_date.year, current_date.month)[1]

        # Determine the cutoff period based on the current date
        if current_date.day <= 15:
            cutoff_start = first_day_of_month.strftime("%Y-%m-01")
            cutoff_end = first_day_of_month.strftime("%Y-%m-15")
        else:
            cutoff_start = first_day_of_month.strftime("%Y-%m-16")
            cutoff_end = first_day_of_month.replace(day=last_day_of_month).strftime("%Y-%m-%d")

        return f"{cutoff_start} to {cutoff_end}"

    def calculate_cutoffs(start_date, current_date):
        cutoffs = 0
        # Calculate complete months between start_date and current_date
        complete_months = (current_date.year - start_date.year) * 12 + current_date.month - start_date.month

        # Count the number of cutoffs in complete months
        cutoffs += complete_months * 2

        # Check if the start_date and current_date are within the same month
        if start_date.day <= 15 and current_date.day > 15:
            cutoffs += 1
        elif start_date.day > 15 and current_date.day > 15:
            cutoffs += 1

        return cutoffs

    # Get the current date and time
    current_datetime = datetime.now()

    # Extract year, month, and day from the current date
    current_year = current_datetime.year
    current_month = current_datetime.month
    current_day = current_datetime.day

    # Create a datetime object with the extracted year, month, and day
    formatted_datetime = datetime(current_year, current_month, current_day)

    # Drop unnecessary columns
    data_frame = data_frame.drop([
        'URL',
        'Story Points',
        'Labels',
        'Priority Level',
    ], axis=1)

    # Get tasks under the "In Progress" and "Done" column
    tasks = data_frame[(data_frame['Status'].isin(['In Progress', 'Done']))]

    rendered_tasks = data_frame[(data_frame['Date Started'] <= RENDER_DATES[0]) & (data_frame['Date Completed'] >= RENDER_DATES[0])]

    # Exclude tasks within the RENDER_DATES timeframe from tasks DataFrame
    tasks = tasks[~tasks.index.isin(rendered_tasks.index)]

    # DOCUMENT TEMPLATE
    doc = DocxTemplate('AR-template.docx')

    # Specify the directory containing the images
    directory_path = "screenshots"

    # Get a list of all files in the directory
    all_files = os.listdir(directory_path)

    # Filter out image files (you can extend the list of allowed extensions)
    image_files = [file for file in all_files if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

    # Process each image file
    image_data_array = []
    for image_file in image_files:
        image_path = os.path.join(directory_path, image_file)
        image_data = InlineImage(doc, image_path, width=512 * 9525, height=320 * 9525)  # EMU calculations
        image_data_array.append(image_data)

    data = {
        'project_name': project_name,
        'project_objectives': PROJECT_DETAILS,
        'developer_name': DEVELOPER_DETAILS['name'],
        'developer_position': DEVELOPER_DETAILS['position'],
        'reviewer_name': REVIEWER_DETAILS['name'],
        'reviewer_position': REVIEWER_DETAILS['position'],
        'cutoff_dates': get_cutoff_period(),
        'tc': calculate_cutoffs(DEVELOPER_DETAILS['date_hired'], formatted_datetime),
        'modules': tasks['Module Label'].unique(),
        "image_data_array": image_data_array,
        'tasks': [{key.replace(' ', '_'): value for key, value in record.items()} for record in tasks.to_dict(orient='records')],
        'rendered_tasks': [{key.replace(' ', '_'): value for key, value in record.items()} for record in rendered_tasks.to_dict(orient='records')]
    }
    doc.render(data)

    # print(data['tasks'])

    # Creates the directory if it does not exist
    date_today = date.today()
    directory_path = Path(f".{DIRECTORY_SEPARATOR}charts{DIRECTORY_SEPARATOR}{date_today}")

    if not directory_path.exists():
        directory_path.mkdir(parents=True)

    doc.save(f"{directory_path}{DIRECTORY_SEPARATOR}{PROJECT_NAME}-output.docx")


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

    # Have MVP as the first index and miscellaneous tasks as the last index
    sorted_list = sorted(sorted(data_frame["Module Label"].unique(), key=lambda e: (e == "mvp", e)),
                         key=lambda e: (e == "miscellaneous tasks", e))

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
        PROJECT_TSV_FILE_PATH,  # Replace with your project
        sep="\t",
        parse_dates=["Date Started", "Date Completed"]
    )

    # Generate Accomplishment Report
    generate_accomplishment_report(data_frame=df, project_name=PROJECT_NAME)

    # Save actual timeline as image
    # generate_project_actual_timeline_as_img(data_frame=df, project_name=PROJECT_NAME)

    # Save projected timeline as image
    # generate_project_projected_timeline_as_img(data_frame=df, project_name=PROJECT_NAME)

    # Create project statistics
    # generate_project_statistics(data_frame=df, project_name=PROJECT_NAME)


if __name__ == '__main__':
    main()
