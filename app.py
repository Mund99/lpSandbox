import yfinance as yf
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import json

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Initialize Firebase
cred = credentials.Certificate('secrets/serviceAccountKeyFirebase.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://lee-phoo-sandbox-default-rtdb.asia-southeast1.firebasedatabase.app/'
})


# Create the dashboard layout using Dash's HTML and CSS components
app = dash.Dash(__name__)
server = app.server

app.title = "Lee & Phoo"

# Define the styles for the header and content sections of the dashboard
header_style = {
    'backgroundColor': '#212121',
    'color': '#FFFFFF',
    'padding': '5px',
    'height': '120px',
    'display': 'flex',
    'justifyContent': 'space-between',
    'alignItems': 'center'
}

header_title_style = {
    'margin': '0',
    'fontSize': '50px',
    'fontFamily': 'Arial'
}

header_image_style = {
    'height': '80px',
    'marginLeft': '20px'
}

content_header_style = {
    'marginBottom': '10px',
    'fontFamily': 'Arial',
    'fontSize': '30px'
}

input_div_style = {
    'marginBottom': '10px'
}

submit_button_style = {
    'backgroundColor': '#4CAF50',
    'color': '#FFFFFF',
    'border': 'none',
    'padding': '10px 20px',
    'cursor': 'pointer',
    'borderRadius': '5px',
    'transition': 'background-color 0.5s ease',
}

submit_button_style_hover = {
    'backgroundColor': '#3E8E41',
}

content_style = {
    'padding': '20px',
    'width': '60%',  # Add a width property to the parent container
    'backgroundColor': '#F2F2F2',
    'boxShadow': '0 0 10px rgba(0,0,0,0.1)',
    'borderRadius': '5px',
    'margin': '20px auto'
}

output_graph_style = {
    'display': 'inline'
}


# Create the dashboard layout using Dash's HTML and CSS components
app = dash.Dash()
app.title = "Lee & Phoo"

app.layout = html.Div(children=[
    html.Div([
        html.H1("Lee & Phoo", className="header-title", style=header_title_style),
        html.Img(src="https://content.fortune.com/wp-content/uploads/2018/10/jpmorgan-chase-e1540043145549.jpg",
                 className="header-image", style=header_image_style)
    ], className="header", style=header_style),
    html.Div([
        html.H3('Stock Visualization Dashboard', style=content_header_style),
        html.Div([
            html.H3('Please enter the stock name', style={'fontFamily': 'Arial'}),
            dcc.Input(id="input-ticker", value='',
                      type='text', style={'width': '300px'})
        ], style=input_div_style),
        html.Div([
            html.H3('Please select start and end date', style={'fontFamily': 'Arial'}),
            dcc.DatePickerRange(id='date-picker-range',
                                start_date='2023-01-01',
                                end_date='2023-04-23')
        ], style=input_div_style),
        html.Button('Submit', id='submit-button',
                    n_clicks=0, style=submit_button_style),
        html.Div(id="output-graph", style=output_graph_style)
    ], className="content", style=content_style)
])

# Define the callback function that gets triggered when the user enters a stock name
@app.callback(
    Output(component_id="output-graph", component_property='children'),
    [Input(component_id="submit-button", component_property="n_clicks")],
    [State(component_id="input-ticker", component_property="value"),
     State(component_id='date-picker-range', component_property='start_date'),
     State(component_id='date-picker-range', component_property='end_date')]
)
def update_value(n_clicks, input_ticker, start_date, end_date):
    if not input_ticker:
        return None
    try:
        # Retrieve the stock data using the yfinance library
        stock = yf.Ticker(input_ticker)
        df = stock.history(start=start_date, end=end_date).reset_index()
        df_dict = df.to_dict('records')
        for row in df_dict:
            row['Date'] = row['Date'].strftime('%Y-%m-%d %H:%M:%S')
        # Write the stock data to Firebase Realtime Database
        ref = db.reference('/stocks/' + input_ticker)
        ref.set(df_dict)
        # Return the graph using Dash's dcc.Graph component
        return dcc.Graph(id="demo", figure={'data': [{'x': df.index, 'y': df.Close, 'type': 'line', 'name': input_ticker}, ], 'layout': {'title': input_ticker}})
    except Exception as e:
        # Return any errors that occur during the process
        return str(e)


# Start the Dash app
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0",port=8080)


