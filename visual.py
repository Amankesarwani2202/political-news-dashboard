import pandas as pd
import plotly.express as px
import streamlit as st

def render_bias_plot(df, topic_column='clean_topic'):
    if df.empty:
        st.warning("No data available for visualization.")
        return

    # Group by topic and bias
    grouped = df.groupby([topic_column, 'bias']).size().reset_index(name='count')

    fig = px.bar(
        grouped,
        x=topic_column,
        y='count',
        color='bias',
        barmode='group',
        title="🧠 Interactive Bias Chart per Topic",
        color_discrete_sequence=px.colors.qualitative.Set1,
    )

    fig.update_layout(
        xaxis_title="Topics",
        yaxis_title="Count",
        xaxis_tickangle=45,
        title_x=0.5,
        font=dict(size=14),
        legend_title="Bias"
    )

    st.plotly_chart(fig, use_container_width=True)
