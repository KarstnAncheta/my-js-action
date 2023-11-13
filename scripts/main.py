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
from pathlib import Path
from datetime import datetime
import calendar
import pandas as pd
from docxtpl import DocxTemplate, InlineImage


DEVELOPER_DETAILS = {
    'name': 'Karstn Paul P. Ancheta',
    'position': 'Information Systems Analyst I',
    'date_hired': datetime(2023, 1, 16)
}
REVIEWER_DETAILS = {
    'name': 'Francis L. Camarao',
    'position': 'Information Systems Analyst III',
}
RENDER_DATES = [
    datetime(2023, 10, 30),
    datetime(2023, 11, 1),
    datetime(2023, 11, 2),
    datetime(2023, 11, 4),
]
PROJECTS = [
    {
        'PROJECT_NAME': 'eGov-BEBS',
        'PROJECT_TSV_FILE_PATH': 'tsv/egov-bebs.tsv',
        'PROJECT_IMAGES_PATH': 'screenshots/egov-bebs',
        'PROJECT_DETAILS': 'To design, build, test, and deploy a system for the Budgeting Office that will digitize a part of their current process.'
    },
]

DIRECTORY_SEPARATOR = os.path.sep


def generate_accomplishment_report() -> None:

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

    # Document template
    doc = DocxTemplate('AR-template.docx')

    # Projects object
    projects = []

    for project_data in PROJECTS:
        project = {
            'name': project_data['PROJECT_NAME'],
            'details': project_data['PROJECT_DETAILS'],
            'modules': [],
            'tasks': [],
            'images': [],
            'rendered_tasks': {date: [] for date in RENDER_DATES}
        }

        # Read dataframe
        df = pd.read_table(
            project_data['PROJECT_TSV_FILE_PATH'],
            sep="\t",
            parse_dates=["Date Started", "Date Completed"]
        )

        # Drop unnecessary columns
        df = df.drop([
            'URL',
            'Story Points',
            'Labels',
            'Priority Level',
        ], axis=1)

        # Get tasks under the "On Hold", "In Progress", and "Done" column
        tasks = df[(df['Status'].isin(['On Hold', 'In Progress', 'Done']))]

        project['modules'] = tasks['Module Label'].unique()

        if RENDER_DATES is not None:
            for render_date in RENDER_DATES:

                # Filter tasks within the current render date
                current_rendered_tasks = df[((df['Date Started'] <= render_date) & (df['Date Completed'] >= render_date)) | (df['Date Started'] == render_date)]

                # Exclude current rendered tasks from tasks
                tasks = tasks[~tasks.index.isin(current_rendered_tasks.index)]

                # If there are rendered tasks, add them to the key pair value
                if len(current_rendered_tasks) >= 1:
                    project['rendered_tasks'][render_date] = [{key.replace(' ', '_'): value for key, value in record.items()} for record in current_rendered_tasks.to_dict(orient='records')]

        # Convert tasks to list of dictionaries and update the 'tasks' key in the project dictionary
        project['tasks'] = [{key.replace(' ', '_'): value for key, value in record.items()} for record in
                            tasks.to_dict(orient='records')]

        # Specify the directory containing the images
        directory_path = project_data['PROJECT_IMAGES_PATH']

        # Get a list of all files in the directory
        all_files = os.listdir(directory_path)

        # Filter out image files (you can extend the list of allowed extensions)
        image_files = [file for file in all_files if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]

        # Process each image file
        image_data_array = []
        for image_file in image_files:
            image_path = os.path.join(directory_path, image_file)
            image_data = InlineImage(doc, image_path, width=512 * 9525, height=320 * 9525)  # EMU calculations
            image_data_array.append(image_data)

        project['images'] = image_data_array

        # Make render dates human readable
        project['rendered_tasks'] = {key.strftime('%Y-%m-%d %H:%M:%S'): value for key, value in project['rendered_tasks'].items()}

        # Append the updated project dictionary to the projects list
        projects.append(project)

    data = {
        'developer_name': DEVELOPER_DETAILS['name'],
        'developer_position': DEVELOPER_DETAILS['position'],
        'reviewer_name': REVIEWER_DETAILS['name'],
        'reviewer_position': REVIEWER_DETAILS['position'],
        'cutoff_dates': get_cutoff_period(),
        'tc': calculate_cutoffs(DEVELOPER_DETAILS['date_hired'], formatted_datetime),
        'projects': projects,
    }
    doc.render(data)

    # Creates the directory if it does not exist
    directory_path = Path(f".{DIRECTORY_SEPARATOR}ACCOMPLISHMENT REPORTS")

    if not directory_path.exists():
        directory_path.mkdir(parents=True)

    doc.save(f"{directory_path}{DIRECTORY_SEPARATOR}output.docx")


def main() -> None:
    """
    Main method.
    :return: None
    """

    # Generate Accomplishment Report
    generate_accomplishment_report()


if __name__ == '__main__':
    main()
