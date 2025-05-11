"""
Institution visualizations for the Pathfinder application.
"""

import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_data(ttl=300)
def plot_control_type_distribution(filtered_data):
    """
    Create a bar chart showing the distribution of university control types.
    """
    st.markdown("#### University Count by Control Type", help="Distribution of institutions by type (Public, Private Non-Profit, Private For-Profit).")
    plot_data = filtered_data.dropna(subset=['CONTROL_TYPE'])

    if not plot_data.empty:
        control_counts = plot_data['CONTROL_TYPE'].value_counts().reset_index()
        control_counts.columns = ['CONTROL_TYPE', 'count']

        fig = px.bar(
            control_counts,
            x='CONTROL_TYPE',
            y='count',
            title="Distribution of Control Types",
            labels={'CONTROL_TYPE': 'Control Type', 'count': 'Number of Universities'},
            color='CONTROL_TYPE',
            text='count'  # Add count labels on bars
        )
        
        fig.update_traces(texttemplate='%{text}', textposition='outside')
        
        fig.update_layout(
            xaxis_title="Control Type",
            yaxis_title="Number of Universities",
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Insufficient data for Control Type distribution plot.")

@st.cache_data(ttl=300)
def plot_institution_size_distribution(filtered_data):
    """
    Create a bar chart showing the distribution of institution sizes by control type.
    """
    st.markdown("#### Institution Size Distribution", help="Distribution of institutions by size category and type.")
    plot_data = filtered_data.dropna(subset=['UGDS', 'CONTROL_TYPE'])
    
    if not plot_data.empty:
        # Create a copy to avoid SettingWithCopyWarning
        plot_data = plot_data.copy()
        
        # Create size categories
        plot_data.loc[:, 'Size Category'] = pd.cut(
            plot_data['UGDS'],
            bins=[0, 1000, 5000, 15000, 30000, float('inf')],
            labels=['Very Small (<1K)', 'Small (1K-5K)', 'Medium (5K-15K)', 'Large (15K-30K)', 'Very Large (>30K)']
        )

        # Count universities by control type and size category
        size_counts = plot_data.groupby(['CONTROL_TYPE', 'Size Category']).size().reset_index(name='count')

        # Create the grouped bar chart
        fig = px.bar(
            size_counts,
            x='CONTROL_TYPE',
            y='count',
            color='Size Category',
            title="Institution Size Distribution by Control Type",
            labels={
                'CONTROL_TYPE': 'Institution Type',
                'count': 'Number of Universities',
                'Size Category': 'Size Category'
            },
            barmode='group',
            category_orders={
                'Size Category': ['Very Small (<1K)', 'Small (1K-5K)', 'Medium (5K-15K)', 'Large (15K-30K)', 'Very Large (>30K)']
            }
        )
        
        fig.update_layout(
            xaxis_title="Institution Type",
            yaxis_title="Number of Universities",
            legend_title="Size Category"
        )
        
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("Insufficient data for Institution Size distribution plot.")
