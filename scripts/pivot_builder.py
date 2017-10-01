#
# INFO20002 Foundations of Informatics
# Project 3
# May 2017
#
# Pivot Table Builder
#
# Floyd Everest
# Kim Le
# Rainer Selby
#
#

import csv
import json


class AverageClass:
    """Stores sum and count of a cell, in order to calculate an average"""
    total = 0
    count = 0

    def average(self):
        return float(self.total) / self.count


csvfile = 'crashes.csv'


def read_csv(csv_filename):

    data = []

    # Read CSV file and store to data
    with open(csv_filename, 'rb') as csv_file:
        reader = csv.reader(csv_file)

        for row in reader:
            data.append(row)

    # Return list of headings (first CSV row) and the data
    return (data[0], data[1:])


def check_filters(csv_row, filters, filter_nums, headings):
    """
    Returns True if a csv_row should be excluded from the pivot table based on
    the filters specified in the user's request

    Arguments:
    csv_row -- row of CSV data to test
    filters -- dictionary of all filters information supplied in the web form
    filter_nums -- list of all unique filter identifier numbers
    headings -- ordered list of headings from the CSV file
    """

    for num in filter_nums:
        try:
            filter_att = filters["FilterAttribute" + num]
            filter_type = filters["FilterType" + num]
            filter_text = filters["FilterText" + num]
        # Skip filter if any of the three required fields is missing
        except KeyError:
            continue

        # Ensure an attribute and non-blank text was provided
        if filter_att != "NoFilter" and filter_text != "":

            filter_index = headings.index(filter_att)
            filter_cell = csv_row[filter_index]

            # Perform checks, return True if cell breaches filter
            if filter_type == "equals" and \
               filter_cell.lower() != filter_text.lower():
                return True

            if filter_type == "does_not_equal" and \
               filter_cell.lower() == filter_text.lower():
                return True

            if filter_type == "contains" and \
               filter_text.lower() not in filter_cell.lower():
                return True

            if filter_type == "does_not_contain" and \
               filter_text.lower() in filter_cell.lower():
                return True

            # Less/greater than sign is reversed for these inequality filters,
            # as we are returning True if the cell breaches the filter
            if filter_type == "less_than" and \
               filter_cell >= filter_text:
                return True

            if filter_type == "less_than_or_equal" and \
               filter_cell > filter_text:
                return True

            if filter_type == "greater_than" and \
               filter_cell <= filter_text:
                return True

            if filter_type == "greater_than_or_equal" and \
               filter_cell < filter_text:
                return True

    # If no filter criterion breached, do not exclude the row
    return False


def update_cell(cell, operation, att3_value):
    """
    Updates an existing numerical cell value based on the selected operation
    and the value of the new value to take into account

    cell -- current value of cell
    operation -- e.g. 'sum', 'average', 'count'
    att3_value -- new value to take into account
    """

    if operation == "sum":
        if cell is None:
            cell = att3_value
        else:
            cell += att3_value

    elif operation == "count":
        if cell is None:
            cell = 1
        else:
            cell += 1

    elif operation == "average":
        if cell is None:
            cell = AverageClass()
            cell.total = att3_value
            cell.count = 1
        else:
            cell.total += att3_value
            cell.count += 1

    elif operation == "max":
        if cell is None:
            cell = att3_value
        else:
            if att3_value > cell:
                cell = att3_value

    elif operation == "min":
        if cell is None:
            cell = att3_value
        else:
            if att3_value < cell:
                cell = att3_value

    return cell


def process_data(json_request):
    """
    Using the user's parameters submitted in the form, processes the dataset to
    produce the pivoted data

    Arguments:
    json_request -- a list of dictionaries representing all of the
                    user-submitted form data
    """

    # Read in the CSV dataset
    headings, data = read_csv(csvfile)

    request = {}
    filters = {}
    filter_nums = []

    # Convert json_request to a single dictionary
    for item in json_request:
        key = str(item["name"])
        value = str(item["value"])

        # Store filters in separate dict and keep a list of indentifer
        # numbers
        if "Filter" in key:
            filters[key] = value

            # Append each unique filter number to list
            if "FilterAttribute" in key:
                filter_nums.append(str(key[15:]))

        # Store all other input information in request dict
        else:
            request[key] = value

    # Store the index number of each attribute column as per the CSV dataset
    try:
        att1_index = headings.index(request["att1"])
        att2_index = headings.index(request["att2"])
        att3_index = headings.index(request["att3"])

        operation = request["operation"]
    except KeyError:
        # Required field(s) missing
        return ("error", 0, 0, 0, 0)

    table = {}
    col_headings = []
    row_headings = []

    for csv_row in data:

        # Skip row if it breaches any filters
        if check_filters(csv_row, filters, filter_nums, headings) is True:
            continue

        att1_value = csv_row[att1_index]
        att2_value = csv_row[att2_index]

        # The value for the numerical attribute needs to be an int
        try:
            att3_value = int(csv_row[att3_index])
        # Otherwise skip this CSV row entirely
        except ValueError:
            continue

        # Ensure there is a dictionary set up for the combination of att1 and
        # att2 within table
        if att1_value not in table:
            table[att1_value] = {att2_value: None}
        elif att2_value not in table[att1_value]:
            table[att1_value][att2_value] = None

        # Ensure att1 and att2 are included in appropriate headings list
        if att1_value not in col_headings:
            col_headings.append(att1_value)
        if att2_value not in row_headings:
            row_headings.append(att2_value)

        # Update cell value
        cell = table[att1_value][att2_value]
        table[att1_value][att2_value] = update_cell(cell, operation,
                                                    att3_value)

    # After all cells are processed, if the operation is average, convert each
    # cell from AverageClass into a float representing the average value
    if operation == "average":
        for att1 in table:
            for att2 in table[att1]:
                average = table[att1][att2].average()
                table[att1][att2] = "{:.2f}".format(average)

    # Find the largest and smallest value in cells. This will be used when
    # colouring the cells based on their relative value.
    maxvalue = None
    minvalue = None

    for att1 in table:
        for att2 in table[att1]:
            cell = table[att1][att2]
            if maxvalue is None and minvalue is None:
                maxvalue = cell
                minvalue = cell
            elif cell > maxvalue:
                maxvalue = cell
            elif cell < minvalue:
                minvalue = cell

    # Sort the lists of headings alphabetically for presentation
    col_headings.sort()
    row_headings.sort()

    return (table, col_headings, row_headings, minvalue, maxvalue)


def cell_colour(cell, minvalue, maxvalue):
    """
    Given 10 equal bins apportioned over the range of values in the table,
    returns which bin the cell would fall into.

    This allows the cell to be coloured in the pivot table based on its
    relative size to the rest of the data.

    Arguments:
    cell -- cell value to test
    minvalue -- smallest value in pivot table
    maxvalue -- largest value in pivot table
    """

    # Numer of bins
    bins = 10

    # Range of values and bin size
    valuerange = float(maxvalue) - float(minvalue)
    increment = float(valuerange) / bins
    testvalue = float(minvalue) + increment + 0.1

    # Find bin number and return
    for i in range(1, bins+1):
        if cell <= testvalue:
            return str(i)
        else:
            testvalue += increment

    return str(bins)


def generate_table(json_request):
    """
    Generate a pivot table

    Arguments:
    json_request -- a list of dictionaries representing all of the
    user-submitted form data
    """

    # Produce pivoted data based on the user's requested parameters
    table, col_headings, row_headings, minvalue, maxvalue = \
        process_data(json_request)

    if table == "error":
        return '<p class="error">Please complete all required fields</p>'

    # Create HTML rendering of pivoted data
    html = '<table id="pivottable"><tr><th></th>'

    for col in col_headings:
        # Empty attributes are to be represented with the word "(blanks)""
        if col.strip() == "":
            html += '<th>(blanks)</th>'
        else:
            html += '<th>' + col + '</th>'

    html += '</tr>'

    for row in row_headings:
        if row.strip() == "":
            html += '<tr><th>(blanks)</th>'
        else:
            html += '<tr><th>' + row + '</th>'

        for col in col_headings:
            try:
                cell = table[col][row]
                # Determine which bin the cell value falls in for colouring
                colour = cell_colour(cell, minvalue, maxvalue)
                html += '<td class="bin-' + colour + '">' + str(cell) + '</td>'
            # If no cell exists for the combination of row and column attribute
            except KeyError:
                html += '<td></td>'

        html += '</tr>'

    html += '</table>'

    # Return the complete HTML table
    return html
