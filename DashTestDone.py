import dash
from dash import dcc, html
import dash.dependencies as dd
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

app = dash.Dash(__name__)
df =pd.read_csv(r"C:\Users\aydar\Desktop\Dashhy\spacex_launch_dash.csv")

app.layout = html.Div([
    html.H1("Launch Success Pie Chart"),

    # Dropdown for selecting site
    dcc.Dropdown(id='site-dropdown',
            options = [{'label': 'All Sites', 'value': 'ALL'}] + [{'label': site, 'value': site} for site in df['Launch Site'].unique()],
            value='ALL',
            placeholder="place holder here",
            searchable=True
            ),
    
    # Graph for pie chart
    dcc.Graph(id="success-pie-chart"),
    dcc.Graph(id="success-payload-scatter-chart"),

    dcc.RangeSlider(id='payload-slider',
                min=0, max=10000, step=1000,
                marks={0: '0',
                       100: '100'},
                value=[0, 10000])
])

@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))

def get_pie_chart(entered_site):
    # If 'ALL' is selected, show data for all sites
    if entered_site == 'ALL':
        fig = px.pie(df, values='class', names='Launch Site', title='Launch Success Pie Chart')
    else:
        # Filter the DataFrame based on the selected site
        filtered_df = df[df["Launch Site"] == entered_site]
        
        # Manually count the successes (1) and failures (0)
        class_counts = filtered_df['class'].value_counts()  # Get the count of 1's (success) and 0's (failure)
        
        # Check if both success and failure are present
        if 1 in class_counts and 0 in class_counts:
            values = class_counts
            names = ['Success', 'Failure']
        elif 1 in class_counts:
            values = [class_counts[1], 0]
            names = ['Success', 'Failure']
        else:
            values = [0, class_counts[0]]
            names = ['Success', 'Failure']
        
        fig = px.pie(
            names=names,
            values=values,  # Use the manually counted values (success vs. failure)
            title=f'Launch Success for {entered_site}',
            color=names,  # Color the slices by 'Success' and 'Failure'
        )
    
    return fig
    

@app.callback(
    Output("success-payload-scatter-chart", "figure"),
    [Input("site-dropdown", "value"),
     Input("payload-slider", "value")]
)

def update_scatter_chart(selected_site, payload_range):
    if selected_site == 'ALL':
        filtered_df = df[
            (df["Payload Mass (kg)"] >= payload_range[0]) & 
            (df["Payload Mass (kg)"] <= payload_range[1])
        ]
    else:
        filtered_df = df[
        (df["Launch Site"] == selected_site) &
        (df["Payload Mass (kg)"] >= payload_range[0]) &
        (df["Payload Mass (kg)"] <= payload_range[1])
        ]

    fig = px.scatter(
        filtered_df,
        x="Payload Mass (kg)",
        y="class",
        color=filtered_df["Launch Site"],
        title=f"Payload vs. Success for {selected_site}",
        labels={"Success": "Launch Outcome"}
    )
    fig.update_layout(yaxis_title="Launch Outcome")
    return fig

if __name__ == "__main__":
    app.run_server(debug=True)


