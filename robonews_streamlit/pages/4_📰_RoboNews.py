import plotly.graph_objects as go
import pandas as pd
import streamlit as st


def retrieve_sentiment():

    """"""

    overall_sentiment = "It's Great!"

    return overall_sentiment


def create_plot(stock_df):

    """"""

    fig = go.Figure()

    fig.add_trace(go.Scatter(

        x=stock_df.datetime,
        y=stock_df['close'],
        name='Close Price Over Time',
        line=dict(color='green'),
        yaxis='y2',
        mode='lines'
    ))

    # Update layout with appropriate y-axis ranges
    fig.update_layout(

        title='Daily Close Price Over Time',
        xaxis_title='Date',
        yaxis=dict(
            title='Y AXIS TITLE'
        ),

        template='plotly_dark'
    )

    st.plotly_chart(fig)


st.sidebar.title("Predicting Stock Prices by News Sentiment")
ticker = st.sidebar.text_input("Enter stock ticker (e.g., NFLX):", value='NFLX')

run_button = st.sidebar.button("Run Analysis")

if run_button:

    # will actually pull from db - need to check on performance of this & remember cache etc
    stock_df = pd.read_csv(r'C:\Users\david\repos\RoboNewsStreamlit\robonews_streamlit\assets\NFLX_last_five_years.csv')

    more_text_info = "NFLX is smashing it!"
    st.write(f'SOME TEXT INFORMATION {more_text_info}')

    # have published news scrolling and appearing instantly

    create_plot(stock_df)
