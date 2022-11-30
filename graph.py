import pandas as pd

from bokeh.plotting import figure, show, output_file
from bokeh.models import ColumnDataSource, Range1d, LinearAxis, DataRange1d, Legend, CustomJSHover
from bokeh.layouts import gridplot
from bokeh.models.tools import HoverTool

from IPython.display import display, HTML

# Output format
output_file('filename.html', title='Graph')



# Input Data
df1 = pd.read_csv('response.csv')
final_df1 = df1.sort_values(by=['request_time'], ascending=True) 
source1 = ColumnDataSource(final_df1)

display(HTML(final_df1.to_html()))

# Plots
p1 = figure(title="Response times of web server")
# Borders config
p1.min_border_left = 0
p1.min_border_right = 0
p1.min_border_top = 0
p1.min_border_bottom = 0
# Axis and grid config
p1.xaxis.axis_label="Request start time"  
p1.yaxis.axis_label="Response time of request" 
p1.x_range = DataRange1d(range_padding=0.0) # 0/0 starting coordinates 
p1.xgrid.grid_line_color=None        # X grid line without color
#p1.add_layout(LinearAxis(y_range_name="foo"), 'right') 
#p1.extra_y_ranges={"foo": Range1d(0,1)}      
# Data config
p1_r1 = p1.vbar(x='request_time', top='request_duration', line_width=1, alpha=0.5, source=source1, color='lightgreen', muted_alpha=0.1) 
# Hover config
p1_hover1 = HoverTool(renderers=[p1_r1], tooltips=[('Request start time', '@request_time s'), ('Response time', '@response_time s')])
p1.add_tools(p1_hover1)
# Legend config
p1_legend = Legend(items=[("Response time", [p1_r1])], location="center", click_policy="mute")  
p1.add_layout(p1_legend, 'below')  

show(p1)
