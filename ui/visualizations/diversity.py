"""
Diversity visualizations for the Pathfinder application.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config import DIVERSITY_MAPPING, STAFF_DIVERSITY_MAPPING, GENDER_MAPPING

@st.cache_data(ttl=300)
def plot_diversity_composition(filtered_data):
    """
    Create a bar chart showing average undergraduate diversity composition.
    """
    st.markdown("#### Average Undergraduate Racial/Ethnic Diversity", help="Average racial and ethnic composition of undergraduate students across institutions.")
    diversity_cols = ['UGDS_WHITE', 'UGDS_BLACK', 'UGDS_HISP', 'UGDS_ASIAN',
                      'UGDS_AIAN', 'UGDS_NHPI', 'UGDS_2MOR', 'UGDS_NRA', 'UGDS_UNKN']

    if all(col in filtered_data.columns for col in diversity_cols):
        avg_diversity = filtered_data.dropna(subset=diversity_cols)[diversity_cols].mean().reset_index()
        avg_diversity.columns = ['Race/Ethnicity', 'Average Proportion']
        avg_diversity['Race/Ethnicity'] = avg_diversity['Race/Ethnicity'].map(DIVERSITY_MAPPING)
        avg_diversity['Category'] = 'Average Composition'

        if not avg_diversity.empty:
            fig = px.bar(
                avg_diversity,
                x='Category',
                y='Average Proportion',
                color='Race/Ethnicity',
                title="Avg. Undergraduate Racial/Ethnic Composition",
                labels={'Average Proportion': 'Proportion', 'Race/Ethnicity': 'Race/Ethnicity'},
                text='Average Proportion'
            )
            fig.update_layout(
                xaxis_title=None,
                yaxis_title="Average Proportion",
                xaxis={'visible': False},
                yaxis_tickformat=".1%",
                legend_title_text='Race/Ethnicity'
            )
            fig.update_traces(texttemplate='%{text:.1%}', textposition='inside')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Could not calculate average diversity for current filters.")
    else:
        st.info("Diversity data columns not available in the dataset.")

@st.cache_data(ttl=300)
def plot_diversity_comparison_by_control(filtered_data):
    """
    Create a grouped bar chart comparing diversity across institution types.
    """
    st.markdown("#### Diversity by Institution Type", help="Comparison of racial and ethnic diversity across different types of institutions.")
    diversity_cols = ['UGDS_WHITE', 'UGDS_BLACK', 'UGDS_HISP', 'UGDS_ASIAN',
                      'UGDS_AIAN', 'UGDS_NHPI', 'UGDS_2MOR', 'UGDS_NRA', 'UGDS_UNKN']

    if all(col in filtered_data.columns for col in diversity_cols) and 'CONTROL_TYPE' in filtered_data.columns:
        # Group by control type and calculate average diversity
        grouped_data = filtered_data.groupby('CONTROL_TYPE')[diversity_cols].mean().reset_index()
        
        # Melt the data for plotting
        melted_data = pd.melt(
            grouped_data, 
            id_vars=['CONTROL_TYPE'],
            value_vars=diversity_cols,
            var_name='Race/Ethnicity',
            value_name='Average Proportion'
        )
        
        # Map column names to readable labels
        melted_data['Race/Ethnicity'] = melted_data['Race/Ethnicity'].map(DIVERSITY_MAPPING)
        
        if not melted_data.empty:
            fig = px.bar(
                melted_data,
                x='CONTROL_TYPE',
                y='Average Proportion',
                color='Race/Ethnicity',
                title="Diversity Comparison by Institution Type",
                labels={
                    'CONTROL_TYPE': 'Institution Type',
                    'Average Proportion': 'Average Proportion',
                    'Race/Ethnicity': 'Race/Ethnicity'
                },
                barmode='group'
            )
            
            fig.update_layout(
                xaxis_title="Institution Type",
                yaxis_title="Average Proportion",
                yaxis_tickformat=".1%",
                legend_title="Race/Ethnicity"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Could not calculate diversity by institution type for current filters.")
    else:
        st.info("Diversity data or institution type not available in the dataset.")

@st.cache_data(ttl=300)
def plot_staff_diversity_composition(filtered_data):
    """
    Create a bar chart showing average staff diversity composition.
    """
    st.markdown("#### Average Staff Racial/Ethnic Diversity", help="Average racial and ethnic composition of staff across institutions.")
    staff_diversity_cols = ['IRPS_WHITE', 'IRPS_BLACK', 'IRPS_HISP', 'IRPS_ASIAN',
                           'IRPS_AIAN', 'IRPS_NHPI', 'IRPS_2MOR', 'IRPS_NRA', 'IRPS_UNKN']

    if all(col in filtered_data.columns for col in staff_diversity_cols):
        # Check if we have any non-null data
        if filtered_data[staff_diversity_cols].notna().any().any():
            avg_diversity = filtered_data.dropna(subset=staff_diversity_cols, how='all')[staff_diversity_cols].mean().reset_index()
            avg_diversity.columns = ['Race/Ethnicity', 'Average Proportion']
            avg_diversity['Race/Ethnicity'] = avg_diversity['Race/Ethnicity'].map(STAFF_DIVERSITY_MAPPING)
            avg_diversity['Category'] = 'Average Composition'

            if not avg_diversity.empty:
                fig = px.bar(
                    avg_diversity,
                    x='Category',
                    y='Average Proportion',
                    color='Race/Ethnicity',
                    title="Avg. Staff Racial/Ethnic Composition",
                    labels={'Average Proportion': 'Proportion', 'Race/Ethnicity': 'Race/Ethnicity'},
                    text='Average Proportion'
                )
                fig.update_layout(
                    xaxis_title=None,
                    yaxis_title="Average Proportion",
                    xaxis={'visible': False},
                    yaxis_tickformat=".1%",
                    legend_title_text='Race/Ethnicity'
                )
                fig.update_traces(texttemplate='%{text:.1%}', textposition='inside')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Could not calculate average staff diversity for current filters.")
        else:
            st.info("No staff diversity data available for the selected universities.")
    else:
        st.info("Staff diversity data columns not available in the dataset.")

@st.cache_data(ttl=300)
def plot_gender_comparison(filtered_data):
    """
    Create a comparison of gender distribution for students and staff.
    """
    st.markdown("#### Gender Distribution Comparison", help="Comparison of gender distribution between students and staff.")

    # Student gender columns
    student_gender_cols = ['UGDS_MEN', 'UGDS_WOMEN']
    # Staff gender columns
    staff_gender_cols = ['IRPS_MEN', 'IRPS_WOMEN']

    # Check if we have student gender data
    has_student_gender = all(col in filtered_data.columns for col in student_gender_cols) and filtered_data[student_gender_cols].notna().any().any()

    # Check if we have staff gender data
    has_staff_gender = all(col in filtered_data.columns for col in staff_gender_cols) and filtered_data[staff_gender_cols].notna().any().any()

    if has_student_gender or has_staff_gender:
        # Create a figure with subplots
        fig = go.Figure()

        # Add student gender data if available
        if has_student_gender:
            student_data = filtered_data.dropna(subset=student_gender_cols, how='all')
            if not student_data.empty:
                avg_student_men = student_data['UGDS_MEN'].mean()
                avg_student_women = student_data['UGDS_WOMEN'].mean()

                # Define consistent colors for gender
                male_color = '#1f77b4'    # Blue for all males
                female_color = '#ff7f0e'  # Orange for all females

                # Add student gender bar
                fig.add_trace(go.Bar(
                    x=['Students'],
                    y=[avg_student_men],
                    name='Male',
                    marker_color=male_color,
                    text=f"{avg_student_men:.1%}",
                    textposition='inside'
                ))

                fig.add_trace(go.Bar(
                    x=['Students'],
                    y=[avg_student_women],
                    name='Female',
                    marker_color=female_color,
                    text=f"{avg_student_women:.1%}",
                    textposition='inside'
                ))

        # Add staff gender data if available
        if has_staff_gender:
            staff_data = filtered_data.dropna(subset=staff_gender_cols, how='all')
            if not staff_data.empty:
                avg_staff_men = staff_data['IRPS_MEN'].mean()
                avg_staff_women = staff_data['IRPS_WOMEN'].mean()

                # Add staff gender bar
                fig.add_trace(go.Bar(
                    x=['Staff'],
                    y=[avg_staff_men],
                    name='Male Staff',
                    marker_color=male_color,  # Same color as male students
                    text=f"{avg_staff_men:.1%}",
                    textposition='inside'
                ))

                fig.add_trace(go.Bar(
                    x=['Staff'],
                    y=[avg_staff_women],
                    name='Female Staff',
                    marker_color=female_color,  # Same color as female students
                    text=f"{avg_staff_women:.1%}",
                    textposition='inside'
                ))

        # Update layout
        fig.update_layout(
            title="Average Gender Distribution",
            barmode='stack',
            yaxis_tickformat=".0%",
            yaxis_title="Proportion",
            legend_title="Gender"
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Gender data not available for the selected universities.")

@st.cache_data(ttl=300)
def plot_gender_ratio_by_type(filtered_data):
    """
    Create a stacked bar chart of gender ratio by institution type.
    """
    st.markdown("#### Gender Ratio by Institution Type", help="Comparison of gender distribution across different types of institutions.")
    
    if 'UGDS_MEN' in filtered_data.columns and 'UGDS_WOMEN' in filtered_data.columns:
        plot_data = filtered_data.dropna(subset=['UGDS_MEN', 'UGDS_WOMEN', 'CONTROL_TYPE'])

        if not plot_data.empty:
            # Calculate average gender ratio by control type
            gender_ratio = plot_data.groupby('CONTROL_TYPE')[['UGDS_MEN', 'UGDS_WOMEN']].mean().reset_index()

            # Melt the data for plotting
            gender_ratio_melt = gender_ratio.melt(
                id_vars=['CONTROL_TYPE'],
                value_vars=['UGDS_MEN', 'UGDS_WOMEN'],
                var_name='Gender',
                value_name='Proportion'
            )

            # Map column names to readable labels
            gender_ratio_melt['Gender'] = gender_ratio_melt['Gender'].map({
                'UGDS_MEN': 'Male',
                'UGDS_WOMEN': 'Female'
            })

            fig = px.bar(
                gender_ratio_melt,
                x='CONTROL_TYPE',
                y='Proportion',
                color='Gender',
                title="Average Gender Ratio by Institution Type",
                labels={
                    'CONTROL_TYPE': 'Institution Type',
                    'Proportion': 'Proportion',
                    'Gender': 'Gender'
                },
                barmode='stack',
                text_auto='.1%'
            )
            
            fig.update_layout(
                yaxis_tickformat=".0%",
                xaxis_title="Institution Type",
                yaxis_title="Proportion"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.info("Insufficient data for Gender Ratio by Institution Type plot.")
    else:
        st.info("Gender data not available in the dataset.")

@st.cache_data(ttl=300)
def plot_staff_gender_ratio_by_type(filtered_data):
    """
    Create a stacked bar chart of staff gender ratio by institution type.
    """
    st.markdown("#### Staff Gender Ratio by Institution Type", help="Comparison of staff gender distribution across different types of institutions.")
    
    if 'IRPS_MEN' in filtered_data.columns and 'IRPS_WOMEN' in filtered_data.columns:
        plot_data = filtered_data.dropna(subset=['IRPS_MEN', 'IRPS_WOMEN', 'CONTROL_TYPE'])

        if not plot_data.empty:
            # Calculate average gender ratio by control type
            gender_ratio = plot_data.groupby('CONTROL_TYPE')[['IRPS_MEN', 'IRPS_WOMEN']].mean().reset_index()

            # Melt the data for plotting
            gender_ratio_melt = gender_ratio.melt(
                id_vars=['CONTROL_TYPE'],
                value_vars=['IRPS_MEN', 'IRPS_WOMEN'],
                var_name='Gender',
                value_name='Proportion'
            )

            # Map column names to readable labels
            gender_ratio_melt['Gender'] = gender_ratio_melt['Gender'].map({
                'IRPS_MEN': 'Male',
                'IRPS_WOMEN': 'Female'
            })

            fig = px.bar(
                gender_ratio_melt,
                x='CONTROL_TYPE',
                y='Proportion',
                color='Gender',
                title="Average Staff Gender Ratio by Institution Type",
                labels={
                    'CONTROL_TYPE': 'Institution Type',
                    'Proportion': 'Proportion',
                    'Gender': 'Gender'
                },
                barmode='stack',
                text_auto='.1%'
            )
            
            fig.update_layout(
                yaxis_tickformat=".0%",
                xaxis_title="Institution Type",
                yaxis_title="Proportion"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.info("Insufficient data for Staff Gender Ratio by Institution Type plot.")
    else:
        st.info("Staff gender data not available in the dataset.")

@st.cache_data(ttl=300)
def plot_diversity_pie(uni_data):
    """
    Create a pie chart showing diversity composition for a university.
    Cached for 5 minutes to improve performance.
    """
    diversity_cols = ['UGDS_WHITE', 'UGDS_BLACK', 'UGDS_HISP', 'UGDS_ASIAN',
                      'UGDS_AIAN', 'UGDS_NHPI', 'UGDS_2MOR', 'UGDS_NRA', 'UGDS_UNKN']

    # Check which diversity columns are available
    available_cols = [col for col in diversity_cols if col in uni_data.index]

    if available_cols and any(pd.notna(uni_data[col]) for col in available_cols):

        # Create mapping of available columns to labels and values
        race_labels = []
        proportions = []

        # Map of column names to display labels
        label_map = {
            'UGDS_WHITE': 'White',
            'UGDS_BLACK': 'Black',
            'UGDS_HISP': 'Hispanic',
            'UGDS_ASIAN': 'Asian',
            'UGDS_AIAN': 'American Indian/Alaska Native',
            'UGDS_NHPI': 'Native Hawaiian/Pacific Islander',
            'UGDS_2MOR': 'Two or More Races',
            'UGDS_NRA': 'Non-Resident Alien',
            'UGDS_UNKN': 'Unknown'
        }

        # Add available data
        for col in available_cols:
            if pd.notna(uni_data[col]) and uni_data[col] > 0:
                race_labels.append(label_map.get(col, col))
                proportions.append(uni_data[col])

        # Create dataframe for plotting
        diversity_data = pd.DataFrame({
            'Race/Ethnicity': race_labels,
            'Proportion': proportions
        })

        # Filter out zero values
        diversity_data = diversity_data[diversity_data['Proportion'] > 0]

        if not diversity_data.empty:
            # Create diversity chart with increased size
            fig = px.pie(
                diversity_data,
                values='Proportion',
                names='Race/Ethnicity',
                title="Student Body Composition"
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(
                height=600,  # Increased height
                margin=dict(t=50, b=50, l=20, r=20),  # Reduced margins
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.2,
                    xanchor="center",
                    x=0.5
                )
            )
            st.plotly_chart(fig, use_container_width=True)

@st.cache_data(ttl=300)
def plot_staff_diversity_pie(uni_data):
    """
    Create a pie chart showing staff diversity composition for a university.
    """
    staff_diversity_cols = ['IRPS_WHITE', 'IRPS_BLACK', 'IRPS_HISP', 'IRPS_ASIAN',
                           'IRPS_AIAN', 'IRPS_NHPI', 'IRPS_2MOR', 'IRPS_NRA', 'IRPS_UNKN']

    # Check which diversity columns are available
    available_cols = [col for col in staff_diversity_cols if col in uni_data.index]

    if available_cols and any(pd.notna(uni_data[col]) for col in available_cols):

        # Create mapping of available columns to labels and values
        race_labels = []
        proportions = []

        # Map of column names to display labels
        label_map = {
            'IRPS_WHITE': 'White',
            'IRPS_BLACK': 'Black',
            'IRPS_HISP': 'Hispanic',
            'IRPS_ASIAN': 'Asian',
            'IRPS_AIAN': 'American Indian/Alaska Native',
            'IRPS_NHPI': 'Native Hawaiian/Pacific Islander',
            'IRPS_2MOR': 'Two or More Races',
            'IRPS_NRA': 'Non-Resident Alien',
            'IRPS_UNKN': 'Unknown'
        }

        # Add available data
        for col in available_cols:
            if pd.notna(uni_data[col]) and uni_data[col] > 0:
                race_labels.append(label_map.get(col, col))
                proportions.append(uni_data[col])

        # Create dataframe for plotting
        diversity_data = pd.DataFrame({
            'Race/Ethnicity': race_labels,
            'Proportion': proportions
        })

        # Filter out zero values
        diversity_data = diversity_data[diversity_data['Proportion'] > 0]

        if not diversity_data.empty:
            # Create diversity chart with increased size
            fig = px.pie(
                diversity_data,
                values='Proportion',
                names='Race/Ethnicity',
                title="Staff Composition"
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(
                height=600,  # Increased height
                margin=dict(t=50, b=50, l=20, r=20),  # Reduced margins
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.2,
                    xanchor="center",
                    x=0.5
                )
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No staff diversity data available for this university.")
    else:
        st.info("Staff diversity data not available for this university.")

@st.cache_data(ttl=300)
def plot_gender_pie(uni_data):
    """
    Create pie charts showing gender distribution for students and staff.
    """
    # Student gender columns
    student_gender_cols = ['UGDS_MEN', 'UGDS_WOMEN']
    # Staff gender columns
    staff_gender_cols = ['IRPS_MEN', 'IRPS_WOMEN']

    # Check if we have student gender data
    has_student_gender = all(col in uni_data.index for col in student_gender_cols) and any(pd.notna(uni_data[col]) for col in student_gender_cols)

    # Check if we have staff gender data
    has_staff_gender = all(col in uni_data.index for col in staff_gender_cols) and any(pd.notna(uni_data[col]) for col in staff_gender_cols)

    if has_student_gender or has_staff_gender:

        # Create columns for the charts
        if has_student_gender and has_staff_gender:
            col1, col2 = st.columns(2)
        else:
            col1 = st

        # Student gender pie chart
        if has_student_gender:
            with col1:
                # Create student gender data
                student_gender_data = pd.DataFrame({
                    'Gender': ['Male', 'Female'],
                    'Proportion': [uni_data['UGDS_MEN'], uni_data['UGDS_WOMEN']]
                })

                # Filter out null values
                student_gender_data = student_gender_data.dropna()

                if not student_gender_data.empty:
                    # Define consistent colors for gender
                    male_color = '#1f77b4'    # Blue for all males
                    female_color = '#ff7f0e'  # Orange for all females

                    # Create pie chart
                    fig = px.pie(
                        student_gender_data,
                        values='Proportion',
                        names='Gender',
                        title="Student Gender Distribution",
                        color_discrete_map={'Male': male_color, 'Female': female_color}
                    )
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(
                        height=500,  # Increased height
                        margin=dict(t=50, b=50, l=20, r=20)  # Reduced margins
                    )
                    st.plotly_chart(fig, use_container_width=True)

        # Staff gender pie chart
        if has_staff_gender:
            with col2 if has_student_gender else col1:
                # Create staff gender data
                staff_gender_data = pd.DataFrame({
                    'Gender': ['Male', 'Female'],
                    'Proportion': [uni_data['IRPS_MEN'], uni_data['IRPS_WOMEN']]
                })

                # Filter out null values
                staff_gender_data = staff_gender_data.dropna()

                if not staff_gender_data.empty:
                    # Create pie chart using the same colors as student gender
                    fig = px.pie(
                        staff_gender_data,
                        values='Proportion',
                        names='Gender',
                        title="Staff Gender Distribution",
                        color_discrete_map={'Male': male_color, 'Female': female_color}
                    )
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(
                        height=500,  # Increased height
                        margin=dict(t=50, b=50, l=20, r=20)  # Reduced margins
                    )
                    st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Gender distribution data not available for this university.")

