import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Load dataset
df=pd.read_csv('Sample - Superstore.csv',encoding='utf-8',encoding_errors='ignore')

# Data preprocessing
df['Order Date'] = pd.to_datetime(df['Order Date'])

# Initialize app
app = dash.Dash(__name__)

# Layout
app.layout = html.Div([
    html.H1("Superstore Sales Dashboard", style={'textAlign': 'center'}),

    # Filters
    html.Div([
        dcc.DatePickerRange(
            id='date_filter',
            start_date=df['Order Date'].min(),
            end_date=df['Order Date'].max()
        ),

        dcc.Dropdown(
            id='category_filter',
            options=[{'label': i, 'value': i} for i in df['Category'].unique()],
            multi=True,
            placeholder="Select Category"
        ),

        dcc.Dropdown(
            id='region_filter',
            options=[{'label': i, 'value': i} for i in df['Region'].unique()],
            multi=True,
            placeholder="Select Region"
        )
    ], style={'display': 'flex', 'gap': '20px'}),

    # Graphs
    dcc.Graph(id='sales_overview'),
    dcc.Graph(id='region_performance'),
    dcc.Graph(id='profit_analysis')
])

# Callback
@app.callback(
    [Output('sales_overview', 'figure'),
     Output('region_performance', 'figure'),
     Output('profit_analysis', 'figure')],
    
    [Input('date_filter', 'start_date'),
     Input('date_filter', 'end_date'),
     Input('category_filter', 'value'),
     Input('region_filter', 'value')]
)
def update_dashboard(start_date, end_date, category, region):

    filtered_df = df.copy()

    # Apply filters
    filtered_df = filtered_df[
        (filtered_df['Order Date'] >= start_date) &
        (filtered_df['Order Date'] <= end_date)
    ]

    if category:
        filtered_df = filtered_df[filtered_df['Category'].isin(category)]

    if region:
        filtered_df = filtered_df[filtered_df['Region'].isin(region)]

    # Sales Overview (Monthly Trend)
    sales_trend = filtered_df.resample('M', on='Order Date')['Sales'].sum().reset_index()
    fig1 = px.line(sales_trend, x='Order Date', y='Sales',
                   title='Sales Overview', markers=True)

    # Region-wise Performance
    region_sales = filtered_df.groupby('Region')['Sales'].sum().reset_index()
    fig2 = px.bar(region_sales, x='Region', y='Sales',
                  title='Region-wise Performance')

    # Profit Analysis
    profit_data = filtered_df.groupby('Category')['Profit'].sum().reset_index()
    fig3 = px.bar(profit_data, x='Category', y='Profit',
                  title='Profit Analysis', color='Profit')

    return fig1, fig2, fig3


# Run app
if __name__ == '__main__':
    app.run(debug=True)