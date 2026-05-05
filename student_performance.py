import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd

# Sample data
data = {
    "Hours":[1,2,3,4,5,1,2,3,4,5],
    "Marks":[50,55,60,65,70,70,75,80,85,90],
    "Group":["A","A","A","A","A","B","B","B","B","B"]
}

df = pd.DataFrame(data)

# Create app
app = dash.Dash(__name__)

# Layout
app.layout = html.Div([

    html.H1("📊 Student Performance Dashboard", style={'textAlign':'center'}),

    # Dropdown
    dcc.Dropdown(
        id="group_filter",
        options=[
            {"label":"Group A", "value":"A"},
            {"label":"Group B", "value":"B"}
        ],
        value="A",
        style={'width':'50%','margin':'auto'}
    ),

    html.Br(),

    # KPI Cards
    html.Div([
        html.Div(id="total_students", style={
            'padding':'20px','backgroundColor':'lightblue','width':'30%',
            'display':'inline-block','textAlign':'center','margin':'10px'
        }),
        
        html.Div(id="avg_marks", style={
            'padding':'20px','backgroundColor':'lightgreen','width':'30%',
            'display':'inline-block','textAlign':'center','margin':'10px'
        })
    ], style={'textAlign':'center'}),

    # Graphs
    html.Div([
        dcc.Graph(id="scatter_plot", style={'width':'48%','display':'inline-block'}),
        dcc.Graph(id="bar_chart", style={'width':'48%','display':'inline-block'})
    ])

])

# Callback
@app.callback(
    [Output("scatter_plot", "figure"),
     Output("bar_chart", "figure"),
     Output("total_students", "children"),
     Output("avg_marks", "children")],
    
    Input("group_filter", "value")
)
def update_dashboard(selected_group):

    filtered_df = df[df["Group"] == selected_group]

    # Scatter plot
    scatter_fig = px.scatter(filtered_df,
                             x="Hours",
                             y="Marks",
                             color="Group",
                             title="Hours vs Marks")

    # Bar chart
    bar_fig = px.bar(filtered_df,
                     x="Hours",
                     y="Marks",
                     title="Marks by Hours")

    # KPI values
    total = f"Total Students: {len(filtered_df)}"
    avg = f"Average Marks: {round(filtered_df['Marks'].mean(),2)}"

    return scatter_fig, bar_fig, total, avg


# Run app
if __name__ == "__main__":
    app.run(debug=True)
ejr-uxpq-jce