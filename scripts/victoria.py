from bokeh.io import show
from bokeh import io
from bokeh.models import (
    ColumnDataSource,
    HoverTool,
    LogColorMapper,
    LogTicker,
    LinearColorMapper,
    ColorBar
)

from bokeh.models.mappers import ContinuousColorMapper
from bokeh.models.tools import BoxZoomTool
from bokeh.palettes import Magma256 as palette
from bokeh.plotting import figure, save
from geometry_handler import getCoords, source
from bokeh.embed import components

palette.reverse()

TOOLS = "pan,reset,hover,save"
color_mapper = LinearColorMapper(palette, low=0, high=150)

p = figure(title="Traffic accidents per local government area (2012-2016)", 
    tools=TOOLS, width=1000, height=720, 
    x_axis_location=None, y_axis_location=None,
    webgl=True
    )

p.add_tools(BoxZoomTool(match_aspect=True))

p.patches('x', 'y', source=source,
          fill_color={'field': 'YOUNG_DRIVER', 'transform': color_mapper},
          fill_alpha=0.7, line_color=None, line_width=0.1)

p.grid.grid_line_color = None

hover = p.select_one(HoverTool)
hover.point_policy = "follow_mouse"
hover.tooltips = [
    ("Name", "@LGA_NAME"),
    ("Total young driver incidents", "@YOUNG_DRIVER"),
    ("(Long, Lat)", "($x, $y)"),
]

color_bar = ColorBar(color_mapper=color_mapper,
                     label_standoff=12, background_fill_alpha=0.7, scale_alpha=0.6,
                     border_line_color=None, location=(0,0))

p.add_layout(color_bar, 'left')

p.title.align = "center"
p.title.text_font_size = "20px"

# Output filepath to HTML
output_file = r"vicmap.html"

# Save the map
save(p, output_file);
