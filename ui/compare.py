"""
University comparison view for the University Scout application.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from utils import get_download_link, get_figure_download_link, clear_comparison, set_selected_university

def display_comparison_section(selected_unitids, all_data, hist_data, fos_data, rank_data):
    """
    Displays the comparison section for selected universities.

    Args:
        selected_unitids: List of university IDs to compare
        all_data: DataFrame containing all university data
        hist_data: DataFrame containing historical data
        fos_data: DataFrame containing field of study data
        rank_data: DataFrame containing ranking data

    Returns:
        None: Displays content directly using streamlit
    """
    if not selected_unitids:
        st.info("Select universities to compare by checking the 'Compare' box in the table view or clicking the 'Compare' button in card view.")
        return  # Don't display anything if no universities are selected

    st.header("⚖️ University Comparison")

    # Get data for selected universities
    selected_data = all_data[all_data['UNITID'].isin(selected_unitids)].copy()

    if selected_data.empty:
        st.warning("Could not find data for selected universities.")
        return

    # Add action buttons
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader(f"Comparing {len(selected_data)} Universities")
    with col2:
        if st.button("🗑️ Clear Comparison"):
            clear_comparison()
            st.rerun()

    # Define metrics to compare
    comparison_metrics = {
        'ADM_RATE': 'Admission Rate',
        'SAT_AVG': 'Average SAT Score',
        'ACTCMMID': 'Median ACT Score',
        'TUITIONFEE_IN': 'In-State Tuition ($)',
        'TUITIONFEE_OUT': 'Out-of-State Tuition ($)',
        'GRAD_DEBT_MDN': 'Median Graduate Debt ($)',
        'C150_4': '4-Year Graduation Rate (%)',
        'MD_EARN_WNE_P10': 'Median Earnings (10yr) ($)',
        'UGDS': 'Undergraduate Enrollment'
    }

    # Filter metrics that actually exist in the data
    available_metrics = {k: v for k, v in comparison_metrics.items() if k in selected_data.columns}

    # Create tabs for different comparison views with emojis
    comp_tabs = st.tabs(["📊 Overview", "🎓 Academics", "💰 Cost & Aid", "📈 Outcomes", "🌈 Diversity", "🏆 Rankings"])

    # Overview Tab
    with comp_tabs[0]:
        # Display university cards with basic info
        st.subheader("University Overview")

        # Create a grid layout for cards
        cols = st.columns(len(selected_data))

        for i, (_, uni) in enumerate(selected_data.iterrows()):
            with cols[i]:
                # Create a card for each university
                st.markdown(f"""
                <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 1rem; text-align: center;">
                    <h4>{uni['INSTNM']}</h4>
                    <p>{uni['CITY']}, {uni['STABBR']} • {uni['CONTROL_TYPE']}</p>
                </div>
                """, unsafe_allow_html=True)

                # Action buttons
                if st.button(f"View Details", key=f"comp_view_{uni['UNITID']}"):
                    set_selected_university(uni['UNITID'])
                    st.rerun()

                # Display key metrics
                if pd.notna(uni['ADM_RATE']):
                    st.metric("Admission Rate", f"{uni['ADM_RATE']:.1%}")

                if pd.notna(uni['TUITIONFEE_IN']):
                    st.metric("In-State Tuition", f"${int(uni['TUITIONFEE_IN']):,}")

                if pd.notna(uni['C150_4']):
                    st.metric("Graduation Rate", f"{uni['C150_4']:.1%}")

        # Display Comparison Table (Transposed for better readability)
        st.subheader("Key Metrics Comparison")

        # Set INSTNM as index for the comparison table
        comparison_df = selected_data.set_index('INSTNM')[list(available_metrics.keys())].copy()

        # Rename columns for readability
        comparison_df.rename(columns=available_metrics, inplace=True)

        # Format percentages
        for col in ['Admission Rate', '4-Year Graduation Rate (%)']:
            if col in comparison_df.columns:
                comparison_df[col] = comparison_df[col].apply(lambda x: f"{x:.1%}" if pd.notna(x) else "N/A")

        # Format currency/scores
        for col in comparison_df.columns:
            if col not in ['Admission Rate', '4-Year Graduation Rate (%)']:
                comparison_df[col] = comparison_df[col].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A")

        st.dataframe(comparison_df.T, use_container_width=True)  # Transpose the table

        # Download option for comparison data
        st.markdown(
            get_download_link(
                selected_data,
                f"university_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "📥 Download Comparison Data"
            ),
            unsafe_allow_html=True
        )

    # Academics Tab
    with comp_tabs[1]:
        st.subheader("Academic Comparison")

        # Compare SAT/ACT with separate scales
        st.markdown("#### Test Scores")

        # Create two separate visualizations for SAT and ACT
        col1, col2 = st.columns(2)

        # SAT Scores (0-1600 scale)
        with col1:
            if 'SAT_AVG' in selected_data.columns and selected_data['SAT_AVG'].notna().any():
                sat_data = selected_data[['INSTNM', 'SAT_AVG']].copy()
                sat_data = sat_data.dropna(subset=['SAT_AVG'])

                if not sat_data.empty:
                    # Sort by SAT score
                    sat_data = sat_data.sort_values('SAT_AVG', ascending=False)

                    fig_sat = px.bar(
                        sat_data,
                        x='INSTNM',
                        y='SAT_AVG',
                        title="Average SAT Score (0-1600 scale)",
                        labels={'INSTNM': 'University', 'SAT_AVG': 'SAT Score'},
                        color='SAT_AVG',
                        color_continuous_scale='blues'
                    )
                    # Set y-axis range to provide context (typical SAT range)
                    fig_sat.update_layout(yaxis_range=[800, 1600])
                    st.plotly_chart(fig_sat, use_container_width=True)
                else:
                    st.info("SAT score data not available for the selected universities.")
            else:
                st.info("SAT score data not available in the dataset.")

        # ACT Scores (1-36 scale)
        with col2:
            if 'ACTCMMID' in selected_data.columns and selected_data['ACTCMMID'].notna().any():
                act_data = selected_data[['INSTNM', 'ACTCMMID']].copy()
                act_data = act_data.dropna(subset=['ACTCMMID'])

                if not act_data.empty:
                    # Sort by ACT score
                    act_data = act_data.sort_values('ACTCMMID', ascending=False)

                    fig_act = px.bar(
                        act_data,
                        x='INSTNM',
                        y='ACTCMMID',
                        title="Median ACT Score (1-36 scale)",
                        labels={'INSTNM': 'University', 'ACTCMMID': 'ACT Score'},
                        color='ACTCMMID',
                        color_continuous_scale='greens'
                    )
                    # Set y-axis range to provide context (ACT is 1-36)
                    fig_act.update_layout(yaxis_range=[15, 36])
                    st.plotly_chart(fig_act, use_container_width=True)
                else:
                    st.info("ACT score data not available for the selected universities.")
            else:
                st.info("ACT score data not available in the dataset.")

        # Historical Test Score Trends
        st.markdown("#### Historical Test Score Trends")
        if not hist_data.empty:
            # Check if we have historical SAT data for any of the selected universities
            has_historical_data = False
            for unitid in selected_unitids:
                uni_hist = hist_data[hist_data['UNITID'] == unitid]
                if not uni_hist.empty and 'SAT_AVG' in uni_hist.columns and uni_hist['SAT_AVG'].notna().any():
                    has_historical_data = True
                    break

            if has_historical_data:
                # Create a figure for historical SAT scores
                fig_hist_sat = go.Figure()

                for _, uni in selected_data.iterrows():
                    unitid = uni['UNITID']
                    uni_hist = hist_data[hist_data['UNITID'] == unitid]

                    if not uni_hist.empty and 'SAT_AVG' in uni_hist.columns and uni_hist['SAT_AVG'].notna().any():
                        # Prepare data for trend chart
                        trend_data = uni_hist[['YEAR', 'SAT_AVG']].dropna()
                        if not trend_data.empty:
                            trend_data = trend_data.sort_values('YEAR')

                            # Add a line for this university
                            fig_hist_sat.add_trace(go.Scatter(
                                x=trend_data['YEAR'],
                                y=trend_data['SAT_AVG'],
                                mode='lines+markers',
                                name=uni['INSTNM']
                            ))

                if len(fig_hist_sat.data) > 0:
                    fig_hist_sat.update_layout(
                        title="Historical SAT Score Trends",
                        xaxis_title="Year",
                        yaxis_title="Average SAT Score",
                        legend_title="University"
                    )
                    st.plotly_chart(fig_hist_sat, use_container_width=True)
                else:
                    st.info("No historical SAT score data available for the selected universities.")
            else:
                st.info("No historical test score data available for the selected universities.")

        # Compare Admission Rates
        st.markdown("#### Admission Rates")
        if 'ADM_RATE' in selected_data.columns and selected_data['ADM_RATE'].notna().any():
            adm_data = selected_data[['INSTNM', 'ADM_RATE']].copy()
            adm_data = adm_data.dropna(subset=['ADM_RATE'])

            if not adm_data.empty:
                # Sort by admission rate
                adm_data = adm_data.sort_values('ADM_RATE')

                fig_adm = px.bar(
                    adm_data,
                    x='INSTNM',
                    y='ADM_RATE',
                    title="Admission Rate Comparison",
                    labels={'INSTNM': 'University', 'ADM_RATE': 'Admission Rate'},
                    color='ADM_RATE',
                    color_continuous_scale='blues_r'  # Reversed blues (darker = more selective)
                )
                fig_adm.update_layout(yaxis_tickformat=".1%")
                st.plotly_chart(fig_adm, use_container_width=True)

                # Add download option for the chart
                st.markdown(
                    get_figure_download_link(
                        fig_adm,
                        f"admission_rate_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                        "📥 Download Chart"
                    ),
                    unsafe_allow_html=True
                )
            else:
                st.info("Admission rate data not available for the selected universities.")
        else:
            st.info("Admission rate data not available in the dataset.")

    # Cost & Aid Tab
    with comp_tabs[2]:
        st.subheader("Cost & Financial Aid Comparison")

        # Compare Tuition
        st.markdown("#### Tuition")
        tuition_metrics = {k: v for k, v in available_metrics.items() if k in ['TUITIONFEE_IN', 'TUITIONFEE_OUT']}
        if tuition_metrics:
            tuition_data = selected_data[['INSTNM'] + list(tuition_metrics.keys())].copy()
            tuition_data_melt = tuition_data.melt(id_vars='INSTNM', var_name='Metric', value_name='Fee')
            tuition_data_melt['Metric'] = tuition_data_melt['Metric'].map(tuition_metrics)

            if not tuition_data_melt.dropna(subset=['Fee']).empty:
                fig_tuition = px.bar(
                    tuition_data_melt.dropna(subset=['Fee']),
                    x='INSTNM',
                    y='Fee',
                    color='Metric',
                    barmode='group',
                    title="Tuition Comparison",
                    labels={'INSTNM': 'University', 'Fee': 'Annual Tuition ($)', 'Metric': 'Tuition Type'}
                )
                fig_tuition.update_layout(yaxis_tickformat="$,.0f")
                st.plotly_chart(fig_tuition, use_container_width=True)

                # Add download option for the chart
                st.markdown(
                    get_figure_download_link(
                        fig_tuition,
                        f"tuition_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                        "📥 Download Chart"
                    ),
                    unsafe_allow_html=True
                )
            else:
                st.info("Insufficient tuition data for comparison.")
        else:
            st.info("Tuition metrics not available in the dataset.")

        # Compare Debt
        st.markdown("#### Student Debt")
        if 'GRAD_DEBT_MDN' in selected_data.columns and selected_data['GRAD_DEBT_MDN'].notna().any():
            debt_data = selected_data[['INSTNM', 'GRAD_DEBT_MDN']].copy()
            debt_data = debt_data.dropna(subset=['GRAD_DEBT_MDN'])

            if not debt_data.empty:
                fig_debt = px.bar(
                    debt_data,
                    x='INSTNM',
                    y='GRAD_DEBT_MDN',
                    title="Median Graduate Debt Comparison",
                    labels={'INSTNM': 'University', 'GRAD_DEBT_MDN': 'Median Debt ($)'},
                    color='GRAD_DEBT_MDN',
                    color_continuous_scale='reds'
                )
                fig_debt.update_layout(yaxis_tickformat="$,.0f")
                st.plotly_chart(fig_debt, use_container_width=True)

                # Add download option for the chart
                st.markdown(
                    get_figure_download_link(
                        fig_debt,
                        f"debt_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                        "📥 Download Chart"
                    ),
                    unsafe_allow_html=True
                )
            else:
                st.info("Debt data not available for the selected universities.")
        else:
            st.info("Debt data not available in the dataset.")

    # Outcomes Tab
    with comp_tabs[3]:
        st.subheader("Outcomes Comparison")

        # Compare Graduation Rates
        st.markdown("#### Graduation Rates")
        if 'C150_4' in selected_data.columns and selected_data['C150_4'].notna().any():
            grad_data = selected_data[['INSTNM', 'C150_4']].copy()
            grad_data = grad_data.dropna(subset=['C150_4'])

            if not grad_data.empty:
                # Sort by graduation rate
                grad_data = grad_data.sort_values('C150_4', ascending=False)

                fig_grad = px.bar(
                    grad_data,
                    x='INSTNM',
                    y='C150_4',
                    title="4-Year Graduation Rate Comparison",
                    labels={'INSTNM': 'University', 'C150_4': 'Graduation Rate'},
                    color='C150_4',
                    color_continuous_scale='greens'
                )
                fig_grad.update_layout(yaxis_tickformat=".1%")
                st.plotly_chart(fig_grad, use_container_width=True)

                # Add download option for the chart
                st.markdown(
                    get_figure_download_link(
                        fig_grad,
                        f"graduation_rate_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                        "📥 Download Chart"
                    ),
                    unsafe_allow_html=True
                )
            else:
                st.info("Graduation rate data not available for the selected universities.")
        else:
            st.info("Graduation rate data not available in the dataset.")

        # Compare Earnings
        st.markdown("#### Post-Graduation Earnings")
        if 'MD_EARN_WNE_P10' in selected_data.columns and selected_data['MD_EARN_WNE_P10'].notna().any():
            earn_data = selected_data[['INSTNM', 'MD_EARN_WNE_P10']].copy()
            earn_data = earn_data.dropna(subset=['MD_EARN_WNE_P10'])

            if not earn_data.empty:
                # Sort by earnings
                earn_data = earn_data.sort_values('MD_EARN_WNE_P10', ascending=False)

                fig_earn = px.bar(
                    earn_data,
                    x='INSTNM',
                    y='MD_EARN_WNE_P10',
                    title="Median Earnings (10 years after entry) Comparison",
                    labels={'INSTNM': 'University', 'MD_EARN_WNE_P10': 'Median Earnings ($)'},
                    color='MD_EARN_WNE_P10',
                    color_continuous_scale='purples'
                )
                fig_earn.update_layout(yaxis_tickformat="$,.0f")
                st.plotly_chart(fig_earn, use_container_width=True)

                # Add download option for the chart
                st.markdown(
                    get_figure_download_link(
                        fig_earn,
                        f"earnings_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                        "📥 Download Chart"
                    ),
                    unsafe_allow_html=True
                )
            else:
                st.info("Earnings data not available for the selected universities.")
        else:
            st.info("Earnings data not available in the dataset.")

    # Diversity Tab
    with comp_tabs[4]:
        st.subheader("Diversity Comparison")

        # Compare Enrollment
        st.markdown("#### Undergraduate Enrollment")
        if 'UGDS' in selected_data.columns and selected_data['UGDS'].notna().any():
            enroll_data = selected_data[['INSTNM', 'UGDS']].copy()
            enroll_data = enroll_data.dropna(subset=['UGDS'])

            if not enroll_data.empty:
                # Sort by enrollment
                enroll_data = enroll_data.sort_values('UGDS', ascending=False)

                fig_enroll = px.bar(
                    enroll_data,
                    x='INSTNM',
                    y='UGDS',
                    title="Undergraduate Enrollment Comparison",
                    labels={'INSTNM': 'University', 'UGDS': 'Enrollment'},
                    color='UGDS',
                    color_continuous_scale='blues'
                )
                fig_enroll.update_layout(yaxis_tickformat=",d")
                st.plotly_chart(fig_enroll, use_container_width=True)

                # Add download option for the chart
                st.markdown(
                    get_figure_download_link(
                        fig_enroll,
                        f"enrollment_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                        "📥 Download Chart"
                    ),
                    unsafe_allow_html=True
                )
            else:
                st.info("Enrollment data not available for the selected universities.")
        else:
            st.info("Enrollment data not available in the dataset.")

        # Compare Diversity
        st.markdown("#### Student Body Diversity")
        diversity_cols = ['UGDS_WHITE', 'UGDS_BLACK', 'UGDS_HISP', 'UGDS_ASIAN',
                          'UGDS_AIAN', 'UGDS_NHPI', 'UGDS_2MOR', 'UGDS_NRA', 'UGDS_UNKN']

        if all(col in selected_data.columns for col in diversity_cols) and any(selected_data[col].notna().any() for col in diversity_cols):
            # Create a figure with subplots for each university
            fig = go.Figure()

            # Define color map for consistency
            diversity_colors = {
                'UGDS_WHITE': '#636EFA',
                'UGDS_BLACK': '#EF553B',
                'UGDS_HISP': '#00CC96',
                'UGDS_ASIAN': '#AB63FA',
                'UGDS_AIAN': '#FFA15A',
                'UGDS_NHPI': '#19D3F3',
                'UGDS_2MOR': '#FF6692',
                'UGDS_NRA': '#B6E880',
                'UGDS_UNKN': '#FF97FF'
            }

            # Define readable labels
            diversity_labels = {
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

            # Create a subplot for each university
            for i, (_, uni) in enumerate(selected_data.iterrows()):
                # Extract diversity data for this university
                diversity_data = {}
                for col in diversity_cols:
                    if pd.notna(uni[col]):
                        diversity_data[col] = uni[col]

                if diversity_data:
                    # Create a pie chart for this university
                    labels = [diversity_labels[col] for col in diversity_data.keys()]
                    values = list(diversity_data.values())
                    colors = [diversity_colors[col] for col in diversity_data.keys()]

                    fig.add_trace(go.Pie(
                        labels=labels,
                        values=values,
                        name=uni['INSTNM'],
                        title=uni['INSTNM'],
                        domain={'x': [i/len(selected_data), (i+1)/len(selected_data)]},
                        marker_colors=colors
                    ))

            if len(fig.data) > 0:
                fig.update_layout(
                    title="Student Body Diversity Comparison",
                    grid={'rows': 1, 'columns': len(selected_data)},
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)

                # Add download option for the chart
                st.markdown(
                    get_figure_download_link(
                        fig,
                        f"diversity_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                        "📥 Download Chart"
                    ),
                    unsafe_allow_html=True
                )
            else:
                st.info("Diversity data not available for the selected universities.")
        else:
            st.info("Diversity data not available in the dataset.")

    # Rankings Tab
    with comp_tabs[5]:
        st.subheader("Rankings Comparison")

        if not rank_data.empty:
            # Try to match universities with ranking data
            uni_rankings = []

            for _, uni in selected_data.iterrows():
                uni_name = uni['INSTNM']
                # Try to find matches in ranking data
                rank_matches = rank_data[rank_data['institution_name'].str.contains(uni_name, case=False, na=False)]

                if not rank_matches.empty:
                    # Group by source and year to get the most recent ranking for each source
                    rank_matches = rank_matches.sort_values('year', ascending=False)
                    latest_rankings = rank_matches.groupby('source').first().reset_index()

                    # Add university name to the dataframe
                    latest_rankings['university'] = uni_name

                    uni_rankings.append(latest_rankings)

            if uni_rankings:
                # Combine all rankings
                combined_rankings = pd.concat(uni_rankings, ignore_index=True)

                # Create a table of rankings
                st.markdown("#### Latest Rankings")

                # Pivot the data to create a university x source table
                pivot_rankings = combined_rankings.pivot(index='university', columns='source', values='world_rank')

                # Display the pivot table
                st.dataframe(
                    pivot_rankings,
                    use_container_width=True
                )

                # Display rankings in a more meaningful way
                st.markdown("#### World Rankings")

                # Create a more visually appealing display of rankings
                for source in combined_rankings['source'].unique():
                    source_data = combined_rankings[combined_rankings['source'] == source]

                    if not source_data.empty:
                        # Sort by rank
                        source_data = source_data.sort_values('world_rank')

                        # Create a section for this ranking source
                        st.subheader(f"{source} World Rankings")

                        # Add explanation of ranking methodology
                        if source == "Times":
                            st.markdown("""
                            **Times Higher Education World University Rankings** evaluate universities based on:
                            - Teaching (learning environment): 30%
                            - Research (volume, income, and reputation): 30%
                            - Citations (research influence): 30%
                            - International outlook (staff, students, research): 7.5%
                            - Industry income (knowledge transfer): 2.5%
                            """)
                        elif source == "Shanghai":
                            st.markdown("""
                            **Shanghai Academic Ranking of World Universities (ARWU)** evaluates universities based on:
                            - Quality of Education (Alumni winning Nobel Prizes/Fields Medals): 10%
                            - Quality of Faculty (Staff winning Nobel Prizes/Fields Medals): 20%
                            - Quality of Faculty (Highly cited researchers): 20%
                            - Research Output (Papers published in Nature/Science): 20%
                            - Research Output (Papers indexed in Science Citation Index): 20%
                            - Per Capita Performance: 10%
                            """)
                        elif source == "CWUR":
                            st.markdown("""
                            **Center for World University Rankings (CWUR)** evaluates universities based on:
                            - Quality of Education (Alumni success): 25%
                            - Alumni Employment (Career success): 25%
                            - Quality of Faculty (Academic achievements): 10%
                            - Research Performance (Research output, high-quality publications, influence): 40%
                            """)

                        # Display rankings in a clean, visual way
                        cols = st.columns(len(source_data))

                        for i, (_, rank_row) in enumerate(source_data.iterrows()):
                            with cols[i]:
                                # Create a card-like display for each university's ranking
                                st.markdown(f"""
                                <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 1rem; text-align: center; background-color: #f8f9fa;">
                                    <h3 style="color: #1e88e5; margin-bottom: 0.5rem;">{rank_row['world_rank']}</h3>
                                    <p style="font-size: 1.2rem; font-weight: bold;">{rank_row['university']}</p>
                                </div>
                                """, unsafe_allow_html=True)

                        st.markdown("---")
            else:
                st.info("No ranking data found for the selected universities.")
        else:
            st.info("Ranking data is not available.")
