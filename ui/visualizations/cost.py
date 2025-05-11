"""
Cost visualizations for the Pathfinder application.
"""

import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_data(ttl=300)
def plot_tuition_distribution(filtered_data):
    """
    Create a box plot of tuition distribution by control type.
    Cached for 5 minutes to improve performance.
    """
    st.markdown("#### Tuition Fee Distribution by Control Type", help="Distribution of annual tuition fees across different types of institutions.")

    # Make a copy to avoid modifying the original dataframe
    plot_data = filtered_data.copy()

    # Only require CONTROL_TYPE and at least one of the tuition columns
    has_in_state = 'TUITIONFEE_IN' in plot_data.columns
    has_out_state = 'TUITIONFEE_OUT' in plot_data.columns

    if 'CONTROL_TYPE' in plot_data.columns and (has_in_state or has_out_state):
        # Prepare columns for melting
        id_vars = ['INSTNM', 'CONTROL_TYPE']
        value_vars = []

        if has_in_state:
            value_vars.append('TUITIONFEE_IN')

        if has_out_state:
            value_vars.append('TUITIONFEE_OUT')

        # Melt the data
        plot_data_melt = plot_data.melt(
            id_vars=id_vars,
            value_vars=value_vars,
            var_name='Tuition Type',
            value_name='Tuition Fee'
        )

        # Map column names to readable labels
        plot_data_melt['Tuition Type'] = plot_data_melt['Tuition Type'].map({
            'TUITIONFEE_IN': 'In-State',
            'TUITIONFEE_OUT': 'Out-of-State'
        })

        # Drop rows with missing tuition values
        plot_data_melt = plot_data_melt.dropna(subset=['Tuition Fee'])

        if not plot_data_melt.empty:
            # Create an enhanced box plot with points
            fig = px.box(
                plot_data_melt,
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
                points="all",  # Show all data points
                height=600     # Increase height for better visibility
            )

            fig.update_layout(
                xaxis_title="Control Type",
                yaxis_title="Annual Tuition Fee ($)",
                yaxis_tickformat="$,.0f"
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Insufficient data for Tuition Fee distribution plot.")
    else:
        st.info("Tuition data not available in the dataset.")

@st.cache_data(ttl=300)
def plot_tuition_vs_size(filtered_data):
    """
    Create a scatter plot of tuition vs. institution size.
    """
    st.markdown("#### Tuition vs. Institution Size", help="Relationship between tuition costs and undergraduate enrollment.")
    plot_data = filtered_data.dropna(subset=['TUITIONFEE_IN', 'UGDS'])
    
    if not plot_data.empty:
        fig = px.scatter(
            plot_data,
            x='UGDS',
            y='TUITIONFEE_IN',
            color='CONTROL_TYPE',
            hover_name='INSTNM',
            title="Tuition vs. Institution Size",
            labels={
                'UGDS': 'Undergraduate Enrollment',
                'TUITIONFEE_IN': 'In-State Tuition ($)',
                'CONTROL_TYPE': 'Institution Type'
            }
        )
        
        fig.update_layout(
            xaxis_title="Undergraduate Enrollment",
            yaxis_title="In-State Tuition ($)",
            yaxis_tickformat="$,.0f"
        )
        
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("Insufficient data for Tuition vs. Size plot.")

@st.cache_data(ttl=300)
def plot_state_tuition_comparison(filtered_data):
    """
    Create a bar chart of average tuition by state.
    """
    st.markdown("#### Average Tuition by State", help="Comparison of average in-state tuition costs across different states.")
    plot_data = filtered_data.dropna(subset=['TUITIONFEE_IN', 'STABBR'])
    
    if not plot_data.empty and len(plot_data['STABBR'].unique()) > 1:
        state_avg = plot_data.groupby('STABBR')['TUITIONFEE_IN'].mean().reset_index()
        state_avg = state_avg.sort_values('TUITIONFEE_IN', ascending=False).head(10)
        
        fig = px.bar(
            state_avg,
            x='STABBR',
            y='TUITIONFEE_IN',
            title="Average In-State Tuition by State (Top 10)",
            labels={'STABBR': 'State', 'TUITIONFEE_IN': 'Average In-State Tuition ($)'},
            color='TUITIONFEE_IN',
            color_continuous_scale='Viridis'
        )
        
        fig.update_layout(
            xaxis_title="State",
            yaxis_title="Average In-State Tuition ($)",
            yaxis_tickformat="$,.0f",
            coloraxis_showscale=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.info("Insufficient data for State Tuition comparison plot.")

@st.cache_data(ttl=300)
def plot_net_price(uni_data):
    """
    Create visualizations for net price data by income bracket.
    """
    # Determine if the institution is public or private
    is_public = uni_data['CONTROL'] == 1 if 'CONTROL' in uni_data else False
    is_private = uni_data['CONTROL'] in [2, 3] if 'CONTROL' in uni_data else False

    # Get the appropriate net price column based on institution type
    net_price_col = 'NPT4_PUB' if is_public else 'NPT4_PRIV' if is_private else None

    # Check if we have overall net price data
    has_net_price = net_price_col in uni_data.index and pd.notna(uni_data[net_price_col])

    # Define income brackets and their corresponding column prefixes
    income_brackets = [
        ('$0-$30,000', 'NPT41'),
        ('$30,001-$48,000', 'NPT42'),
        ('$48,001-$75,000', 'NPT43'),
        ('$75,001-$110,000', 'NPT44'),
        ('$110,001+', 'NPT45')
    ]

    # Get the appropriate suffix based on institution type
    suffix = '_PUB' if is_public else '_PRIV' if is_private else None

    if suffix:
        # Check if we have income bracket data
        bracket_cols = [f"{prefix}{suffix}" for _, prefix in income_brackets]
        has_bracket_data = any(col in uni_data.index and pd.notna(uni_data[col]) for col in bracket_cols)

        if has_bracket_data:
            st.subheader("Net Price by Income")

            # Create data for the chart
            data = []
            for bracket, prefix in income_brackets:
                col = f"{prefix}{suffix}"
                if col in uni_data.index and pd.notna(uni_data[col]):
                    data.append({
                        'Income Bracket': bracket,
                        'Net Price': uni_data[col]
                    })

            if data:
                # Create DataFrame
                df = pd.DataFrame(data)

                # Create the bar chart
                fig = px.bar(
                    df,
                    x='Income Bracket',
                    y='Net Price',
                    title=f"Average Net Price by Family Income",
                    labels={
                        'Income Bracket': 'Family Income',
                        'Net Price': 'Average Net Price ($)'
                    },
                    color='Net Price',
                    color_continuous_scale='Viridis'
                )

                # Add the overall average net price as a line if available
                if has_net_price:
                    overall_avg = uni_data[net_price_col]
                    fig.add_shape(
                        type="line",
                        x0=-0.5,
                        y0=overall_avg,
                        x1=len(income_brackets) - 0.5,
                        y1=overall_avg,
                        line=dict(
                            color="red",
                            width=2,
                            dash="dash",
                        )
                    )
                    fig.add_annotation(
                        x=len(income_brackets) - 1,
                        y=overall_avg,
                        text=f"Overall Avg: ${overall_avg:,.0f}",
                        showarrow=False,
                        yshift=10,
                        font=dict(color="red")
                    )

                # Update layout
                fig.update_layout(
                    yaxis_tickformat="$,.0f",
                    height=500,
                    coloraxis_showscale=False
                )

                # Add value labels on top of bars
                fig.update_traces(
                    text=[f"${val:,.0f}" for val in df['Net Price']],
                    textposition='outside'
                )

                st.plotly_chart(fig, use_container_width=True)


                # Add explanation of net price
                st.markdown("""
                **What is Net Price?**

                Net price is the amount that a student pays to attend an institution in a single academic year after subtracting scholarships and grants.
                It includes tuition and fees, books and supplies, and living expenses like room and board, minus the average grant/scholarship aid.

                This is often a more accurate representation of college costs than the published tuition rates.
                """)
            else:
                st.info("Detailed net price data by income bracket not available for this institution.")
        elif has_net_price:
            # If we only have overall net price but not by income bracket
            st.subheader("Average Net Price")

            # Create a simple card to display the overall net price
            overall_avg = uni_data[net_price_col]
            st.markdown(f"""
            <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 20px; background-color: white; text-align: center;">
                <h3 style="margin-top: 0; color: #333;">Average Net Price</h3>
                <p style="font-size: 36px; font-weight: bold; margin: 15px 0; color: #333;">${overall_avg:,.0f}</p>
                <p style="color: #666;">Average annual cost after financial aid</p>
            </div>
            """, unsafe_allow_html=True)

            # Add explanation of net price
            st.markdown("""
            **What is Net Price?**

            Net price is the amount that a student pays to attend an institution in a single academic year after subtracting scholarships and grants.
            It includes tuition and fees, books and supplies, and living expenses like room and board, minus the average grant/scholarship aid.

            This is often a more accurate representation of college costs than the published tuition rates.
            """)
        else:
            st.info("Net price data not available for this institution.")
    else:
        st.info("Institution type information not available to determine appropriate net price data.")

@st.cache_data(ttl=300)
def plot_tuition_trend(uni_data, hist_data, unitid):
    """
    Create a line chart showing historical tuition trend for a university.
    Cached for 5 minutes to improve performance.
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

                # Create enhanced trend chart
                fig = px.line(
                    trend_data_melt,
                    x='YEAR',
                    y='Amount',
                    color='Tuition Type',
                    title="Historical Tuition (2015-2023)",
                    labels={'YEAR': 'Year', 'Amount': 'Tuition ($)'},
                    markers=True,
                    line_shape='spline'
                )

                # Calculate and display inflation-adjusted values if we have enough data points
                if len(trend_data) > 2:
                    # Create a copy of the data for inflation adjustment
                    # Using a simple 3% annual inflation rate for demonstration
                    inflation_adjusted = trend_data.copy()

                    # Get the most recent year as the base year
                    base_year = inflation_adjusted['YEAR'].max()

                    # Calculate inflation adjustment factors
                    for col in ['TUITIONFEE_IN', 'TUITIONFEE_OUT']:
                        if col in inflation_adjusted.columns:
                            # Create adjusted columns
                            adjusted_col = f"{col}_ADJ"
                            inflation_adjusted[adjusted_col] = inflation_adjusted[col]

                            # Apply inflation adjustment
                            for year in inflation_adjusted['YEAR'].unique():
                                if year != base_year:
                                    # Adjust by 3% per year difference
                                    years_diff = base_year - year
                                    adjustment_factor = (1.03) ** years_diff
                                    mask = inflation_adjusted['YEAR'] == year
                                    inflation_adjusted.loc[mask, adjusted_col] = inflation_adjusted.loc[mask, col] * adjustment_factor

                    # Melt the adjusted data
                    adjusted_melt = inflation_adjusted.melt(
                        id_vars=['YEAR'],
                        value_vars=['TUITIONFEE_IN_ADJ', 'TUITIONFEE_OUT_ADJ'],
                        var_name='Tuition Type',
                        value_name='Amount'
                    )

                    # Map column names to readable labels
                    adjusted_melt['Tuition Type'] = adjusted_melt['Tuition Type'].map({
                        'TUITIONFEE_IN_ADJ': 'In-State (Inflation Adj.)',
                        'TUITIONFEE_OUT_ADJ': 'Out-of-State (Inflation Adj.)'
                    })

                    # Add the adjusted data as dashed lines
                    for tuition_type in adjusted_melt['Tuition Type'].unique():
                        data = adjusted_melt[adjusted_melt['Tuition Type'] == tuition_type]
                        fig.add_scatter(
                            x=data['YEAR'],
                            y=data['Amount'],
                            mode='lines',
                            name=tuition_type,
                            line=dict(dash='dash')
                        )

                # Improve layout
                fig.update_layout(
                    yaxis_tickformat="$,.0f",
                    xaxis_title="Academic Year",
                    yaxis_title="Tuition ($)",
                    legend_title="Tuition Type",
                    hovermode="x unified",
                    xaxis=dict(
                        tickmode='array',
                        tickvals=trend_data['YEAR'].unique(),
                        ticktext=[f"'{str(year)[2:4]}-{str(year+1)[2:4]}" for year in trend_data['YEAR'].unique()]
                    )
                )

                st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("Historical data not available.")
