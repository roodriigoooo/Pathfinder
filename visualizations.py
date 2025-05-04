"""
Visualization functions for the University Scout application.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from Pathfinder.utils import get_figure_download_link
from Pathfinder.config import DIVERSITY_MAPPING

@st.cache_data(ttl=300)
def plot_selectivity_scatter(filtered_data):
    """
    Create a scatter plot of admission rate vs. SAT score.
    Cached for 5 minutes to improve performance.

    Args:
        filtered_data: DataFrame containing university data

    Returns:
        None: Displays the plot directly using streamlit
    """
    st.markdown("#### Admission Rate vs. Average SAT Score")
    plot_data = filtered_data.dropna(subset=['ADM_RATE', 'SAT_AVG'])

    if not plot_data.empty:
        fig = px.scatter(
            plot_data,
            x='ADM_RATE',
            y='SAT_AVG',
            color='CONTROL_TYPE',
            hover_name='INSTNM',
            title="Selectivity Landscape",
            labels={'ADM_RATE': 'Admission Rate', 'SAT_AVG': 'Average SAT Score', 'CONTROL_TYPE': 'Type'}
        )
        fig.update_layout(
            xaxis_title="Admission Rate (Lower is More Selective)",
            yaxis_title="Average SAT Score",
            xaxis_tickformat=".0%"
        )
        st.plotly_chart(fig, use_container_width=True)

        # Add download option
        st.markdown(
            get_figure_download_link(
                fig,
                f"selectivity_scatter.png",
                "📥 Download Chart"
            ),
            unsafe_allow_html=True
        )
    else:
        st.info("Insufficient data for Admission Rate vs. SAT Score plot with current filters.")

def plot_control_type_distribution(filtered_data):
    """
    Create a bar chart showing the distribution of university control types.

    Args:
        filtered_data: DataFrame containing university data

    Returns:
        None: Displays the plot directly using streamlit
    """
    st.markdown("#### University Count by Control Type")
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
            color='CONTROL_TYPE'
        )
        fig.update_layout(
            xaxis_title="Control Type",
            yaxis_title="Number of Universities"
        )
        st.plotly_chart(fig, use_container_width=True)

        # Add download option
        st.markdown(
            get_figure_download_link(
                fig,
                f"control_type_distribution.png",
                "📥 Download Chart"
            ),
            unsafe_allow_html=True
        )
    else:
        st.info("Insufficient data for Control Type distribution plot.")

def plot_debt_earnings_scatter(filtered_data):
    """
    Create a scatter plot of median debt vs. median earnings.

    Args:
        filtered_data: DataFrame containing university data

    Returns:
        None: Displays the plot directly using streamlit
    """
    st.markdown("#### Median Debt vs. Median Earnings (10yr)")
    plot_data = filtered_data.dropna(subset=['GRAD_DEBT_MDN', 'MD_EARN_WNE_P10'])

    if not plot_data.empty:
        fig = px.scatter(
            plot_data,
            x='GRAD_DEBT_MDN',
            y='MD_EARN_WNE_P10',
            color='CONTROL_TYPE',
            hover_name='INSTNM',
            title="Potential Return on Investment",
            labels={
                'GRAD_DEBT_MDN': 'Median Debt of Graduates',
                'MD_EARN_WNE_P10': 'Median Earnings (10 years after entry)',
                'CONTROL_TYPE': 'Type'
            }
        )
        fig.update_layout(
            xaxis_title="Median Graduate Debt ($)",
            yaxis_title="Median Earnings ($)",
            xaxis_tickformat="$,.0f",
            yaxis_tickformat="$,.0f"
        )
        st.plotly_chart(fig, use_container_width=True)

        # Add download option
        st.markdown(
            get_figure_download_link(
                fig,
                f"debt_earnings_scatter.png",
                "📥 Download Chart"
            ),
            unsafe_allow_html=True
        )
    else:
        st.info("Insufficient data for Debt vs. Earnings plot with current filters.")

@st.cache_data(ttl=300)
def plot_tuition_distribution(filtered_data):
    """
    Create a box plot of tuition distribution by control type.
    Cached for 5 minutes to improve performance.

    Args:
        filtered_data: DataFrame containing university data

    Returns:
        None: Displays the plot directly using streamlit
    """
    st.markdown("#### Tuition Fee Distribution by Control Type")
    plot_data = filtered_data.dropna(subset=['TUITIONFEE_IN', 'TUITIONFEE_OUT', 'CONTROL_TYPE'])

    if not plot_data.empty:
        plot_data_melt = plot_data.melt(
            id_vars=['INSTNM', 'CONTROL_TYPE'],
            value_vars=['TUITIONFEE_IN', 'TUITIONFEE_OUT'],
            var_name='Tuition Type',
            value_name='Tuition Fee'
        )
        plot_data_melt['Tuition Type'] = plot_data_melt['Tuition Type'].map({
            'TUITIONFEE_IN': 'In-State',
            'TUITIONFEE_OUT': 'Out-of-State'
        })

        fig = px.box(
            plot_data_melt.dropna(subset=['Tuition Fee']),
            x='CONTROL_TYPE',
            y='Tuition Fee',
            color='Tuition Type',
            hover_name='INSTNM',
            title="Distribution of Annual Tuition Fees",
            labels={
                'CONTROL_TYPE': 'Control Type',
                'Tuition Fee': 'Annual Tuition Fee ($)',
                'Tuition Type': 'Tuition Type'
            },
            points=False
        )
        fig.update_layout(
            xaxis_title="Control Type",
            yaxis_title="Annual Tuition Fee ($)",
            yaxis_tickformat="$,.0f"
        )
        st.plotly_chart(fig, use_container_width=True)

        # Add download option
        st.markdown(
            get_figure_download_link(
                fig,
                f"tuition_distribution.png",
                "📥 Download Chart"
            ),
            unsafe_allow_html=True
        )
    else:
        st.info("Insufficient data for Tuition Fee distribution plot.")

def plot_graduation_rate_histogram(filtered_data):
    """
    Create a histogram of 4-year graduation rates.

    Args:
        filtered_data: DataFrame containing university data

    Returns:
        None: Displays the plot directly using streamlit
    """
    st.markdown("#### 4-Year Graduation Rate Distribution")
    plot_data = filtered_data.dropna(subset=['C150_4'])

    if not plot_data.empty:
        fig = px.histogram(
            plot_data,
            x='C150_4',
            nbins=30,
            title="Distribution of 4-Year Graduation Rates (Bachelor's)",
            labels={'C150_4': '4-Year Graduation Rate'}
        )
        fig.update_layout(
            xaxis_title="4-Year Graduation Rate",
            yaxis_title="Number of Universities",
            xaxis_tickformat=".0%"
        )
        st.plotly_chart(fig, use_container_width=True)

        # Add download option
        st.markdown(
            get_figure_download_link(
                fig,
                f"graduation_rate_histogram.png",
                "📥 Download Chart"
            ),
            unsafe_allow_html=True
        )
    else:
        st.info("Insufficient data for 4-Year Graduation Rate histogram.")

def plot_diversity_composition(filtered_data):
    """
    Create a bar chart showing average undergraduate diversity composition.

    Args:
        filtered_data: DataFrame containing university data

    Returns:
        None: Displays the plot directly using streamlit
    """
    st.markdown("#### Average Undergraduate Diversity")
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

            # Add download option
            st.markdown(
                get_figure_download_link(
                    fig,
                    f"diversity_composition.png",
                    "📥 Download Chart"
                ),
                unsafe_allow_html=True
            )
        else:
            st.info("Could not calculate average diversity for current filters.")
    else:
        st.info("Diversity data columns not available in the dataset.")

@st.cache_data(ttl=300)
def plot_admission_trend(uni_data, hist_data, unitid):
    """
    Create a line chart showing historical admission rate trend for a university.
    Cached for 5 minutes to improve performance.

    Args:
        uni_data: Series containing university data
        hist_data: DataFrame containing historical data
        unitid: University ID

    Returns:
        None: Displays the plot directly using streamlit
    """
    if not hist_data.empty:
        uni_hist = hist_data[hist_data['UNITID'] == unitid]
        if not uni_hist.empty and 'ADM_RATE' in uni_hist.columns and uni_hist['ADM_RATE'].notna().any():
            st.subheader("Admission Rate Trend")

            # Prepare data for trend chart
            trend_data = uni_hist[['YEAR', 'ADM_RATE']].dropna()
            if not trend_data.empty:
                trend_data = trend_data.sort_values('YEAR')

                # Create trend chart
                fig = px.line(
                    trend_data,
                    x='YEAR',
                    y='ADM_RATE',
                    title="Historical Admission Rate",
                    labels={'YEAR': 'Year', 'ADM_RATE': 'Admission Rate'}
                )
                fig.update_layout(yaxis_tickformat=".1%")
                st.plotly_chart(fig, use_container_width=True)

                # Add download option for the chart
                st.markdown(
                    get_figure_download_link(
                        fig,
                        f"{uni_data['INSTNM'].replace(' ', '_')}_admission_trend.png",
                        "📥 Download Chart"
                    ),
                    unsafe_allow_html=True
                )

@st.cache_data(ttl=300)
def plot_tuition_trend(uni_data, hist_data, unitid):
    """
    Create a line chart showing historical tuition trend for a university.
    Cached for 5 minutes to improve performance.

    Args:
        uni_data: Series containing university data
        hist_data: DataFrame containing historical data
        unitid: University ID

    Returns:
        None: Displays the plot directly using streamlit
    """
    if not hist_data.empty:
        uni_hist = hist_data[hist_data['UNITID'] == unitid]
        if not uni_hist.empty and 'TUITIONFEE_IN' in uni_hist.columns and uni_hist['TUITIONFEE_IN'].notna().any():
            st.subheader("Tuition Trend")

            # Prepare data for trend chart
            trend_data = uni_hist[['YEAR', 'TUITIONFEE_IN', 'TUITIONFEE_OUT']].dropna()
            if not trend_data.empty:
                trend_data = trend_data.sort_values('YEAR')

                # Melt the data for plotting
                trend_data_melt = trend_data.melt(
                    id_vars=['YEAR'],
                    value_vars=['TUITIONFEE_IN', 'TUITIONFEE_OUT'],
                    var_name='Tuition Type',
                    value_name='Amount'
                )

                # Map column names to readable labels
                trend_data_melt['Tuition Type'] = trend_data_melt['Tuition Type'].map({
                    'TUITIONFEE_IN': 'In-State',
                    'TUITIONFEE_OUT': 'Out-of-State'
                })

                # Create trend chart
                fig = px.line(
                    trend_data_melt,
                    x='YEAR',
                    y='Amount',
                    color='Tuition Type',
                    title="Historical Tuition",
                    labels={'YEAR': 'Year', 'Amount': 'Tuition ($)'}
                )
                fig.update_layout(yaxis_tickformat="$,.0f")
                st.plotly_chart(fig, use_container_width=True)

                # Add download option for the chart
                st.markdown(
                    get_figure_download_link(
                        fig,
                        f"{uni_data['INSTNM'].replace(' ', '_')}_tuition_trend.png",
                        "📥 Download Chart"
                    ),
                    unsafe_allow_html=True
                )

@st.cache_data(ttl=300)
def plot_diversity_pie(uni_data):
    """
    Create a pie chart showing diversity composition for a university.
    Cached for 5 minutes to improve performance.

    Args:
        uni_data: Series containing university data

    Returns:
        None: Displays the plot directly using streamlit
    """
    diversity_cols = ['UGDS_WHITE', 'UGDS_BLACK', 'UGDS_HISP', 'UGDS_ASIAN',
                      'UGDS_AIAN', 'UGDS_NHPI', 'UGDS_2MOR', 'UGDS_NRA', 'UGDS_UNKN']

    # Check which diversity columns are available
    available_cols = [col for col in diversity_cols if col in uni_data.index]

    if available_cols and any(pd.notna(uni_data[col]) for col in available_cols):
        st.subheader("Student Body Diversity")

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
            # Create diversity chart
            fig = px.pie(
                diversity_data,
                values='Proportion',
                names='Race/Ethnicity',
                title="Student Body Composition"
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)

            # Add download option for the chart
            st.markdown(
                get_figure_download_link(
                    fig,
                    f"{uni_data['INSTNM'].replace(' ', '_')}_diversity.png",
                    "📥 Download Chart"
                ),
                unsafe_allow_html=True
            )

def plot_graduation_trend(uni_data, hist_data, unitid):
    """
    Create a line chart showing historical graduation rate trend for a university.

    Args:
        uni_data: Series containing university data
        hist_data: DataFrame containing historical data
        unitid: University ID

    Returns:
        None: Displays the plot directly using streamlit
    """
    if not hist_data.empty:
        uni_hist = hist_data[hist_data['UNITID'] == unitid]
        if not uni_hist.empty and 'C150_4' in uni_hist.columns and uni_hist['C150_4'].notna().any():
            st.subheader("Graduation Rate Trend")

            # Prepare data for trend chart
            trend_data = uni_hist[['YEAR', 'C150_4']].dropna()
            if not trend_data.empty:
                trend_data = trend_data.sort_values('YEAR')

                # Create trend chart
                fig = px.line(
                    trend_data,
                    x='YEAR',
                    y='C150_4',
                    title="Historical 4-Year Graduation Rate",
                    labels={'YEAR': 'Year', 'C150_4': 'Graduation Rate'}
                )
                fig.update_layout(yaxis_tickformat=".1%")
                st.plotly_chart(fig, use_container_width=True)

                # Add download option for the chart
                st.markdown(
                    get_figure_download_link(
                        fig,
                        f"{uni_data['INSTNM'].replace(' ', '_')}_graduation_trend.png",
                        "📥 Download Chart"
                    ),
                    unsafe_allow_html=True
                )

def plot_ranking_trend(uni_data, rank_data):
    """
    Create a line chart showing ranking trends for a university.

    Args:
        uni_data: Series containing university data
        rank_data: DataFrame containing ranking data

    Returns:
        None: Displays the plot directly using streamlit
    """
    if not rank_data.empty:
        # Try to find matches in ranking data
        uni_name = uni_data['INSTNM']
        rank_matches = rank_data[rank_data['institution_name'].str.contains(uni_name, case=False, na=False)]

        if not rank_matches.empty and len(rank_matches['year'].unique()) > 1:
            st.subheader("Ranking Trends")

            # Create ranking trend chart
            fig = px.line(
                rank_matches.sort_values(['source', 'year']),
                x='year',
                y='world_rank',
                color='source',
                title="World Ranking Trend",
                labels={'year': 'Year', 'world_rank': 'World Rank', 'source': 'Ranking Source'}
            )
            # Invert y-axis so lower (better) ranks are at the top
            fig.update_layout(yaxis_autorange="reversed")
            st.plotly_chart(fig, use_container_width=True)

            # Add download option for the chart
            st.markdown(
                get_figure_download_link(
                    fig,
                    f"{uni_data['INSTNM'].replace(' ', '_')}_ranking_trend.png",
                    "📥 Download Chart"
                ),
                unsafe_allow_html=True
            )

def plot_program_earnings(uni_data, fos_data, unitid, level):
    """
    Create a bar chart showing earnings by program for a university.

    Args:
        uni_data: Series containing university data
        fos_data: DataFrame containing field of study data
        unitid: University ID
        level: Credential level

    Returns:
        None: Displays the plot directly using streamlit
    """
    if not fos_data.empty:
        # Filter field of study data for this university and credential level
        uni_fos = fos_data[(fos_data['UNITID'] == unitid) & (fos_data['CREDLEV'] == level)]

        # If we have earnings data, show visualization
        if not uni_fos.empty and 'EARN_MDN_HI_1YR' in uni_fos.columns and uni_fos['EARN_MDN_HI_1YR'].notna().any():
            # Get top programs by earnings
            top_programs = uni_fos.dropna(subset=['EARN_MDN_HI_1YR']).sort_values('EARN_MDN_HI_1YR', ascending=False).head(10)

            if not top_programs.empty:
                level_name = uni_fos['CREDDESC'].iloc[0]
                st.subheader(f"Top {level_name} Programs by Earnings")

                # Create earnings chart
                fig = px.bar(
                    top_programs,
                    x='EARN_MDN_HI_1YR',
                    y='CIPDESC',
                    orientation='h',
                    title=f"Median Earnings by Program ({level_name})",
                    labels={'EARN_MDN_HI_1YR': 'Median Earnings ($)', 'CIPDESC': 'Program'}
                )
                fig.update_layout(
                    yaxis={'categoryorder': 'total ascending'},
                    xaxis_tickformat="$,.0f"
                )
                st.plotly_chart(fig, use_container_width=True)

                # Add download option for the chart
                st.markdown(
                    get_figure_download_link(
                        fig,
                        f"{uni_data['INSTNM'].replace(' ', '_')}_{level}_earnings.png",
                        "📥 Download Chart"
                    ),
                    unsafe_allow_html=True
                )
