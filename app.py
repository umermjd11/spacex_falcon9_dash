from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd

# Read the airline data into pandas dataframe
df_dash = pd.read_csv("falcon9_dash.input.csv")
max_payload = df_dash['Payload Mass (kg)'].max()
min_payload = df_dash['Payload Mass (kg)'].min()

# Extract unique launch sites
unique_launch_sites = df_dash['Launch Site'].unique()

# Create a list of options for the dropdown
launch_site_options = [{'label': 'ALL sites', 'value': 'ALL'}] + \
                      [{'label': site, 'value': site} for site in unique_launch_sites]

# Create a Dash app
app = Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options=launch_site_options,
                                    placeholder="Select a Launch Site",
                                    value='ALL'  # Default value is set to 'ALL'
                                ),
                                html.Br(),

                                # Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=min_payload,
                                    max=max_payload,
                                    step=1000,  # Optional: Define the step size
                                    marks={int(i): f'{int(i)} kg' for i in range(int(min_payload), int(max_payload)+1, 1000)},  # Optional: Add marks at intervals
                                    value=[min_payload, max_payload],  # Default range is the full range of payloads
                                ),

                                # Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])


# Define the callback to update the graph based on the dropdown selection
@app.callback(
    Output('success-pie-chart', 'figure'),
    [Input('site-dropdown', 'value')]
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Step 1: Count the number of successful launches for each site
        success_counts = df_dash[df_dash['class'] == 1].groupby('Launch Site').size().reset_index(name='Successes')

        # Step 2: Calculate the total number of successful launches across all sites
        total_successes = success_counts['Successes'].sum()

        # Step 3: Calculate the success proportion for each site
        success_counts['Success Percentage'] = (success_counts['Successes'] / total_successes) * 100

        # Step 4: Create the pie chart
        fig = px.pie(success_counts, values='Success Percentage', 
                     names='Launch Site', 
                     title='Total Success Percentage by Launch Site')
        return fig
    else:
        # For the second chart (Specific site)
        site_data = df_dash[df_dash['Launch Site'] == entered_site]
        
        # Calculate total launches and successful launches for the selected site
        total_launches = site_data.shape[0]
        successful_launches = site_data['class'].sum()
        
        # Calculate success percentage
        success_percentage = (successful_launches / total_launches) * 100
        failure_percentage = 100 - success_percentage
        
        # Create a DataFrame for plotting
        site_success_data = pd.DataFrame({
            'Outcome': ['Success', 'Failure'],
            'Percentage': [success_percentage, failure_percentage]
        })

        fig = px.pie(site_success_data, values='Percentage', 
                     names='Outcome', 
                     color='Outcome',
                     color_discrete_map={'Success': 'green', 'Failure': 'red'},
                     title=f'Success Rate for {entered_site} Launch Site')
        return fig


# Define the callback to update the graph based on the dropdown selection
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('payload-slider', 'value'), Input(component_id='site-dropdown', component_property='value')]
)
def get_scatter_chart(payload_range, entered_site):
    if entered_site == 'ALL':
        filtered_df_dash = df_dash
        tailored_title =  "Scatter Plot of Launches: Payload Mass vs. Class with Booster Version Category Highlighted"
    else:
        filtered_df_dash = df_dash[df_dash['Launch Site'] == entered_site]
        tailored_title = f"Scatter Plot of Launches for {entered_site}: Payload Mass vs. Class with Booster Version Category Highlighted"

    filtered_df_dash = filtered_df_dash[ (filtered_df_dash['Payload Mass (kg)'] >= payload_range[0]) & (filtered_df_dash['Payload Mass (kg)'] <= payload_range[1])]
    fig = px.scatter(filtered_df_dash, x='Payload Mass (kg)', y='class', 
                     color='Booster Version Category', 
                     title = tailored_title,         
                     hover_data={
                        'Flight Number': True,
                        'Launch Site': True,
                        'Payload Mass (kg)': True, 'Booster Version' : True,
                        'class': True  
                    } 
            )
        
    return fig




# Run the Dash app
app.run_server(debug=False)