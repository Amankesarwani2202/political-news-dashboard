import pandas as pd
import plotly.express as px
import streamlit as st

def render_bias_plot(df):
    count_df = df.groupby(['topic_name', 'bias']).size().reset_index(name='count')

    fig = px.bar(
        count_df,
        x='count',
        y='topic_name',
        color='bias',
        orientation='h',
        title='🧠 Interactive Bias Chart per Topic',
        color_discrete_map={
            "Left": "#e74c3c",
            "Left-Center": "#3498db",
            "Center-Left": "#f39c12",
            "Center": "#2ecc71",
            "Right": "#9b59b6",
            "Right-Center": "#e67e22"
        },
        height=600
    )
    fig.update_layout(
        yaxis_title='Topics',
        xaxis_title='Count',
        legend_title='Bias',
        plot_bgcolor='#f8f9fa',
        paper_bgcolor='#f8f9fa',
    )
    st.plotly_chart(fig, use_container_width=True)
