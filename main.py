"""
Name:   Ethan Harrison
CS230:  Section 4.FA21
Data:   LondonAirBnBSep2021
URL:
"""

# This file reads the file with AirBnb data and describes the data in several ways
# First, it provides some general statistics about the data
# Next, it provides 3 charts about the data, one of which is based on user input
# specifying the price range to describe the data
# Finally, it presents 2 different maps. One of them is based on the number
# of nights the user wants to stay and the type of room they want.
# The second map is provided based on price range that the user
# wants to stay in and the specific neighbourhood(s) they want to stay in.
# In this section, a csv file of the houses that describe the user input
# is created and available for download.

# Besides in-class activities, I used the following websites to
# https://docs.streamlit.io/
# https://matplotlib.org/

import pandas as pd
import streamlit as st
import numpy as np
import pydeck as pdk
import matplotlib.pyplot as plt
from PIL import Image


# Turns the csv file into a data frame
def read_data(source):
    return pd.read_csv(source, low_memory=False)


def stat_lines(df):

    num_houses = len(df.index)
    st.markdown(f"<p style='text-align: left; color: white; font-size: 32px;'>Total number of houses: {num_houses}</p>", unsafe_allow_html=True)

    max_value = df['price'].max()
    st.markdown(f"<p style='text-align: left; color: white; font-size: 32px;'>Highest nightly price: ${max_value}</p>", unsafe_allow_html=True)

    min_value = df['price'].min()
    st.markdown(f"<p style='text-align: left; color: white; font-size: 32px;'>Lowest nightly price: ${min_value}</p>", unsafe_allow_html=True)

    unique_neighbourhood = len(pd.unique(df['neighbourhood']))
    st.markdown(f"<p style='text-align: left; color: white; font-size: 32px;'>Total neighbourhoods with AirBnBs available: {unique_neighbourhood}</p>", unsafe_allow_html=True)

    avg_price = df['price'].mean()
    st.markdown(f"<p style='text-align: left; color: white; font-size: 32px;'>Average nightly price: ${avg_price.round(2)}</p>", unsafe_allow_html=True)


# Creates a histogram that shows houses organized by price
# within a range specified by user
def hist_by_price(df, values):
    difference = values[1]-values[0]

    column1 = len((df[(df['price'] >= values[0]) & (df['price'] <= values[0] + int(difference/4))]))
    column2 = len((df[(df['price'] > values[0] + int(difference/4)) & (df['price'] <= values[0] + int(difference/2))]))
    column3 = len((df[(df['price'] > values[0] + int(difference/2)) & (df['price'] <= values[1] - int(difference/4))]))
    column4 = len((df[(df['price'] > values[1] - int(difference/4)) & (df['price'] <= values[1])]))
    x_axis = [values[0], values[0] + int(difference/4), values[0] + int(difference/2),
              values[1] - int(difference/4), values[1]]
    y_axis = [column1, column2, column3, column4, 0]
    plt.figure(1)
    plt.subplot(211)
    bar = plt.bar(x_axis, y_axis, width=250, align='edge', color=['black', 'red', 'green', 'blue', 'cyan'])
    plt.xlabel("Nightly Prices")
    plt.ylabel("Number of Houses")
    plt.title("Number of Houses in Specified House Range")
    plt.xticks(rotation=90)
    return plt


# Creates a pie chart based on the different types of rooms available
# for the user
def roomtype_pie(df):
    counts = list(df['room_type'].value_counts())
    x_axe = df['room_type'].unique()

    explode = (0.0, 0.0, 0.5, 0.5)
    plt.figure(3)
    plt.figure(213)
    pie = plt.pie(counts, autopct='%1.2f%%', pctdistance=1.2, explode=explode)
    plt.legend(x_axe, loc='best', ncol=1)
    plt.title("Percentages of Houses by Neighbourhood")
    return plt


# Creates a dictionary that is organized by neighbourhood and contains
# All of the nightly prices for each neighbourhood
def neighbourhood_price(df):
    prices = [row['price'] for ind, row in df.iterrows()]
    neighbourhoods = [row['neighbourhood'] for ind, row in df.iterrows()]
    dict = {}
    for neighbourhood in neighbourhoods:
        dict[neighbourhood] = []
    for i in range(len(prices)):
        dict[neighbourhoods[i]].append(prices[i])
    return dict


# Creates a dictionary of all of the neighbourhoods
# with the average prices of each neighbourhood
def neighbourhood_average(dict_prices):
    dict = {}
    for key in dict_prices.keys():
        dict[key] = np.mean(dict_prices[key])
    return dict


# Creates a bar chart of the average prices in all of the neighbourhoods
def gen_bar_chart(dict):
    x = dict.keys()
    y = dict.values()
    plt.figure(2)
    plt.subplot(212)
    bar2 = plt.bar(x, y, color=['black', 'red', 'green', 'blue', 'cyan'])
    plt.xlabel("Neighbourhood")
    plt.ylabel("Average Price")
    plt.title("Average Nightly Price by Neighbourhood")
    plt.xticks(rotation=90)
    return plt


# Filters a dataframe by the minimum number of
# nights and by the type of room
def both_filter(df,room_type,night=1):
    result = df[(df['minimum_nights'] <= night) &
                (df['room_type'].isin(room_type))]
    return result


# Filters a dataframe by a specified price range
# and neighbourhoods
def filter_price_neighbourhood(df,low_price,up_price,neighbourhood):
    result = df[(df['price'] >= low_price) & (df['price'] <= up_price) &
                (df['neighbourhood'].isin(neighbourhood))]
    result = result.sort_values(['price'], ascending=True)
    return result


# Converts a dataframe to a csv file
def convert_df(df):
     return df.to_csv().encode('utf-8')


# Presents a download button for a csv file
def show_download(c):
    st.download_button(
             label="Download them here!",
             data=c,
             file_name='home_file.csv',
             mime='text/csv',
         )


# Maps a dataframe and shows the name and price of each house
def map_both_filter(df,z):
    # Broke the argument 'df' into two separate dataframes in order to
    # Remove emojis from the 'name' column of df because streamlit
    # couldn't process the emoji values when mapping the data frame
    map_df = df.filter(['latitude','longitude','price'])
    map_df_names = df.filter(['name'])
    new_df = df[['latitude', 'longitude','price']]

    # The source code and icon data for using a house emoji as the layer
    # I used this website to figure out how to do this:
    # https://pydeck.gl/gallery/icon_layer.html
    icon_source = "https://upload.wikimedia.org/wikipedia/commons/f/f2/Noto_Emoji_Oreo_1f3e1.svg"
    icon_data = {
        "url": icon_source,
        "width": 242,
        "height": 242,
        "anchorY": 242,
    }
    if map_df.empty:
        st.markdown(f"<p style='text-align: center; color: white; font-size: 32px;'>Provide input on the sidebar to generate your map!</p>", unsafe_allow_html=True)
    else:
        view_state = pdk.ViewState(
                                   latitude=map_df["latitude"].mean(),
                                   longitude=map_df["longitude"].mean(),
                                    zoom=z,
                                    pitch=0)

        # These two lines of code took a while to get to. This was a tricky
        # thing to figure out
        # Removes the emojis from the 'name' column and recombines the
        # two dataframes to be ready to map
        map_df_names = map_df_names.astype(str).apply(lambda x: x.str.encode('ascii', 'ignore').str.decode('ascii'))
        new_df['name'] = map_df_names['name'].values

        # Adding the icon data into each entry in the data frame
        new_df["icon_data"] = None
        for i in new_df.index:
            new_df["icon_data"][i] = icon_data

        layer1 = pdk.Layer('IconLayer',
                          data =new_df,
                          get_position='[longitude, latitude]',
                          get_icon="icon_data",
                          get_size=2,
                          size_scale=15,
                          pickable=True
                          )

        tool_tip = {"html": "Name of House:<br/> <b>{name}</br> "
                            "<b>Price Per Night:<br/> <b>${price}</br>",
                    "style": {"backgroundColor": "steelblue",
                              "color": "white"}
                    }

        map = pdk.Deck(
            map_style='mapbox://styles/mapbox/outdoors-v11',
            initial_view_state=view_state,
            layers=[layer1],
            tooltip=tool_tip
        )

        st.pydeck_chart(map)


def main():
    # Creates and posts the AirBnb logo as a header
    image = Image.open('AirBnb Header.png')
    st.image(image, width=600)
    #main_bg = "house emoji.jpg"
    #main_bg_ext = "jpg"
    st.markdown("<h1 style='text-align: center; color: #FF5A5F;'>London AirBnB Data</h1>", unsafe_allow_html=True)

    st.markdown(
        """
        <style>
        .reportview-container .markdown-text-container {
            font-family: monospace;
        }
        .sidebar .sidebar-content {
            background-image: linear-gradient(#FF5A5F,#FF5A5F);
            color: white;
        }
        .Widget>label {
            color: white;
            font-family: monospace;
        }
        [class^="st-b"] {
            color: white;
            font-family: monospace;
        }
        .st-bb {
            background-color: transparent;
        }
        .st-at {
            background-color: #FF5A5F;
        }
        footer {
            font-family: monospace;
        }
        
        .reportview-container {
            background: url("house emoji.jpeg")
        }
        header .decoration {
            background-image: none;
        }
        
        </style>
        """,
            unsafe_allow_html=True,
    )

    # Specifies name of source of data and reads data into a dataframe
    data_source = "LondonAirBnBSep2021.csv"
    data_frame = read_data(data_source)


    st.subheader("General stats about the data :house:")



    with st.expander("See here"):
        stat_lines(data_frame)

    # Expander minimizes section of graphs

    st.subheader("Charts/Graphs describing data :house:")
    with st.expander("See here"):
        st.sidebar.title("Input for Chart #1:")
        value = st.sidebar.slider('Select a range of nightly prices',int(data_frame.price.min()),int(data_frame.price.max()),(int(data_frame.price.min()),int(data_frame.price.max())))
        st.sidebar.write("")
        st.sidebar.write("")
        st.sidebar.write("")
        # Calls Two Functions Described Above and writes bar charts to streamlit
        st.markdown("<h1 style='text-align: center; color: white;'>Chart #1</h1>", unsafe_allow_html=True)

        st.markdown(f"<p style='text-align: center; color: white; font-size: 32px;'>This is a bar chart describing the number of houses that are available"
                 " within a certain price range that is specified in the sidebar</p>", unsafe_allow_html=True)

        hist_frame = hist_by_price(data_frame,value)
        st.pyplot(hist_frame)



        # Creates and plots a pie chart of the percentages of houses
        pies = roomtype_pie(data_frame)
        st.markdown("<h1 style='text-align: center; color: white;'>Chart #2</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: white; font-size: 32px;'>This is a pie chart describing the percentages of the 4 different"
                 " types of AirBnB rooms available</p>", unsafe_allow_html=True)

        st.pyplot(pies)
        # Calls functions defined above to generate a bar
        # chart of average prices by neighborhood
        prices = neighbourhood_price(data_frame)
        averages = neighbourhood_average(prices)
        st.markdown("<h1 style='text-align: center; color: white;'>Chart #3</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: white; font-size: 32px;'>This is a bar chart describing the average nightly price"
                 " in all of the neighbourhoods that AirBnBs are offered</p>", unsafe_allow_html=True)
        st.pyplot(gen_bar_chart(averages))

    st.subheader("Map #1 :house:")
    with st.expander("See here"):
        # Gathers input needed in order to call the
        st.sidebar.title("Input for Map #1")
        nights = st.sidebar.number_input("Pick the number of nights you would like to stay", min_value=int(data_frame.minimum_nights.min()), max_value=int(data_frame.minimum_nights.max()),value=1,key=0)
        room_type = st.sidebar.multiselect("Pick the type(s) of room(s) you would like to stay in", data_frame['room_type'].unique())
        zoom = st.sidebar.slider("Pick the level of zoom for the map", min_value=1,max_value=20,key=0)
        st.sidebar.write("")
        st.sidebar.write("")
        st.sidebar.write("")

        st.markdown(f"<p style='text-align: center; color: white; font-size: 32px;'>This is a map of the houses that are available based on the number"
                 " of nights you want to stay in the AirBnB and the type of room that"
                 " you want to stay in</p>", unsafe_allow_html=True)

        # Uses input to filter data and calls the function to map
        # the filtered data frame
        filtered_frame = both_filter(data_frame,room_type,nights)

        map_both_filter(filtered_frame,zoom)

    st.subheader("Map #2 :house:")
    with st.expander("See here"):
        # Gathers input to and calls function to filter the data
        # frame by price range and selected neighbourhoods
        st.sidebar.title("Input for Map #2")
        lower_price = st.sidebar.number_input("Pick the lowest nightly rate you would like to pay", min_value=int(data_frame.price.min()), max_value=int(data_frame.price.max()),value=1,key=1)
        upper_price = st.sidebar.number_input("Pick the highest nightly rate you would like to pay", min_value=int(data_frame.price.min()), max_value=int(data_frame.price.max()),value=1,key=2)
        neighbourhoods = st.sidebar.multiselect("Pick the neighbourhood(s) you would like to stay in", data_frame['neighbourhood'].unique())
        filtered_frame_2 = filter_price_neighbourhood(data_frame,lower_price,upper_price,neighbourhoods)



        # Shows a map of the filtered data frame based on the input
        # provided by user
        st.markdown(f"<p style='text-align: center; color: white; font-size: 32px;'>This is a map of the houses that are available based on the price "
                 " range that you specify and in the neighbourhoods that you select</p>", unsafe_allow_html=True)

        zoom_2 = st.sidebar.slider("Pick the level of zoom for the map", min_value=1,max_value=20,key=1)
        map_both_filter(filtered_frame_2,zoom_2)

        # Counts the number of houses in the new data frame and writes it into Streamlit
        frame_count = filtered_frame_2['id'].count()
        st.markdown(f"<p style='text-align: left; color: white; font-size: 16px;'>There are " + str(frame_count) +
                    " houses that fit your chosen criteria</p>", unsafe_allow_html=True)

        # Converts the filtered data frame into a csv file that is
        # available for download by the user
        csv = convert_df(filtered_frame_2)
        show_download(csv)

main()
