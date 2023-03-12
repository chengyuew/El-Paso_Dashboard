import streamlit as st
import pandas as pd
import folium
import altair as alt
import numpy as np
from datetime import datetime
from streamlit_folium import folium_static
from folium.plugins import HeatMap
import random

# Load the data
crash_data = pd.read_csv('crash_data.csv')
covid_data = pd.read_csv('covid_data.csv')
traffic_data = pd.read_csv('traffic_data.csv')

# Set up the Streamlit app
#st.title('El Paso Data Dashboard')
# Set up the Streamlit app
st.set_page_config(page_title='El Paso Data Dashboard', page_icon=':bar_chart:')
st.title('El Paso Data Dashboard')

# Add a dropdown to allow the user to select a data module
# data_module = st.sidebar.selectbox('Select a data module', ['Crash Data', 'Traffic Data', 'Health Data'])

# Add a radio button group to allow the user to select a data module
data_module = st.radio('Select a data module', ['Crash Data 🚗', 'Traffic Data 🚦', 'Health Data 🏥'])

# Define a dictionary of icons for each data module option
# icons = {
#     'Crash Data': '🚗',
#     'Traffic Data': '🚦',
#     'Health Data': '🏥',
# }

# # Add a selectbox to allow the user to select a data module
# data_module = st.selectbox('Select a data module', ['Crash Data', 'Traffic Data', 'Health Data'], format_func=lambda x: icons[x]+' '+x)

if data_module == 'Crash Data 🚗':
    # Set default values for start_date and end_date
    default_start_date = pd.to_datetime('2020-01-01')
    default_end_date = pd.to_datetime('2020-03-01')

    # Add a slider to allow the user to select a time frame
    start_date = st.sidebar.date_input('Start date', default_start_date)
    end_date = st.sidebar.date_input('End date', default_end_date)

    # Add options to select the type of map display
    map_type = st.sidebar.selectbox('Map Display', ['Marker Cluster', 'Heatmap', 'Markers'])

    # Add options to filter by crash severity
    crash_severity = st.sidebar.selectbox('Crash Severity', ['TOTAL','NOT INJURED', 'SUSPECTED MINOR INJURY', 
                                                            'POSSIBLE INJURY', 'SUSPECTED SERIOUS INJURY', 'FATAL INJURY', 'UNKNOWN'])

    crash_data['Crash Date'] = pd.to_datetime(crash_data['Crash Date'], format='%m/%d/%Y')

    # Filter the data based on the user's selection
    filtered_data = crash_data[(crash_data['Crash Date'] >= pd.Timestamp(start_date)) & (crash_data['Crash Date'] <= pd.Timestamp(end_date))]

    if crash_severity != 'TOTAL':
        filtered_data = filtered_data[filtered_data['Crash Severity'] == crash_severity]

    # Create a map using Folium
    m = folium.Map(location=[31.7619, -106.4850], zoom_start=11)

    # Add markers to the map for each crash in the filtered data
    #for index, row in filtered_data.iterrows():
    #    lat = row['Crash Latitude']
    #    lon = row['Crash Longitude']
    #    marker = folium.Marker([lat, lon])
    #    marker.add_to(m)
    # Add markers, heatmap, or marker clusters to the map based on user selection

    # st.sidebar.subheader('Authors:')
    # st.sidebar.write('- Kelvin Cheu')
    # st.sidebar.write('- Ruimin Ke')
    # st.sidebar.write('- Chengyue Wang')
    # st.sidebar.write('- Swapnil Samat')
    # st.sidebar.write('- Jeffrey Weidner') 
    st.sidebar.image('utep-miners-logo.png', width=200)

    if map_type == 'Markers':
        for index, row in filtered_data.iterrows():
            lat = row['Crash Latitude']
            lon = row['Crash Longitude']
            marker = folium.Marker([lat, lon])
            marker.add_to(m)
    elif map_type == 'Heatmap':
        data = filtered_data[['Crash Latitude', 'Crash Longitude']].values.tolist()
        folium.plugins.HeatMap(data).add_to(m)
    else:
        from folium.plugins import MarkerCluster
        marker_cluster = MarkerCluster()
        for index, row in filtered_data.iterrows():
            lat = row['Crash Latitude']
            lon = row['Crash Longitude']
            marker = folium.Marker([lat, lon])
            marker_cluster.add_child(marker)
        marker_cluster.add_to(m)

    # Display the map in the Streamlit app
    folium_static(m)

elif data_module == 'Traffic Data 🚦':
    # Filter the data by date and time
    #date = st.date_input('Select a date', min_value=traffic_data['capturedtimestamp'].min().date(), max_value=traffic_data['capturedtimestamp'].max().date())
    #time = st.time_input('Select a time')
    # Speed-based pattern analysis
    traffic_data['postalcode'].replace([np.nan, np.inf, -np.inf], 0, inplace=True)
    traffic_data['postalcode'] = traffic_data['postalcode'].astype(int)

    zip_code = st.sidebar.selectbox('Select a zip code', sorted(traffic_data['postalcode'].unique()))
    # if zip_code == -1:
    #     zip_code = 'All'
    if zip_code != 0:
        traffic_data = traffic_data[traffic_data['postalcode'] == zip_code]

    # st.sidebar.subheader('Authors:')
    # st.sidebar.write('- Kelvin Cheu')
    # st.sidebar.write('- Ruimin Ke')
    # st.sidebar.write('- Chengyue Wang')
    # st.sidebar.write('- Swapnil Samat')
    # st.sidebar.write('- Jeffrey Weidner') 
    st.sidebar.image('utep-miners-logo.png', width=200)

    st.subheader('Speed-based Pattern Analysis')
    speed_threshold = st.slider('Select a speed threshold', min_value=0, max_value=120, step=5, value=50)
    speed_df = traffic_data[traffic_data['speed'] >= speed_threshold]
    if len(speed_df) > 0:
        st.write('Number of datapoints:', len(speed_df))
        st.write(speed_df)
        st.write('Average speed:', speed_df['speed'].mean())
        st.write('Max speed:', speed_df['speed'].max())
        st.write('Min speed:', speed_df['speed'].min())
        st.write('Standard deviation:', speed_df['speed'].std())


    else:
        st.write('No datapoints above the speed threshold')

    # Density analysis
    st.subheader('Density Heatmap (Zoom in for better visualization)')
    m = folium.Map(location=[31.771959, -106.438233], zoom_start=10)
    data = traffic_data[['latitude', 'longitude']].values.tolist()
    HeatMap(data).add_to(m)
    folium_static(m)

    # Trajectory analysis based on journeyid
    st.subheader('Trajectory Visualization')
    m2 = folium.Map(location=[31.771959, -106.438233], zoom_start=10)
    colors = ['blue','red','green','purple','black','gray','yellow']
    grouped = traffic_data.groupby(by='journeyid')
    for name, group in grouped:
        original_points = [group['latitude'].tolist(), group['longitude'].tolist()]
        points = [list(row) for row in zip(*original_points)]
        folium.PolyLine(points, color=colors[random.randrange(0,len(colors))], weight=4, opacity=0.75).add_to(m2)
    folium_static(m2)
    # journeyids = traffic_data['journeyid'].unique()
    # selected_journeyid = st.selectbox('Select a journeyid', ['All'] + list(journeyids))
    # if selected_journeyid != 'All':
    #     journey_df

elif data_module == 'Health Data 🏥':
    # Set default values for start_date and end_date
    default_start_date = pd.to_datetime('2021-01-01')
    default_end_date = pd.to_datetime('2021-06-30')

    # Add a slider to allow the user to select a time frame
    start_date = st.sidebar.date_input('Start date', default_start_date)
    end_date = st.sidebar.date_input('End date', default_end_date)

    # Filter the data based on the user's selection
    covid_data['date'] = pd.to_datetime(covid_data['date'], format='%m/%d/%Y')
    filtered_data = covid_data[(covid_data['date'] >= pd.Timestamp(start_date)) & (covid_data['date'] <= pd.Timestamp(end_date))]

    grouped_data = filtered_data.groupby('zip code').sum()[['cumulative positive cases', 'cumulative recoveries', 'cumulative deaths']]

    # Reset the index to make zip code a column
    grouped_data = grouped_data.reset_index()

    # Filter the data based on the user's selection
    zip_code = st.sidebar.selectbox('Select a zip code', sorted(covid_data['zip code'].unique()))
    filtered_zip_data = filtered_data[filtered_data['zip code'] == zip_code]

    # Set the date column as the index of the DataFrame
    #filtered_zip_data = filtered_zip_data.set_index('date')

    # Create a line chart of the total positive cases, recoveries, and deaths over time
    variable = st.sidebar.selectbox('Data Display', ['cumulative positive cases', 'cumulative recoveries', 'cumulative deaths'])

    # st.sidebar.subheader('Authors:')
    # st.sidebar.write('- Kelvin Cheu')
    # st.sidebar.write('- Ruimin Ke')
    # st.sidebar.write('- Chengyue Wang')
    # st.sidebar.write('- Swapnil Samat')
    # st.sidebar.write('- Jeffrey Weidner') 
    st.sidebar.image('utep-miners-logo.png', width=200)

    chart = alt.Chart(filtered_zip_data).mark_line().encode(
        x='date:T',
        y=alt.Y(variable + ':Q', stack=True),
        color='variable:N'
    ).properties(
        title=f'The {variable} over selected time range for zip code {zip_code}',
        width=800,
        height=400
    )

    # Display the line chart in the Streamlit app using altair_chart
    st.altair_chart(chart)

    # Create a table of the total positive cases, recoveries, and deaths by zip code
    st.markdown('### Total Cases by Zip Code from ' + str(start_date) + ' to ' + str(end_date))
    #pd.set_option('display.max_colwidth', 100)
    # Set the width of each column to 150 pixels
    #styles = [dict(selector="th", props=[("max-width", "150px")])]
    st.write(grouped_data) 


    # # Set default values for start_date and end_date
    # default_start_date = pd.to_datetime('2021-01-01')
    # default_end_date = pd.to_datetime('2021-03-31')

    # # Add a slider to allow the user to select a time frame
    # start_date = st.sidebar.date_input('Start date', default_start_date)
    # end_date = st.sidebar.date_input('End date', default_end_date)

    # # Add options to select the zip code
    # zip_code = st.sidebar.selectbox('Zip Code', [79901, 79902, 79903, 79904, 79905, 79907, 79911, 79912, 79915, 
    #                                              79922, 79924, 79925, 79927, 79928, 79930, 79932, 79934, 79935, 79936, 79938])
    # # Add options to select the type of map display
    # display_type = st.sidebar.selectbox('Data Display', ['Positive Cases', 'Recoveries', 'Deaths'])

    # # Data filtering
    # covid_data['date'] = pd.to_datetime(covid_data['date'], format='%m/%d/%Y')
    # filtered_data = covid_data[(covid_data['date'] >= start_date) & (covid_data['date'] <= end_date)]
    # if zip_code != 'ALL':
    #     filtered_data = filtered_data[filtered_data['zip code'] == zip_code]
    

    

    
