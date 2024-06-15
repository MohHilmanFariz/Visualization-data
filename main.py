import pandas as pd
import numpy as np
from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import Select, ColumnDataSource, Div
from bokeh.plotting import figure

# Load the dataset (sample data for illustration)
# Replace 'data.csv' with your actual dataset path
df = pd.read_csv('data.csv')

# Filter columns to include only numeric data types (integers and floats)
numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()

# Ensure there are at least two numeric columns to plot
if len(numeric_cols) < 2:
    raise ValueError("The dataset must contain at least two numeric columns.")

# Initial column selection for scatter plot
initial_x1 = numeric_cols[0]
initial_y1 = numeric_cols[1]

# Initial column selection for histogram
initial_hist = numeric_cols[0]

# Initial column selection for line chart (assuming 'Tahun' column exists)
initial_line = 'Tahun'  # Adjust this based on your actual column name

# Initial column selection for boxplot
initial_box = numeric_cols[1]  # Adjust this index based on your preference

# Initial province selection
initial_provinsi = df['Provinsi'].unique()[0]

# Create ColumnDataSource for scatter plot
source1 = ColumnDataSource(data={
    'x': df[df['Provinsi'] == initial_provinsi][initial_x1],
    'y': df[df['Provinsi'] == initial_provinsi][initial_y1],
})

# Create ColumnDataSource for histogram
hist, edges = np.histogram(
    df[df['Provinsi'] == initial_provinsi][initial_hist], bins=20)
source2 = ColumnDataSource(data={
    'top': hist,
    'left': edges[:-1],
    'right': edges[1:],
})

# Create ColumnDataSource for line chart
source3 = ColumnDataSource(data={
    # Use 'Tahun' column as X-axis
    'x': df[df['Provinsi'] == initial_provinsi]['Tahun'],
    'y': df[df['Provinsi'] == initial_provinsi][initial_line],
})

# Create ColumnDataSource for barchart
# Assuming you want to create barchart for one numeric column grouped by 'Provinsi'
barchart_source = ColumnDataSource(data={
    'provinsi': df['Provinsi'],
    # Adjust this based on the numeric column you want to plot
    'values': df[initial_x1],
})

# Create ColumnDataSource for box plot
grouped = df.groupby('Provinsi')
provinces = df['Provinsi'].unique()
source5 = ColumnDataSource(data={
    'provinsi': provinces,
    'q1': [grouped.get_group(prov)[initial_box].quantile(0.25) for prov in provinces],
    'q2': [grouped.get_group(prov)[initial_box].quantile(0.5) for prov in provinces],
    'q3': [grouped.get_group(prov)[initial_box].quantile(0.75) for prov in provinces],
    'upper': [min(grouped.get_group(prov)[initial_box].max(), grouped.get_group(prov)[initial_box].quantile(0.75) + 1.5 * (grouped.get_group(prov)[initial_box].quantile(0.75) - grouped.get_group(prov)[initial_box].quantile(0.25))) for prov in provinces],
    'lower': [max(grouped.get_group(prov)[initial_box].min(), grouped.get_group(prov)[initial_box].quantile(0.25) - 1.5 * (grouped.get_group(prov)[initial_box].quantile(0.75) - grouped.get_group(prov)[initial_box].quantile(0.25))) for prov in provinces]
})

# Create Select widgets for scatter plot
x_axis_select1 = Select(title='Select X-axis feature for Scatter Plot',
                        value=initial_x1, options=numeric_cols)
y_axis_select1 = Select(title='Select Y-axis feature for Scatter Plot',
                        value=initial_y1, options=numeric_cols)
provinsi_select1 = Select(title='Select Province for Scatter Plot',
                          value=initial_provinsi, options=['Semua Provinsi'] + df['Provinsi'].unique().tolist())

# Create Select widget for histogram
hist_select = Select(title='Select feature for Histogram',
                     value=initial_hist, options=numeric_cols)
provinsi_select2 = Select(title='Select Province for Histogram',
                          value=initial_provinsi, options=['Semua Provinsi'] + df['Provinsi'].unique().tolist())

# Create Select widget for line chart
line_select = Select(title='Select feature for Line Chart',
                     value=initial_line, options=numeric_cols)
provinsi_select3 = Select(title='Select Province for Line Chart',
                          value=initial_provinsi, options=['Semua Provinsi'] + df['Provinsi'].unique().tolist())

# Create Select widget for bar chart
barchart_select = Select(title='Select feature for Bar Chart',
                         value=initial_x1, options=numeric_cols)

# Create Select widgets for box plot
box_select = Select(title='Select feature for Box Plot',
                    value=initial_box, options=numeric_cols)

# Create the scatter plot figure
p1 = figure(title='Scatter Plot', x_axis_label=initial_x1,
            y_axis_label=initial_y1)
p1.circle('x', 'y', source=source1, size=8)

# Create the histogram figure
p2 = figure(title='Histogram', x_axis_label=initial_hist, y_axis_label='Count')
p2.quad(top='top', bottom=0, left='left', right='right',
        source=source2, fill_color="navy", line_color="white", alpha=0.5)

# Create the line chart figure
p3 = figure(title='Line Chart', x_axis_label='Tahun',
            y_axis_label=initial_line)
p3.line('x', 'y', source=source3, line_width=2)

# Create the Bar chart figure
p4 = figure(title='Bar chart', x_range=df['Provinsi'].unique().tolist(),
            y_axis_label=initial_x1)
p4.vbar(x='provinsi', top='values', source=barchart_source, width=0.7)

# Create the box plot figure
p5 = figure(title='Box Plot', x_axis_label='Provinsi',
            y_axis_label=initial_box, x_range=provinces)
p5.segment(x0='provinsi', y0='upper', x1='provinsi',
           y1='q3', source=source5, line_color="black")
p5.segment(x0='provinsi', y0='lower', x1='provinsi',
           y1='q1', source=source5, line_color="black")
p5.vbar(x='provinsi', width=0.7, bottom='q2', top='q3',
        source=source5, fill_color="#E08E79", line_color="black")
p5.vbar(x='provinsi', width=0.7, bottom='q1', top='q2',
        source=source5, fill_color="#3B8686", line_color="black")
p5.rect(x='provinsi', y='lower', width=0.2,
        height=0.01, source=source5, line_color="black")
p5.rect(x='provinsi', y='upper', width=0.2,
        height=0.01, source=source5, line_color="black")


# Define callback function to update scatter plot
def update_scatter(attr, old, new):
    x_axis = x_axis_select1.value
    y_axis = y_axis_select1.value
    provinsi = provinsi_select1.value
    if provinsi == 'Semua Provinsi':
        source1.data = {
            'x': df[x_axis],
            'y': df[y_axis],
        }
    else:
        source1.data = {
            'x': df[df['Provinsi'] == provinsi][x_axis],
            'y': df[df['Provinsi'] == provinsi][y_axis],
        }
    p1.xaxis.axis_label = x_axis
    p1.yaxis.axis_label = y_axis

# Define callback function to update histogram


def update_histogram(attr, old, new):
    hist_feature = hist_select.value
    provinsi = provinsi_select2.value
    if provinsi == 'Semua Provinsi':
        hist, edges = np.histogram(df[hist_feature], bins=20)
    else:
        hist, edges = np.histogram(
            df[df['Provinsi'] == provinsi][hist_feature], bins=20)
    source2.data = {
        'top': hist,
        'left': edges[:-1],
        'right': edges[1:],
    }
    p2.xaxis.axis_label = hist_feature

# Define callback function to update line chart


def update_line(attr, old, new):
    line_feature = line_select.value
    provinsi = provinsi_select3.value
    if provinsi == 'Semua Provinsi':
        source3.data = {
            'x': df['Tahun'],
            'y': df[line_feature],
        }
    else:
        source3.data = {
            'x': df[df['Provinsi'] == provinsi]['Tahun'],
            'y': df[df['Provinsi'] == provinsi][line_feature],
        }
    p3.yaxis.axis_label = line_feature

# Define callback function to update barchart


def update_barchart(attr, old, new):
    barchart_feature = barchart_select.value
    barchart_source.data = {
        'provinsi': df['Provinsi'],
        'values': df[barchart_feature],
    }
    p4.yaxis.axis_label = barchart_feature


# Define callback function to update box plot
def update_boxplot(attr, old, new):
    box_feature = box_select.value
    grouped = df.groupby('Provinsi')
    provinces = df['Provinsi'].unique()
    source5.data = {
        'provinsi': provinces,
        'q1': [grouped.get_group(prov)[box_feature].quantile(0.25) for prov in provinces],
        'q2': [grouped.get_group(prov)[box_feature].quantile(0.5) for prov in provinces],
        'q3': [grouped.get_group(prov)[box_feature].quantile(0.75) for prov in provinces],
        'upper': [min(grouped.get_group(prov)[box_feature].max(), grouped.get_group(prov)[box_feature].quantile(0.75) + 1.5 * (grouped.get_group(prov)[box_feature].quantile(0.75) - grouped.get_group(prov)[box_feature].quantile(0.25))) for prov in provinces],
        'lower': [max(grouped.get_group(prov)[box_feature].min(), grouped.get_group(prov)[box_feature].quantile(0.25) - 1.5 * (grouped.get_group(prov)[box_feature].quantile(0.75) - grouped.get_group(prov)[box_feature].quantile(0.25))) for prov in provinces]
    }
    p5.yaxis.axis_label = box_feature


# Add the callback functions to the Select widgets
x_axis_select1.on_change('value', update_scatter)
y_axis_select1.on_change('value', update_scatter)
provinsi_select1.on_change('value', update_scatter)
hist_select.on_change('value', update_histogram)
provinsi_select2.on_change('value', update_histogram)
line_select.on_change('value', update_line)
provinsi_select3.on_change('value', update_line)
barchart_select.on_change('value', update_barchart)
box_select.on_change('value', update_boxplot)

# Create layouts for each plot
layout1 = column(provinsi_select1, x_axis_select1, y_axis_select1, p1)
layout2 = column(provinsi_select2, hist_select, p2)
layout3 = column(provinsi_select3, line_select, p3)
layout4 = column(barchart_select, p4)
layout5 = column(box_select, p5)

# Create a title for the dashboard
title = Div(text="<h1 style='text-align: center'>Data Visualization Dashboard Tanaman Padi Sumatera</h1>", width=1200)

# Combine all layouts
layout = column(title, row(layout1, layout2), row(layout3, layout4), layout5)

# Add the layout to the current document
curdoc().add_root(layout)

# To display the plot in a standalone script, uncomment the following line:
# show(layout)
