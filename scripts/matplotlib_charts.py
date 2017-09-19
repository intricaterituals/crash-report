#
# INFO20002 Foundations of Informatics
# Project 3
# May 2017
#
# Matplotlib charts
#
# Floyd Everest
# Kim Le
# Rainer Selby
#

#
# Bar chart code based on code from
#     http://matplotlib.org/examples/api/barchart_demo.html
#
# Code to serve dynamic image to Flask based on code from
#     https://gist.github.com/wilsaj/862153 b
#  
# Code to create pie chart using Pandas output based on code from
#     https://stackoverflow.com/questions/38337918/plot-pie-chart-and-a-table-
#     using-matplotlib-in-pandas-dataframe
#

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import matplotlib

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib as mpl

import StringIO
from flask import Flask, request, make_response

# filename of CSV file
csvfile = 'crashes.csv'

# read in the CSV file
data = pd.read_csv('crashes.csv')

# column to count
count_col = 'Y'

def flask_response(fig):
    """Using the given matplotlib 'fig', creates response to send to Flask to
       serve"""

    # render as PNG
    canvas = FigureCanvas(fig)
    png_output = StringIO.StringIO()
    canvas.print_png(png_output)

    # return as response for Flask to serve
    response = make_response(png_output.getvalue())
    response.headers['Content-Type'] = 'image/png'
    return response


def create_pie_chart(attribute):
    """Generates the pie chart requested in 'attribute' parameter"""

    # clear any previous plots
    plt.clf()
    plt.cla()
    plt.close()

    # set the parameters based on attribute
    if attribute == "young":
        # count how many crashes meet criteria
        count = (data[data['YOUNG_DRIVER'] > 0])[count_col].count()

        # count the rest
        others = data[count_col].count() - count

        series = pd.Series([count, others])
        colours = ["#F0700E", "#7A7585"]
        explode = (0.15, 0)
        startangle = 0
        labels = ("Young driver involved", "No young drivers involved")

    elif attribute == "old":
        count = (data[data['OLD_DRIVER'] > 0])[count_col].count()
        others = data[count_col].count() - count
        series = pd.Series([count, others])
        colours = ["#7A5C85", "#FFBF98"]
        explode = (0.15, 0)
        startangle = 0
        labels = ("Old driver involved", "No old drivers involved")

    elif attribute == "hitrun":
        count = (data[data['HIT_RUN_FLAG'] == "Yes"])[count_col].count()
        others = data[count_col].count() - count
        series = pd.Series([count, others])
        colours = ["#FF483C", "#2994FF"]
        explode = (0.25, 0)
        startangle = 45
        labels = ("Hit and run", "Not hit and run")

    elif attribute == "fatality":
        count_fatality = (data[data['SEVERITY'] == "Fatal accident"])[count_col].count()
        count_seriousinjury = (data[data['SEVERITY'] == "Serious injury accident"])[count_col].count()
        count_otherinjury = (data[data['SEVERITY'] == "Other injury accident"])[count_col].count()
        series = pd.Series([count_fatality, count_seriousinjury, count_otherinjury])
        explode = (0.3, 0, 0)
        startangle = 45
        colours = ["#918C8C", "#E84A30", "#ADFFA7"]
        labels = ("Fatality", "Serious injury", "Non-serious injury")

    elif attribute == "light":
        count_all = data[count_col].count()
        count_day = (data[data['LIGHT_CONDITION'] == "Day"])[count_col].count()
        count_dawndusk = (data[data['LIGHT_CONDITION'] == "Dusk/Dawn"])[count_col].count()
        count_unknown = (data[data['LIGHT_CONDITION'] == "Unk."])[count_col].count()
        count_night = (count_all - count_unknown - count_day - count_dawndusk)
        series = pd.Series([count_night, count_day, count_dawndusk])
        labels = ("Night", "Day", "Dawn/Dusk")
        colours = ["#403D6E", "#FFC341", "#9C6E72"]
        startangle = 0
        explode = (0.15, 0.1, 0.1)

    else:
        return None


    # plot as pie chart
    chart = series.plot.pie(subplots=True, autopct='%1.0f%%', explode=explode,
                           startangle=startangle, labels=labels,
                           colors=colours)

    fig = chart[0].get_figure()
    ax = chart[0].get_axes()

    # transparent background
    fig.patch.set_alpha(0)

    # round circle
    plt.axis('equal')

    # hide y axis
    ax.yaxis.set_visible(False)

    # size of figure
    fig.set_size_inches(6,3)

    # return as response for Flask to serve
    return flask_response(fig)


def create_bar_chart():
    """Generates the pie chart requested in 'attribute' parameter"""

    # clear any previous plots
    plt.clf()
    plt.cla()
    plt.close()

    # classes to use for bar chart x-axis
    categories = ["Collision with vehicle", "Collision with a fixed object",
                  "Struck Pedestrian", "Vehicle overturned (no collision)",
                  "No collision and no object struck"]

    # filters to apply to data
    filters = [data['YOUNG_DRIVER'] > 0, data['YOUNG_DRIVER'] == 0]

    series = []

    for cond in filters:
        # filter the data for each condition
        data2 = data[cond]

        # count the data
        data2_total = data2[count_col].count()

        counts = []
        sum_counted = 0

        # count the data in each category
        for cat in categories:
            count = data2[data2['ACCIDENT_TYPE'] == cat][count_col].count()
            counts.append(count)
            sum_counted += count

        # calculate the 'Others'
        counts.append(data2_total - sum_counted)
        sum_counted += count

        # convert to percentages of the total
        for i in range(len(counts)):
            counts[i] = float(counts[i]) / sum_counted * 100

        series.append(counts)


    N = 6

    young = series[0]
    non_young = series[1]

    # x locations for the groups
    ind = np.arange(N)  
    # width of the bars
    width = 0.35       

    fig, ax = plt.subplots()
    
    # transparent background
    fig.patch.set_alpha(0)

    # define bars
    rects1 = ax.bar(ind, young, width, color='#F0700E')
    rects2 = ax.bar(ind + width, non_young, width, color='#7A7585')

    # add labels
    ax.set_ylabel('%')
    ax.set_title('Crashes by type')
    ax.set_xticks(ind + width / 2)
    ax.set_xticklabels(("Collision with vehicle",
                        "Collision with a fixed object",
                        "Struck pedestrian",
                        "Vehicle overturned (no collision)",
                        "No collision and no object struck",
                        "Other"),
                        rotation=40, ha='right')

    # add legend
    ax.legend((rects1[0], rects2[0]),
              ('Crashes with at least one young driver', 'All other crashes'))

    # correct the size of the figure
    plt.tight_layout()

    # return as response for Flask to serve
    return flask_response(fig)