"""
Academic visualizations for the Pathfinder application.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

@st.cache_data(ttl=300)
def plot_selectivity_scatter(filtered_data):
    """
    Create a scatter plot of admission rate vs. SAT score.
    """
    st.markdown("#### Admission Rate vs. Average SAT Score",
              help="Lower admission rates and higher SAT scores generally indicate more selective institutions. Only institutions that report both admission rates and SAT scores are shown.")

    # Make a copy to avoid modifying the original dataframe
    plot_data = filtered_data.copy()

    # Count total institutions vs those with data
    total_institutions = len(filtered_data)
    institutions_with_data = len(filtered_data.dropna(subset=['ADM_RATE', 'SAT_AVG']))
    missing_data_pct = (total_institutions - institutions_with_data) / total_institutions * 100 if total_institutions > 0 else 0

    # Add transparency note if significant data is missing
    if missing_data_pct > 10:
        st.caption(f"Note: {missing_data_pct:.0f}% of institutions in your filter are not shown due to missing admission rate or SAT score data.")

    # Only drop rows where both ADM_RATE and SAT_AVG are missing
    plot_data = plot_data.dropna(subset=['ADM_RATE', 'SAT_AVG'])

    # Convert admission rate to percentage for display
    if 'ADM_RATE' in plot_data.columns:
        plot_data['ADM_RATE_DISPLAY'] = plot_data['ADM_RATE'] * 100

    if not plot_data.empty:
        # Create scatter plot with improved handling of data points
        fig = px.scatter(
            plot_data,
            x='ADM_RATE',
            y='SAT_AVG',
            color='CONTROL_TYPE',
            hover_name='INSTNM',
            hover_data={
                'ADM_RATE': ':.1%',  # Format as percentage in hover
                'SAT_AVG': True,
                'CONTROL_TYPE': True,
                'ADM_RATE_DISPLAY': False  # Hide this from hover
            },
            title="Selectivity Landscape",
            labels={'ADM_RATE': 'Admission Rate', 'SAT_AVG': 'Average SAT Score', 'CONTROL_TYPE': 'Type'}
        )

        # Improve layout with better formatting
        fig.update_layout(
            xaxis_title="Admission Rate (Lower is More Selective)",
            yaxis_title="Average SAT Score",
            xaxis_tickformat=".0%",
            height=600,  # Increase height for better visibility
            hovermode="closest"
        )

        # Add more data points to the plot
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("Insufficient data for Admission Rate vs. SAT Score plot with current filters.")

@st.cache_data(ttl=300)
def plot_sat_distribution(filtered_data):
    """
    Create a box plot of SAT score distribution by institution type.
    """
    st.markdown("#### SAT Score by Institution Type",
              help="Distribution of average SAT scores across different types of institutions. Only institutions that report SAT scores are shown.")

    # Count total institutions vs those with data
    total_institutions = len(filtered_data)
    institutions_with_data = len(filtered_data.dropna(subset=['SAT_AVG', 'CONTROL_TYPE']))
    missing_data_pct = (total_institutions - institutions_with_data) / total_institutions * 100 if total_institutions > 0 else 0

    # Add transparency note if significant data is missing
    if missing_data_pct > 10:
        st.caption(f"Note: {missing_data_pct:.0f}% of institutions in your filter are not shown due to missing SAT score data.")

    plot_data = filtered_data.dropna(subset=['SAT_AVG', 'CONTROL_TYPE'])

    if not plot_data.empty:
        fig = px.box(
            plot_data,
            x='CONTROL_TYPE',
            y='SAT_AVG',
            title="SAT Score Distribution by Institution Type",
            labels={'CONTROL_TYPE': 'Institution Type', 'SAT_AVG': 'Average SAT Score'},
            color='CONTROL_TYPE'
        )

        # Add individual points for better visibility
        fig.update_traces(boxpoints='all', jitter=0.3, pointpos=-1.8)

        fig.update_layout(
            xaxis_title="Institution Type",
            yaxis_title="Average SAT Score",
            yaxis_range=[700, 1600],
            height=550
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("Insufficient data for SAT Score distribution plot.")

@st.cache_data(ttl=300)
def plot_test_policy_distribution(filtered_data):
    """
    Create a pie chart showing the distribution of test score policies.
    """
    st.markdown("#### Test Score Policy Distribution",
              help="Breakdown of standardized test score policies across institutions. Only institutions that report their test score policy are shown.")

    # Count total institutions vs those with data
    total_institutions = len(filtered_data)
    institutions_with_data = len(filtered_data.dropna(subset=['ADMCON7']))
    missing_data_pct = (total_institutions - institutions_with_data) / total_institutions * 100 if total_institutions > 0 else 0

    # Add transparency note if significant data is missing
    if missing_data_pct > 10:
        st.caption(f"Note: {missing_data_pct:.0f}% of institutions in your filter are not shown due to missing test score policy data.")

    plot_data = filtered_data.dropna(subset=['ADMCON7'])

    if not plot_data.empty:
        # Map ADMCON7 values to readable labels
        policy_map = {
            1: "Required",
            2: "Recommended",
            3: "Neither Required nor Recommended",
            4: "Do not know",
            5: "Considered but not Required"
        }

        # Convert ADMCON7 to integer and map to labels
        plot_data['Test Score Policy'] = plot_data['ADMCON7'].astype(int).map(policy_map)

        # Count universities by policy
        policy_counts = plot_data['Test Score Policy'].value_counts().reset_index()
        policy_counts.columns = ['Test Score Policy', 'Count']

        # Create the pie chart
        fig = px.pie(
            policy_counts,
            values='Count',
            names='Test Score Policy',
            title="Test Score Policy Distribution",
            color='Test Score Policy',
        )

        # Improve layout
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(
            legend_title="Test Score Policy",
            margin=dict(t=30, b=0, l=0, r=0)
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("Insufficient data for Test Score Policy distribution plot.")

@st.cache_data(ttl=300)
def plot_admission_trend(uni_data, hist_data, unitid):
    """
    Create a line chart showing historical admission rate trend for a university.
    """
    if not hist_data.empty:
        uni_hist = hist_data[hist_data['UNITID'] == unitid]
        if not uni_hist.empty and 'ADM_RATE' in uni_hist.columns and uni_hist['ADM_RATE'].notna().any():
            st.subheader("Admission Rate Trend")

            # Prepare data for trend chart
            trend_data = uni_hist[['YEAR', 'ADM_RATE']].dropna()
            if not trend_data.empty:
                trend_data = trend_data.sort_values('YEAR')

                # Create trend chart with enhanced styling
                fig = px.line(
                    trend_data,
                    x='YEAR',
                    y='ADM_RATE',
                    title="Historical Admission Rate (2015-2023)",
                    labels={'YEAR': 'Year', 'ADM_RATE': 'Admission Rate'},
                    markers=True,
                    line_shape='spline'
                )

                # Add a trend line (rolling average)
                if len(trend_data) > 2:
                    trend_data['Rolling_Avg'] = trend_data['ADM_RATE'].rolling(window=min(3, len(trend_data)), min_periods=1).mean()
                    fig.add_scatter(
                        x=trend_data['YEAR'],
                        y=trend_data['Rolling_Avg'],
                        mode='lines',
                        name='3-Year Average',
                        line=dict(color='rgba(0,0,255,0.5)', width=3, dash='dot')
                    )

                # Improve layout
                fig.update_layout(
                    yaxis_tickformat=".1%",
                    xaxis_title="Academic Year",
                    yaxis_title="Admission Rate",
                    legend_title="Metric",
                    hovermode="x unified",
                    xaxis=dict(
                        tickmode='array',
                        tickvals=trend_data['YEAR'].unique(),
                        ticktext=[f"'{str(year)[2:4]}-{str(year+1)[2:4]}" for year in trend_data['YEAR'].unique()]
                    )
                )

                st.plotly_chart(fig, use_container_width=True)

@st.cache_data(ttl=300)
def plot_test_scores_trend(uni_data, hist_data, unitid):
    """
    Create a line chart showing historical SAT/ACT score trends for a university.
    """
    if not hist_data.empty:
        uni_hist = hist_data[hist_data['UNITID'] == unitid]

        # Check if we have SAT or ACT data
        has_sat = 'SAT_AVG' in uni_hist.columns and uni_hist['SAT_AVG'].notna().any()
        has_act = 'ACTCMMID' in uni_hist.columns and uni_hist['ACTCMMID'].notna().any()

        if has_sat or has_act:
            st.subheader("Test Score Trends")

            # Create figure with secondary y-axis
            fig = go.Figure()

            # Add SAT data if available
            if has_sat:
                sat_data = uni_hist[['YEAR', 'SAT_AVG']].dropna().sort_values('YEAR')
                if not sat_data.empty:
                    # Add SAT line
                    fig.add_trace(
                        go.Scatter(
                            x=sat_data['YEAR'],
                            y=sat_data['SAT_AVG'],
                            name='SAT Average',
                            mode='lines+markers',
                            line=dict(color='blue', width=2),
                            marker=dict(size=8)
                        )
                    )

                    # Add rolling average if we have enough data points
                    if len(sat_data) > 2:
                        sat_data['Rolling_Avg'] = sat_data['SAT_AVG'].rolling(window=min(3, len(sat_data)), min_periods=1).mean()
                        fig.add_trace(
                            go.Scatter(
                                x=sat_data['YEAR'],
                                y=sat_data['Rolling_Avg'],
                                name='SAT 3-Year Avg',
                                mode='lines',
                                line=dict(color='rgba(0,0,255,0.5)', width=3, dash='dot')
                            )
                        )

            # Add ACT data if available
            if has_act:
                act_data = uni_hist[['YEAR', 'ACTCMMID']].dropna().sort_values('YEAR')
                if not act_data.empty:
                    # Add ACT line on secondary y-axis
                    fig.add_trace(
                        go.Scatter(
                            x=act_data['YEAR'],
                            y=act_data['ACTCMMID'],
                            name='ACT Median',
                            mode='lines+markers',
                            line=dict(color='green', width=2),
                            marker=dict(size=8),
                            yaxis='y2'
                        )
                    )

                    # Add rolling average if we have enough data points
                    if len(act_data) > 2:
                        act_data['Rolling_Avg'] = act_data['ACTCMMID'].rolling(window=min(3, len(act_data)), min_periods=1).mean()
                        fig.add_trace(
                            go.Scatter(
                                x=act_data['YEAR'],
                                y=act_data['Rolling_Avg'],
                                name='ACT 3-Year Avg',
                                mode='lines',
                                line=dict(color='rgba(0,128,0,0.5)', width=3, dash='dot'),
                                yaxis='y2'
                            )
                        )

            # Update layout with dual y-axes
            years = uni_hist['YEAR'].dropna().unique()
            fig.update_layout(
                title="Historical Test Score Trends (2015-2023)",
                xaxis=dict(
                    title="Academic Year",
                    tickmode='array',
                    tickvals=years,
                    ticktext=[f"'{str(year)[2:4]}-{str(year+1)[2:4]}" for year in years]
                ),
                yaxis=dict(
                    title="SAT Score",
                    range=[min(800, uni_hist['SAT_AVG'].min() * 0.9 if has_sat else 800),
                           max(1600, uni_hist['SAT_AVG'].max() * 1.1 if has_sat else 1600)]
                ),
                yaxis2=dict(
                    title="ACT Score",
                    overlaying='y',
                    side='right',
                    range=[min(12, uni_hist['ACTCMMID'].min() * 0.9 if has_act else 12),
                           max(36, uni_hist['ACTCMMID'].max() * 1.1 if has_act else 36)]
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="center",
                    x=0.5
                ),
                hovermode="x unified"
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Historical test score data not available for this university.")

@st.cache_data(ttl=300)
def plot_enrollment_trend(selected_df, historical_data):
    """
    Create a line chart showing historical undergraduate enrollment trends for selected universities.
    """
    st.markdown("### Enrollment Trends",
              help="This chart shows the trend in undergraduate enrollment over time. The dotted lines represent 3-year rolling averages to smooth out year-to-year fluctuations. Only institutions that report enrollment data are shown.")

    # Add note about data availability
    st.caption("Note: Historical enrollment data may not be available for all institutions. Missing years in the trend may indicate unreported data.")

    if 'UNITID' not in selected_df.columns or selected_df.empty or historical_data.empty:
        st.info("Insufficient data for enrollment trend visualization.")
        return

    # Create a line chart for enrollment trends
    fig = go.Figure()

    # Track if we have any data to display
    has_data = False

    # Add data for each university
    for _, uni in selected_df.iterrows():
        uni_id = uni['UNITID']
        uni_name = uni['INSTNM']

        # Get historical data for this university
        uni_history = historical_data[historical_data['UNITID'] == uni_id].copy()

        if not uni_history.empty and 'UGDS' in uni_history.columns:
            # Get the data sorted by year
            enrollment_trend = uni_history[['YEAR', 'UGDS']].dropna().sort_values('YEAR')

            if not enrollment_trend.empty and len(enrollment_trend) > 1:
                has_data = True

                # Add a line for this university
                fig.add_trace(go.Scatter(
                    x=enrollment_trend['YEAR'],
                    y=enrollment_trend['UGDS'],
                    mode='lines+markers',
                    name=uni_name,
                    line=dict(width=2),
                    hovertemplate='%{y:,.0f} students'
                ))

                # Add rolling average if we have enough data points
                if len(enrollment_trend) > 2:
                    enrollment_trend['Rolling_Avg'] = enrollment_trend['UGDS'].rolling(window=min(3, len(enrollment_trend)), min_periods=1).mean()
                    fig.add_trace(go.Scatter(
                        x=enrollment_trend['YEAR'],
                        y=enrollment_trend['Rolling_Avg'],
                        mode='lines',
                        name=f"{uni_name} (3-Year Avg)",
                        line=dict(dash='dot', width=1.5),
                        showlegend=False,
                        hovertemplate='%{y:,.0f} students (3-year avg)'
                    ))

    if has_data:
        # Improve layout
        fig.update_layout(
            title="Historical Undergraduate Enrollment (2015-2023)",
            xaxis_title="Academic Year",
            yaxis_title="Undergraduate Enrollment",
            yaxis_tickformat=",",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            hovermode="x unified",
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Historical enrollment data not available for the selected universities.")

@st.cache_data(ttl=300)
def plot_admission_rate_card(uni_data, key_prefix=""):
    """
    Display an admission rate card with visual indicator.
    """
    # Add help text about admission rate
    if pd.notna(uni_data.get('ADM_RATE')):
        adm_rate = uni_data['ADM_RATE']
        # Determine selectivity level with neutral colors
        if adm_rate < 0.1:
            selectivity = "Highly Selective"
            color = "#5B6ABF"  # Muted blue-purple
        elif adm_rate < 0.25:
            selectivity = "Very Selective"
            color = "#6B8E9F"  # Muted blue-gray
        elif adm_rate < 0.5:
            selectivity = "Selective"
            color = "#7C9A83"  # Muted green-gray
        elif adm_rate < 0.75:
            selectivity = "Moderately Selective"
            color = "#8E9C6B"  # Muted olive
        else:
            selectivity = "Inclusive"
            color = "#9F8E6B"  # Muted tan

        st.markdown(f"""
        <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; background-color: white;">
            <h4 style="margin-top: 0; color: #333;">Admission Rate</h4>
            <p style="font-size: 24px; font-weight: bold; margin: 10px 0; color: #333;">{adm_rate:.1%}</p>
            <p style="color: {color}; font-weight: bold; margin-bottom: 5px;">{selectivity}</p>
            <div style='text-align: right;'></div>
            <div style="background-color: #e9ecef; border-radius: 4px; height: 8px;">
                <div style="background-color: {color}; width: {min(adm_rate * 100, 100)}%; height: 100%; border-radius: 4px;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True)
        
    else:
        st.markdown("""
        <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; background-color: white;">
            <h4 style="margin-top: 0; color: #333;">Admission Rate</h4>
            <p style="font-size: 24px; font-weight: bold; margin: 10px 0; color: #333;">N/A</p>
        </div>
        """, unsafe_allow_html=True)

@st.cache_data(ttl=300)
def plot_test_policy_card(uni_data, key_prefix=""):
    """
    Display a test score policy card.
    """
    # Add help text about test score policy
    if 'ADMCON7' in uni_data and pd.notna(uni_data['ADMCON7']):
        admcon_value = int(uni_data['ADMCON7'])

        # Map ADMCON7 values to descriptions
        admcon_map = {
            1: {"label": "Required", "color": "#5B6ABF", "icon": "🔒"},
            2: {"label": "Recommended", "color": "#6B8E9F", "icon": "👍"},
            3: {"label": "Neither Required nor Recommended", "color": "#8E9C6B", "icon": "🤔"},
            4: {"label": "Do not know", "color": "#9F8E6B", "icon": "❓"},
            5: {"label": "Considered but not Required", "color": "#7C9A83", "icon": "✓"}
        }

        policy = admcon_map.get(admcon_value, {"label": "Unknown", "color": "#9F8E6B", "icon": "❓"})

        st.markdown(f"""
        <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; margin-top: 15px; background-color: white;">
            <h4 style="margin-top: 0; color: #333;">Test Score Policy</h4>
            <p style="font-size: 18px; font-weight: bold; margin: 10px 0; color: {policy['color']};">
                {policy['icon']} {policy['label']}
            </p>
            <p style="color: #666; font-size: 0.9rem;">Standardized test scores (SAT/ACT) are {policy['label'].lower()} for admission.</p>
        </div>
        """,
        unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; margin-top: 15px; background-color: white;">
            <h4 style="margin-top: 0; color: #333;">Test Score Policy</h4>
            <p style="font-size: 18px; font-weight: bold; margin: 10px 0; color: #666;">No Information Available</p>
            <p style="color: #666; font-size: 0.9rem;">Contact the university for their test score policy.</p>
        </div>
        """, unsafe_allow_html=True)

@st.cache_data(ttl=300)
def plot_sat_score_card(uni_data, key_prefix=""):
    """
    Display a SAT score card with visual indicator.
    """
    if pd.notna(uni_data.get('SAT_AVG')):
        sat_score = int(uni_data['SAT_AVG'])
        # Determine SAT level with neutral colors (approximate percentiles)
        if sat_score >= 1500:
            sat_level = "Top 1%"
            color = "#5B6ABF"  # Muted blue-purple
        elif sat_score >= 1400:
            sat_level = "Top 5%"
            color = "#6B8E9F"  # Muted blue-gray
        elif sat_score >= 1300:
            sat_level = "Top 10%"
            color = "#7C9A83"  # Muted green-gray
        elif sat_score >= 1200:
            sat_level = "Top 25%"
            color = "#8E9C6B"  # Muted olive
        else:
            sat_level = "National Average Range"
            color = "#9F8E6B"  # Muted tan

        # Calculate percentage for visual (1600 is max SAT)
        sat_percent = min(sat_score / 1600 * 100, 100)

        st.markdown(f"""
        <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; background-color: white;">
            <h4 style="margin-top: 0; color: #333;">Median SAT Score</h4>
            <p style="font-size: 24px; font-weight: bold; margin: 10px 0; color: #333;">{sat_score}</p>
            <p style="color: {color}; font-weight: bold; margin-bottom: 5px;">{sat_level}</p>
            <div style="background-color: #e9ecef; border-radius: 4px; height: 8px;">
                <div style="background-color: {color}; width: {sat_percent}%; height: 100%; border-radius: 4px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; background-color: white;">
            <h4 style="margin-top: 0; color: #333;">Median SAT Score</h4>
            <p style="font-size: 24px; font-weight: bold; margin: 10px 0; color: #333;">N/A</p>
        </div>
        """, unsafe_allow_html=True)

@st.cache_data(ttl=300)
def plot_act_score_card(uni_data, key_prefix=""):
    """
    Display an ACT score card with visual indicator.
    """
    if 'ACTCMMID' in uni_data and pd.notna(uni_data['ACTCMMID']):
        act_score = int(uni_data['ACTCMMID'])
        # Determine ACT level with neutral colors (approximate percentiles)
        if act_score >= 34:
            act_level = "Top 1%"
            color = "#5B6ABF"  # Muted blue-purple
        elif act_score >= 32:
            act_level = "Top 5%"
            color = "#6B8E9F"  # Muted blue-gray
        elif act_score >= 30:
            act_level = "Top 10%"
            color = "#7C9A83"  # Muted green-gray
        elif act_score >= 27:
            act_level = "Top 25%"
            color = "#8E9C6B"  # Muted olive
        else:
            act_level = "National Average Range"
            color = "#9F8E6B"  # Muted tan

        # Calculate percentage for visual (36 is max ACT)
        act_percent = min(act_score / 36 * 100, 100)

        st.markdown(f"""
        <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; background-color: white;">
            <h4 style="margin-top: 0; color: #333;">Median ACT Score</h4>
            <p style="font-size: 24px; font-weight: bold; margin: 10px 0; color: #333;">{act_score}</p>
            <p style="color: {color}; font-weight: bold; margin-bottom: 5px;">{act_level}</p>
            <div style="background-color: #e9ecef; border-radius: 4px; height: 8px;">
                <div style="background-color: {color}; width: {act_percent}%; height: 100%; border-radius: 4px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; background-color: white;">
            <h4 style="margin-top: 0; color: #333;">Median ACT Score</h4>
            <p style="font-size: 24px; font-weight: bold; margin: 10px 0; color: #333;">N/A</p>
        </div>
        """, unsafe_allow_html=True)