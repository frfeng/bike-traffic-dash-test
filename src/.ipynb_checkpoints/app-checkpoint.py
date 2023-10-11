import numpy as np
import pandas as pd
df = pd.read_excel("./data/bike-counter-annarbor.xlsx", skiprows=3, names=['datetime', 'in', 'out'])

df_weather = pd.read_csv("./data/weather-annarbor.csv", 
                         parse_dates=['DATE'],
                         usecols=['DATE', 'PRCP', 'TMAX', 'TMIN'],
                        )

import plotly.express as px
from dash import Dash, html, dcc, Input, Output

app = Dash(__name__)   # make an instance of the dashboard application

server = app.server

# specify the layout of the dashboard
app.layout = html.Div([
    html.H1(children=["Bicycle traffic dashboard"]),

    html.H2(children=dcc.Markdown("Location: [Division St. Ann Arbor, MI](https://maps.app.goo.gl/3n6pveJ7ojM7ZSzU8)")),

    dcc.DatePickerRange(id='date_range',
                        start_date='2023-05-01',
                        end_date='2023-09-16',
                       ),

    dcc.RadioItems(id='data_res', 
                   options={"1_week":"Weekly",
                            "1_day":"Daily",
                            "1_hour":"Hourly",
                           },
                   value='1_day',
                   inline=True,
                  ),

    dcc.Graph(id='trend_graph'),
])

# specify the callback function

@app.callback(
    Output(component_id='trend_graph', component_property='figure'),
    Input(component_id='date_range', component_property='start_date'),
    Input(component_id='date_range', component_property='end_date'),
    Input(component_id='data_res', component_property='value'),
)

def update_figure(start_date, end_date, data_res_value):

    if data_res_value == '1_week':

        rule = 'W'

    elif data_res_value == '1_day':

        rule = 'D'

    elif data_res_value == '1_hour':

        rule = 'H'
    
    df_updated = (
        df
          .set_index("datetime")
          .resample(rule)
          .sum()
          .assign(total=lambda x:x['in'] + x['out'],
                  day_of_week=lambda x: x.index.day_name(),
                 )
          .loc[start_date:end_date]
          .join(df_weather.set_index('DATE'))
    )    

    fig = px.bar(df_updated, 
                 x=df_updated.index,
                 y='total',
                 hover_data=['in', 'out', 'day_of_week', 'TMAX', 'TMIN', 'PRCP'],
                )
    return fig

if __name__ == '__main__':

    app.run(jupyter_mode='external', debug=True, port=8051)
