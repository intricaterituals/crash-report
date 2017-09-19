
from bokeh.charts.attributes import cat, color
from bokeh.palettes import YlGnBu9 as palette
from bokeh.embed import components
from bokeh.charts.attributes import ColorAttr, CatAttr

def hitrun_chart(value, value_label, filename):

    '''
    Takes 3 string arguments:
    column name of attribute being pivoted with HIT_RUN_FLAG as "value",
    an axis label name as "value_label", 
    and a filename for the final JS output as "filename"

    Outputs Bokeh plot in JS format for embedding

    '''

    df = pd.pivot_table(crashes[crashes.HIT_RUN_FLAG == 'Yes'], values='HIT_RUN_FLAG', 
                          index=value, aggfunc='count')

    df = df.to_frame()
    hitrun_speed.reset_index(inplace=True)

    hover = HoverTool(
        tooltips = [
        ("Total hit and runs", "@height"),
    ])

    tools=[hover]
    a = Bar(df, label=CatAttr(columns=[value], sort=False), 
            values='HIT_RUN_FLAG', plot_width=720,
             plot_height=720, 
            color=color(columns = 'HIT_RUN_FLAG', palette=palette),
              tools=tools, legend='top_right', sizing_mode="scale_both")

    a.xaxis.axis_label=value_label
    a.yaxis.axis_label='Total number of hit and runs'

    #save file to JS

    script, div = components(a)

    foo = open(filename, 'w')
    foo.write(script)
    foo.close

#### PLOTTING THE BAR CHARTS ########

hitrun_chart('SPEED_ZONE', 'Speed zone', 'hitrun_speed.js')
hitrun_chart('SEVERITY', 'Severity of accident', 'hitrun_sev.js')
hitrun_chart('NO_OF_VEHICLES', 'Number of vehicles', 'hitrun_vehicles.js')
hitrun_chart('LIGHT_CONDITION', 'Light condition', 'hitrun_light.js')
