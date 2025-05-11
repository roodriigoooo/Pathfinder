"""
Outcomes visualizations for the Pathfinder application.
"""

import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_data(ttl=300)
def plot_graduation_rate_histogram(filtered_data):
    """
    Create a histogram of 4-year graduation rates.
    """
    st.markdown("#### 4-Year Graduation Rate Distribution",
              help="Distribution of graduation rates for bachelor's degree programs across institutions. Only institutions that report graduation rate data are shown.")

    # Count total institutions vs those with data
    total_institutions = len(filtered_data)
    institutions_with_data = len(filtered_data.dropna(subset=['C150_4']))
    missing_data_pct = (total_institutions - institutions_with_data) / total_institutions * 100 if total_institutions > 0 else 0

    # Add transparency note if significant data is missing
    if missing_data_pct > 10:
        st.caption(f"Note: {missing_data_pct:.0f}% of institutions in your filter are not shown due to missing graduation rate data.")

    plot_data = filtered_data.dropna(subset=['C150_4'])

    if not plot_data.empty:
        # Convert to percentage for display
        plot_data = plot_data.copy()
        plot_data['C150_4_PCT'] = plot_data['C150_4'] * 100

        fig = px.histogram(
            plot_data,
            x='C150_4_PCT',
            nbins=30,
            title="Distribution of 4-Year Graduation Rates (Bachelor's)",
            labels={'C150_4_PCT': '4-Year Graduation Rate (%)'},
            color_discrete_sequence=['#4682B4']  # Steel blue for monochromatic theme
        )

        fig.update_layout(
            xaxis_title="4-Year Graduation Rate (%)",
            yaxis_title="Number of Universities",
            xaxis_tickformat=".0f"
        )

        # Add a vertical line for the average graduation rate
        avg_grad_rate = plot_data['C150_4_PCT'].mean()
        fig.add_vline(x=avg_grad_rate, line_dash="dash", line_color="#0047AB",  # Darker blue for the line
                     annotation_text=f"Average: {avg_grad_rate:.1f}%",
                     annotation_position="top right")

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Insufficient data for 4-Year Graduation Rate histogram.")

@st.cache_data(ttl=300)
def plot_debt_earnings_scatter(filtered_data):
    """
    Create a scatter plot of median debt vs. median earnings.
    """
    st.markdown("#### Median Debt vs. Median Earnings (10yr)",
              help="Relationship between student debt and earnings 10 years after entry, indicating potential return on investment. Only institutions that report both debt and earnings data are shown.")

    # Use DEBT_MDN if available, otherwise fall back to GRAD_DEBT_MDN
    debt_col = 'DEBT_MDN' if 'DEBT_MDN' in filtered_data.columns else 'GRAD_DEBT_MDN'

    # Count total institutions vs those with data
    total_institutions = len(filtered_data)
    institutions_with_data = len(filtered_data.dropna(subset=[debt_col, 'MD_EARN_WNE_P10']))
    missing_data_pct = (total_institutions - institutions_with_data) / total_institutions * 100 if total_institutions > 0 else 0

    # Add transparency note if significant data is missing
    if missing_data_pct > 10:
        st.caption(f"Note: {missing_data_pct:.0f}% of institutions in your filter are not shown due to missing debt or earnings data.")

    plot_data = filtered_data.dropna(subset=[debt_col, 'MD_EARN_WNE_P10'])

    if not plot_data.empty:
        # Calculate debt-to-earnings ratio
        plot_data = plot_data.copy()
        plot_data['Debt_to_Earnings'] = plot_data[debt_col] / plot_data['MD_EARN_WNE_P10']

        # Create a scatter plot with debt-to-earnings ratio as color
        fig = px.scatter(
            plot_data,
            x=debt_col,
            y='MD_EARN_WNE_P10',
            color='Debt_to_Earnings',
            color_continuous_scale=['#0047AB', '#4682B4', '#87CEEB', '#B0E0E6'],  # Monochromatic blue
            hover_name='INSTNM',
            hover_data={
                debt_col: ':$,.0f',
                'MD_EARN_WNE_P10': ':$,.0f',
                'Debt_to_Earnings': ':.2f',
                'CONTROL_TYPE': True
            },
            title="Potential Return on Investment",
            labels={
                debt_col: 'Median Student Debt',
                'MD_EARN_WNE_P10': 'Median Earnings (10 years after entry)',
                'Debt_to_Earnings': 'Debt-to-Earnings Ratio',
                'CONTROL_TYPE': 'Type'
            }
        )

        # Add a diagonal reference line for 1:1 debt-to-earnings ratio
        max_val = max(plot_data[debt_col].max(), plot_data['MD_EARN_WNE_P10'].max())
        fig.add_shape(
            type="line",
            x0=0, y0=0,
            x1=max_val, y1=max_val,
            line=dict(color="gray", width=1, dash="dash"),
        )

        # Add annotation for the reference line
        fig.add_annotation(
            x=max_val*0.7,
            y=max_val*0.8,
            text="1:1 Debt-to-Earnings",
            showarrow=False,
            font=dict(size=10, color="gray")
        )

        fig.update_layout(
            xaxis_title="Median Student Debt ($)",
            yaxis_title="Median Earnings ($)",
            xaxis_tickformat="$,.0f",
            yaxis_tickformat="$,.0f",
            height=600
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Insufficient data for Debt vs. Earnings plot with current filters.")

@st.cache_data(ttl=300)
def plot_graduation_trend(uni_data, hist_data, unitid):
    """
    Create a line chart showing historical graduation rate trend for a university.
    """
    if not hist_data.empty:
        uni_hist = hist_data[hist_data['UNITID'] == unitid]
        if not uni_hist.empty and 'C150_4' in uni_hist.columns and uni_hist['C150_4'].notna().any():
            st.subheader("Graduation Rate Trend")

            # Prepare data for trend chart
            trend_data = uni_hist[['YEAR', 'C150_4']].dropna()
            if not trend_data.empty:
                trend_data = trend_data.sort_values('YEAR')

                # Create enhanced trend chart
                fig = px.line(
                    trend_data,
                    x='YEAR',
                    y='C150_4',
                    title="Historical 4-Year Graduation Rate (2015-2023)",
                    labels={'YEAR': 'Year', 'C150_4': 'Graduation Rate'},
                    markers=True,
                    line_shape='spline'
                )

                # Add a trend line (rolling average)
                if len(trend_data) > 2:
                    trend_data['Rolling_Avg'] = trend_data['C150_4'].rolling(window=min(3, len(trend_data)), min_periods=1).mean()
                    fig.add_scatter(
                        x=trend_data['YEAR'],
                        y=trend_data['Rolling_Avg'],
                        mode='lines',
                        name='3-Year Average',
                        line=dict(color='rgba(0,0,255,0.5)', width=3, dash='dot')
                    )

                    # Add national average for comparison if available
                    # This is obtained National Center of Education Statistics
                    national_avg = pd.DataFrame({
                        'YEAR': trend_data['YEAR'].unique(),
                        'National_Avg': [0.80, 0.82, 0.83, 0.83, 0.84, 0.85, 0.87, 0.88][:len(trend_data['YEAR'].unique())]
                    })

                    if not national_avg.empty and len(national_avg) == len(trend_data['YEAR'].unique()):
                        fig.add_scatter(
                            x=national_avg['YEAR'],
                            y=national_avg['National_Avg'],
                            mode='lines',
                            name='National Average (Est.)',
                            line=dict(color='rgba(255,0,0,0.5)', width=2, dash='dash')
                        )

                # Improve layout
                fig.update_layout(
                    yaxis_tickformat=".1%",
                    xaxis_title="Academic Year",
                    yaxis_title="Graduation Rate",
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
def plot_detailed_debt(uni_data):
    """
    Create a comprehensive visualization of student debt data by different categories.
    """
    # Define all debt-related columns
    debt_columns = {
        'DEBT_MDN': 'Overall Median',
        'GRAD_DEBT_MDN': 'Graduates',
        'WDRAW_DEBT_MDN': 'Withdrawals',
        'FEMALE_DEBT_MDN': 'Female Students',
        'MALE_DEBT_MDN': 'Male Students',
        'FIRSTGEN_DEBT_MDN': 'First-Generation',
        'NOTFIRSTGEN_DEBT_MDN': 'Non-First-Generation'
    }

    # Check which debt columns are available
    available_columns = [col for col in debt_columns.keys() if col in uni_data.index and pd.notna(uni_data[col])]

    if available_columns:
        st.subheader("Student Debt by Category")

        # Create data for the chart
        data = []
        for col in available_columns:
            data.append({
                'Category': debt_columns[col],
                'Debt': uni_data[col]
            })

        # Create DataFrame
        df = pd.DataFrame(data)

        # Sort by debt amount for better visualization
        df = df.sort_values('Debt', ascending=False)

        # Create the bar chart
        fig = px.bar(
            df,
            x='Debt',
            y='Category',
            orientation='h',
            title="Median Debt by Student Category",
            labels={
                'Debt': 'Median Debt ($)',
                'Category': 'Student Category'
            },
            color='Debt',
            color_continuous_scale='Viridis',
            text='Debt'
        )

        # Update layout
        fig.update_layout(
            xaxis_tickformat="$,.0f",
            height=400,
            coloraxis_showscale=False,
            margin=dict(l=20, r=20, t=50, b=20)
        )

        # Add value labels
        fig.update_traces(
            texttemplate='$%{x:,.0f}',
            textposition='outside'
        )

        st.plotly_chart(fig, use_container_width=True)

        # Add context about borrowing rate if available
        if 'FTFTPCTFLOAN' in uni_data.index and pd.notna(uni_data['FTFTPCTFLOAN']):
            borrowing_rate = uni_data['FTFTPCTFLOAN']
            st.markdown(f"""
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                <p style="margin: 0;"><strong>Context:</strong> {borrowing_rate:.1%} of first-time, full-time undergraduate students at this institution take out federal loans.</p>
            </div>
            """, unsafe_allow_html=True)

        # Add explanation
        st.markdown("""
        **Understanding the Debt Categories:**

        - **Overall Median**: Median debt for all student borrowers
        - **Graduates**: Median debt for students who completed their degree
        - **Withdrawals**: Median debt for students who withdrew before completion
        - **Female/Male**: Median debt broken down by gender
        - **First-Generation**: Median debt for students whose parents did not complete college
        - **Non-First-Generation**: Median debt for students whose parents completed college

        *Note: Lower median debt for withdrawals may simply reflect less time spent at the institution rather than lower costs.*
        """)
    else:
        st.info("Detailed debt information by category is not available for this institution.")

@st.cache_data(ttl=300)
def plot_debt_comparison(uni_data, hist_data, unitid):
    """
    Create a visualization comparing debt levels across years if historical data is available.
    """
    if not hist_data.empty:
        uni_hist = hist_data[hist_data['UNITID'] == unitid]

        # Check if we have debt data in the historical dataset
        if 'DEBT_MDN' in uni_hist.columns and uni_hist['DEBT_MDN'].notna().any():
            st.subheader("Historical Debt Trends")

            # Prepare data for trend chart
            trend_data = uni_hist[['YEAR', 'DEBT_MDN']].dropna()
            if not trend_data.empty:
                trend_data = trend_data.sort_values('YEAR')

                # Create trend chart
                fig = px.line(
                    trend_data,
                    x='YEAR',
                    y='DEBT_MDN',
                    title="Median Student Debt Over Time",
                    labels={'YEAR': 'Year', 'DEBT_MDN': 'Median Debt'},
                    markers=True,
                    line_shape='spline'
                )

                # Add a trend line (rolling average)
                if len(trend_data) > 2:
                    trend_data['Rolling_Avg'] = trend_data['DEBT_MDN'].rolling(window=min(3, len(trend_data)), min_periods=1).mean()
                    fig.add_scatter(
                        x=trend_data['YEAR'],
                        y=trend_data['Rolling_Avg'],
                        mode='lines',
                        name='3-Year Average',
                        line=dict(color='rgba(0,0,255,0.5)', width=3, dash='dot')
                    )

                # Improve layout
                fig.update_layout(
                    xaxis_title="Academic Year",
                    yaxis_title="Median Debt ($)",
                    yaxis_tickformat="$,.0f",
                    legend_title="Metric",
                    hovermode="x unified",
                    xaxis=dict(
                        tickmode='array',
                        tickvals=trend_data['YEAR'].unique(),
                        ticktext=[f"'{str(year)[2:4]}-{str(year+1)[2:4]}" for year in trend_data['YEAR'].unique()]
                    )
                )

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Historical debt trend data not available for this institution.")
        else:
            st.info("Historical debt data not available for this institution.")
    else:
        st.info("Historical data not available.")

@st.cache_data(ttl=300)
def plot_graduation_rate_card(uni_data, key_prefix=""):
    """
    Display a graduation rate card with visual gauge.
    """
    if pd.notna(uni_data.get('C150_4')):
        grad_rate = uni_data['C150_4']

        # Determine graduation rate level with neutral colors
        if grad_rate >= 0.9:
            grad_level = "Excellent"
            color = "#5B6ABF"  # Muted blue-purple
        elif grad_rate >= 0.75:
            grad_level = "Very Good"
            color = "#6B8E9F"  # Muted blue-gray
        elif grad_rate >= 0.6:
            grad_level = "Good"
            color = "#7C9A83"  # Muted green-gray
        elif grad_rate >= 0.4:
            grad_level = "Fair"
            color = "#8E9C6B"  # Muted olive
        else:
            grad_level = "Below Average"
            color = "#9F8E6B"  # Muted tan

        # Create a circular gauge for graduation rate
        st.markdown(f"""
        <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 20px; margin-bottom: 20px; background-color: #f8f9fa; text-align: center;">
            <h3 style="margin-top: 0;">4-Year Graduation Rate</h3>
            <div style="position: relative; width: 150px; height: 150px; margin: 0 auto;">
                <svg viewBox="0 0 36 36" style="width: 100%; height: 100%;">
                    <path d="M18 2.0845
                        a 15.9155 15.9155 0 0 1 0 31.831
                        a 15.9155 15.9155 0 0 1 0 -31.831"
                        fill="none" stroke="#e9ecef" stroke-width="3" stroke-dasharray="100, 100" />
                    <path d="M18 2.0845
                        a 15.9155 15.9155 0 0 1 0 31.831
                        a 15.9155 15.9155 0 0 1 0 -31.831"
                        fill="none" stroke="{color}" stroke-width="3" stroke-dasharray="{grad_rate * 100}, 100" />
                    <text x="18" y="20.5" text-anchor="middle" font-size="8" font-weight="bold" fill="{color}">{grad_rate:.1%}</text>
                </svg>
            </div>
            <p style="color: {color}; font-weight: bold; margin-top: 10px;">{grad_level} Graduation Rate</p>
        </div>
        """,
        unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 20px; margin-bottom: 20px; background-color: #f8f9fa; text-align: center;">
            <h3 style="margin-top: 0;">4-Year Graduation Rate</h3>
            <p style="font-size: 24px; font-weight: bold; margin: 10px 0;">N/A</p>
        </div>
        """, unsafe_allow_html=True)


@st.cache_data(ttl=300)
def plot_detailed_debt_comparison(filtered_data):
    """
    Create a comprehensive visualization comparing student debt data by different categories
    across multiple universities.
    """
    # Define all debt-related columns
    debt_columns = {
        'DEBT_MDN': 'Overall Median',
        'GRAD_DEBT_MDN': 'Graduates',
        'WDRAW_DEBT_MDN': 'Withdrawals',
        'FEMALE_DEBT_MDN': 'Female Students',
        'MALE_DEBT_MDN': 'Male Students',
        'FIRSTGEN_DEBT_MDN': 'First-Generation',
        'NOTFIRSTGEN_DEBT_MDN': 'Non-First-Generation'
    }

    # Add help text explaining the visualization
    st.markdown("""
    <div style="margin-bottom: 15px;">
        <p style="margin: 0; font-size: 0.9rem;">
            This visualization shows debt by different student categories. Not all institutions report data for all categories.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Check which debt columns are available in the dataset
    available_columns = [col for col in debt_columns.keys()
                        if col in filtered_data.columns
                        and filtered_data[col].notna().any()]

    if not available_columns:
        st.info("No detailed debt data available for the filtered universities.")
        return

@st.cache_data(ttl=300)
def plot_admission_debt_earnings_ratio(filtered_data):
    """
    Create a visualization showing the relationship between admission rates
    and debt-to-earnings ratios.

    Args:
        filtered_data: DataFrame containing university data

    Returns:
        None: Displays the plot directly using streamlit
    """
    st.markdown("#### Admission Selectivity vs. Financial Outcomes", help='Lower debt-to-earnings ratios indicate better financial outcomes. The dashed line represents a 1:1 ratio where debt equals annual earnings.')

    # Use DEBT_MDN if available, otherwise fall back to GRAD_DEBT_MDN
    debt_col = 'DEBT_MDN' if 'DEBT_MDN' in filtered_data.columns else 'GRAD_DEBT_MDN'

    # Filter data and create a copy to avoid modifying the original
    plot_data = filtered_data.dropna(subset=['ADM_RATE', debt_col, 'MD_EARN_WNE_P10']).copy()

    if not plot_data.empty:
        # Calculate debt-to-earnings ratio
        plot_data['Debt_to_Earnings'] = plot_data[debt_col] / plot_data['MD_EARN_WNE_P10']

        # Convert admission rate to percentage for display
        plot_data['Admission_Rate_Pct'] = plot_data['ADM_RATE'] * 100

        # Create a categorical variable for institution type
        plot_data['Institution_Type'] = plot_data['CONTROL_TYPE'].fillna('Unknown')

        # Create the scatter plot
        fig = px.scatter(
            plot_data,
            x='Admission_Rate_Pct',
            y='Debt_to_Earnings',
            color='Institution_Type',
            size='UGDS',  # Size by undergraduate enrollment
            size_max=20,
            hover_name='INSTNM',
            hover_data={
                'Admission_Rate_Pct': ':.1f',
                'Debt_to_Earnings': ':.2f',
                debt_col: ':$,.0f',
                'MD_EARN_WNE_P10': ':$,.0f',
                'UGDS': ':,.0f',
                'Institution_Type': True
            },
            labels={
                'Admission_Rate_Pct': 'Admission Rate (%)',
                'Debt_to_Earnings': 'Debt-to-Earnings Ratio',
                'Institution_Type': 'Institution Type',
                'UGDS': 'Undergraduate Enrollment'
            }
        )

        # Add a reference line for 1:1 debt-to-earnings ratio
        fig.add_shape(
            type="line",
            x0=0, y0=1.0,
            x1=100, y1=1.0,
            line=dict(color="gray", width=1, dash="dash"),
        )

        # Update layout
        fig.update_layout(
            title="Relationship Between Selectivity and Financial Outcomes",
            xaxis_title="Admission Rate (%). Size of points represents undergraduate enrollment.",
            yaxis_title="Debt-to-Earnings Ratio",
            height=600,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            xaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(211,211,211,0.3)',
                zeroline=False
            ),
            yaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(211,211,211,0.3)',
                zeroline=False
            )
        )

        # Display the plot
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Insufficient data for Admission Rate vs. Debt-to-Earnings plot with current filters.")

