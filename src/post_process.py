import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MultipleLocator, AutoMinorLocator, FuncFormatter
from bs4 import BeautifulSoup
import datetime as dt
import os, glob


def create_plot(group_name, group_data, plot_dir):

    # Create a figure and axes
    fig, ax = plt.subplots(figsize=(20, 6))

    x = list(group_data["Timestamp"])

    y1 = group_data["Total Average Response Time"].values
    y2 = group_data["Total Min Response Time"].values
    y3 = group_data["Total Max Response Time"].values
    y4 = group_data["Failures/s"].values

    # Plot the data as a line plot with datetimes on the x-axis
    # ax.plot_date(dates, values, linestyle='-', marker=None)
    ax.plot_date(x, y1, linestyle='-', marker=None, color='green', label='AVG')
    ax.plot_date(x, y2, linestyle='-', marker=None, color='blue', label='MIN')
    ax.plot_date(x, y3, linestyle='-', marker=None, color='orange', label='MAX')
    ax.plot_date(x, y4, linestyle='-', marker=None, color='red', label='Failures')

    # Set the intervals for the x-axis to be every 5 minutes
    ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=30))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

    # Add minor tick marks at 1-minute intervals
    ax.xaxis.set_minor_locator(MultipleLocator(1))
    ax.xaxis.set_minor_formatter(FuncFormatter(lambda x, pos: ''))

    # Add a legend to the plot
    ax.legend()

    # Add labels and a title
    ax.set_xlabel('Time')
    ax.set_ylabel('RPS')
    ax.set_title(f'Plot {group_name}')

    # Save the plot to a file
    plot_file = os.path.join(plot_dir, f'{group_name}.png')
    plt.savefig(plot_file)

    # Clear the figure for the next group
    plt.clf()


def manage_plotting(files):

    # Read in the CSV data and group it by the "group" column
    if not os.path.exists(files['plot_dir']):
        os.mkdir(files['plot_dir'])

    df = pd.read_csv(files['stats_file'])

    # Drop all rows with NaN values
    df = df.dropna()

    df = df.reset_index()

    df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='s')

    grouped_data = df.groupby("Name")

    # Iterate over the groups and plot and save the data for each group
    for group_name, group_data in grouped_data:
        if group_name == 'Aggregated':
            continue
        create_plot(group_name, group_data, files['plot_dir'])


def manage_html_report(files):

    # Load the HTML file
    with open(files['html_file'], 'r') as f:
        html = f.read()

    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    # Find the div with class 'charts-container'
    charts_div = soup.find('div', {'class': 'charts-container'})

    # Find the h2 tag within the div
    h2_tag = charts_div.find('h2')

    plot_files = sorted(glob.glob(os.path.join(files['plot_dir'], '*.png')))

    for plot_file in plot_files:

        plot_format = 'png'
        plot_basename = os.path.basename(plot_file).replace(f'.{plot_format}', '')

        # Create an image tag with the desired source and alt attributes
        img_tag = soup.new_tag(
            'img', 
            src=f'./plots/{plot_basename}.{plot_format}', 
            width=1000,
            height=300,
            alt=plot_basename
        )

        # Create an br tag 
        br_tag = soup.new_tag('br')

        # Insert the image tag after the h2 tag
        h2_tag.insert_after(img_tag)
        h2_tag.insert_after(br_tag)

    # Save the modified HTML to a new file
    with open(files['modified_html_file'], 'w') as f:
        f.write(str(soup))


def move_files_to_new_report_dir():
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data/')

    now = dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    new_report_dir = os.path.join(data_dir, f'report_{now}')
    if not os.path.exists(new_report_dir):
        os.mkdir(new_report_dir)

    print('report_dir: ', new_report_dir)

    html_file = os.path.join(data_dir, 'report.html')
    stats_file = os.path.join(data_dir, 'report.csv_stats_history.csv')
    if not os.path.exists(html_file) or not os.path.exists(stats_file):
        raise Exception("OOOOOPS, cant find report.html or history_stats_file, stopping post processing")
    
    dst_html_file = os.path.join(new_report_dir, f'report_{now}.html')
    os.rename(html_file, dst_html_file)

    dst_stats_file = os.path.join(new_report_dir, f'report.csv_stats_history_{now}.csv')
    os.rename(stats_file, dst_stats_file)

    new_html_file = os.path.join(new_report_dir, f'modified_report_{now}.html')
    plot_dir = os.path.join(new_report_dir, 'plots')

    files = {
        'report_dir': new_report_dir,
        'html_file': dst_html_file,
        'modified_html_file': new_html_file,
        'stats_file': dst_stats_file,
        'plot_dir': plot_dir
    }

    return files


def manage_post_processing():

    files = move_files_to_new_report_dir()

    manage_plotting(files)
    
    manage_html_report(files)


if __name__ == "__main__":
    manage_post_processing()