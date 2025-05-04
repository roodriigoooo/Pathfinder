"""
Explore universities tab for the University Scout application.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from utils import (
    get_download_link, add_to_shortlist, remove_from_shortlist,
    set_selected_university, toggle_university_selection
)
import visualizations as viz

def display_main_content(filtered_data, all_data, historical_data, fos_data, ranking_data):
    """
    Displays the filtered data table (with selection) and visualizations.

    Args:
        filtered_data: DataFrame containing filtered university data
        all_data: DataFrame containing all university data
        historical_data: DataFrame containing historical data
        fos_data: DataFrame containing field of study data
        ranking_data: DataFrame containing ranking data

    Returns:
        None: Displays content directly using streamlit
    """
    # Display count and download option with emoji
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader(f"🔍 Filtered Universities ({len(filtered_data)} found)")
    with col2:
        if not filtered_data.empty:
            # Create a download link for the filtered data
            st.markdown(
                get_download_link(
                    filtered_data,
                    f"filtered_universities_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    "📥 Download Filtered List"
                ),
                unsafe_allow_html=True
            )

    # Display shortlist management section with emoji
    if 'shortlisted_universities' in st.session_state and st.session_state.shortlisted_universities:
        with st.expander("📋 Manage Shortlist", expanded=False):
            shortlist_df = all_data[all_data['UNITID'].isin(st.session_state.shortlisted_universities)].copy()
            st.write(f"✅ You have {len(shortlist_df)} universities in your shortlist")

            # Download options for shortlist
            if st.button("🗑️ Clear Shortlist", key="clear_shortlist_button"):
                st.session_state.shortlisted_universities = []
                st.rerun()

            st.markdown(
                get_download_link(
                    shortlist_df,
                    f"shortlisted_universities_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    "📥 Download Shortlist as CSV"
                ),
                unsafe_allow_html=True
            )

    # Display optimized table view
    display_table_view(filtered_data)

    # --- Enhanced Visualizations Section ---
    if not filtered_data.empty and len(filtered_data) > 1:
        st.header("📊 Data Visualizations")
        st.write("Explore the data through interactive visualizations to gain deeper insights.")

        # Create tabs for different visualization categories
        viz_tabs = st.tabs(["🎯 Selectivity", "💰 Cost", "📈 Outcomes", "🏫 Institution Types", "🌈 Diversity"])

        # Selectivity Tab
        with viz_tabs[0]:
            st.subheader("University Selectivity Analysis")
            viz.plot_selectivity_scatter(filtered_data)

            # Add a second row with additional visualizations
            col1, col2 = st.columns(2)
            with col1:
                # Add admission rate histogram
                if 'ADM_RATE' in filtered_data.columns:
                    st.markdown("#### Admission Rate Distribution")
                    plot_data = filtered_data.dropna(subset=['ADM_RATE'])
                    if not plot_data.empty:
                        fig = px.histogram(
                            plot_data,
                            x='ADM_RATE',
                            nbins=20,
                            title="Distribution of Admission Rates",
                            labels={'ADM_RATE': 'Admission Rate'}
                        )
                        fig.update_layout(
                            xaxis_title="Admission Rate",
                            yaxis_title="Number of Universities",
                            xaxis_tickformat=".0%"
                        )
                        st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Add test score box plot
                if 'SAT_AVG' in filtered_data.columns:
                    st.markdown("#### SAT Score by Institution Type")
                    plot_data = filtered_data.dropna(subset=['SAT_AVG', 'CONTROL_TYPE'])
                    if not plot_data.empty:
                        fig = px.box(
                            plot_data,
                            x='CONTROL_TYPE',
                            y='SAT_AVG',
                            title="SAT Score Distribution by Institution Type",
                            labels={'CONTROL_TYPE': 'Institution Type', 'SAT_AVG': 'Average SAT Score'}
                        )
                        st.plotly_chart(fig, use_container_width=True)

        # Cost Tab
        with viz_tabs[1]:
            st.subheader("Cost Analysis")
            viz.plot_tuition_distribution(filtered_data)

            # Add a second row with additional cost visualizations
            col1, col2 = st.columns(2)
            with col1:
                # Add tuition vs. size scatter plot
                if all(col in filtered_data.columns for col in ['TUITIONFEE_IN', 'UGDS']):
                    st.markdown("#### Tuition vs. Institution Size")
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

            with col2:
                # Add state tuition comparison
                if all(col in filtered_data.columns for col in ['TUITIONFEE_IN', 'STABBR']):
                    st.markdown("#### Average Tuition by State")
                    plot_data = filtered_data.dropna(subset=['TUITIONFEE_IN', 'STABBR'])
                    if not plot_data.empty and len(plot_data['STABBR'].unique()) > 1:
                        state_avg = plot_data.groupby('STABBR')['TUITIONFEE_IN'].mean().reset_index()
                        state_avg = state_avg.sort_values('TUITIONFEE_IN', ascending=False).head(10)

                        fig = px.bar(
                            state_avg,
                            x='STABBR',
                            y='TUITIONFEE_IN',
                            title="Average In-State Tuition by State (Top 10)",
                            labels={'STABBR': 'State', 'TUITIONFEE_IN': 'Average In-State Tuition ($)'}
                        )
                        fig.update_layout(
                            xaxis_title="State",
                            yaxis_title="Average In-State Tuition ($)",
                            yaxis_tickformat="$,.0f"
                        )
                        st.plotly_chart(fig, use_container_width=True)

        # Outcomes Tab
        with viz_tabs[2]:
            st.subheader("Student Outcomes Analysis")

            # Graduation rate visualization
            viz.plot_graduation_rate_histogram(filtered_data)

            # Add ROI visualization
            if all(col in filtered_data.columns for col in ['GRAD_DEBT_MDN', 'MD_EARN_WNE_P10']):
                viz.plot_debt_earnings_scatter(filtered_data)

        # Institution Types Tab
        with viz_tabs[3]:
            st.subheader("Institution Types Analysis")

            # Control type distribution
            viz.plot_control_type_distribution(filtered_data)

            # Add institution size distribution
            if 'UGDS' in filtered_data.columns:
                st.markdown("#### Institution Size Distribution")
                plot_data = filtered_data.dropna(subset=['UGDS', 'CONTROL_TYPE'])
                if not plot_data.empty:
                    # Create size categories
                    plot_data['Size Category'] = pd.cut(
                        plot_data['UGDS'],
                        bins=[0, 1000, 5000, 15000, 30000, float('inf')],
                        labels=['Very Small (<1K)', 'Small (1K-5K)', 'Medium (5K-15K)', 'Large (15K-30K)', 'Very Large (>30K)']
                    )

                    size_counts = plot_data.groupby(['CONTROL_TYPE', 'Size Category']).size().reset_index(name='count')

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
                        barmode='group'
                    )
                    st.plotly_chart(fig, use_container_width=True)

        # Diversity Tab
        with viz_tabs[4]:
            st.subheader("Diversity Analysis")

            # Average diversity composition
            viz.plot_diversity_composition(filtered_data)

            # Add gender ratio visualization if available
            if 'UGDS_MEN' in filtered_data.columns and 'UGDS_WOMEN' in filtered_data.columns:
                st.markdown("#### Gender Ratio by Institution Type")
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
                        barmode='stack'
                    )
                    fig.update_layout(yaxis_tickformat=".0%")
                    st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("ℹ️ No universities match the current filter criteria or not enough data for visualizations.")

def display_table_view(filtered_data):
    """
    Displays universities in an optimized table view with selection options.

    Args:
        filtered_data: DataFrame containing filtered university data

    Returns:
        None: Displays content directly using streamlit
    """
    # Initialize session state for tracking changes
    if 'last_shortlist_action' not in st.session_state:
        st.session_state.last_shortlist_action = None

    # Create a lightweight copy with only necessary columns
    essential_columns = ['UNITID', 'INSTNM', 'CITY', 'STABBR', 'CONTROL_TYPE',
                         'ADM_RATE', 'SAT_AVG', 'TUITIONFEE_IN', 'C150_4']

    # Filter columns that exist in the dataframe
    available_columns = [col for col in essential_columns if col in filtered_data.columns]
    display_df = filtered_data[available_columns].copy()

    # Add interaction columns
    display_df.insert(0, 'Select', display_df['UNITID'].isin(st.session_state.selected_universities))
    display_df.insert(1, 'Shortlist', display_df['UNITID'].isin(st.session_state.shortlisted_universities))

    # Create optimized column configuration
    column_config = {
        "Select": st.column_config.CheckboxColumn("Compare"),
        "Shortlist": st.column_config.CheckboxColumn("Shortlist"),
        "INSTNM": st.column_config.TextColumn("Institution Name"),
        "CITY": st.column_config.TextColumn("City"),
        "STABBR": st.column_config.TextColumn("State"),
        "CONTROL_TYPE": st.column_config.TextColumn("Type")
    }

    # Add numeric columns with formatting if they exist
    if 'ADM_RATE' in display_df.columns:
        column_config["ADM_RATE"] = st.column_config.NumberColumn("Admission Rate", format="%.1f%%")
    if 'SAT_AVG' in display_df.columns:
        column_config["SAT_AVG"] = st.column_config.NumberColumn("Avg SAT")
    if 'TUITIONFEE_IN' in display_df.columns:
        column_config["TUITIONFEE_IN"] = st.column_config.NumberColumn("In-State Tuition", format="$%d")
    if 'C150_4' in display_df.columns:
        column_config["C150_4"] = st.column_config.NumberColumn("Graduation Rate", format="%.1f%%")

    # Add a helper message
    st.info("✏️ Check the boxes to select universities for shortlisting or comparison, then click 'Apply Changes' to save your selections.")

    # Display the optimized data editor
    edited_df = st.data_editor(
        display_df,
        key="university_selector",
        disabled=list(set(display_df.columns) - set(['Select', 'Shortlist'])),
        hide_index=True,
        column_config=column_config,
        use_container_width=True,
        on_change=None  # Prevent automatic rerun on change
    )

    # Add an apply button to save changes
    col1, col2 = st.columns([4, 1])
    with col2:
        apply_changes = st.button("✅ Apply Changes", key="apply_shortlist_changes")

    # Process selections when apply button is clicked
    if apply_changes and 'UNITID' in edited_df.columns:
        # Update selected universities
        selected_unitids = edited_df.loc[edited_df['Select'], 'UNITID'].tolist()

        # Get newly shortlisted universities
        shortlisted_unitids = edited_df.loc[edited_df['Shortlist'], 'UNITID'].tolist()

        # Update both lists at once to avoid multiple reruns
        st.session_state.selected_universities = selected_unitids
        st.session_state.shortlisted_universities = shortlisted_unitids

        # Show confirmation
        st.success(f"✅ Updated: {len(shortlisted_unitids)} universities shortlisted, {len(selected_unitids)} selected for comparison")

        # Store the last action for debugging
        st.session_state.last_shortlist_action = {
            'shortlisted': shortlisted_unitids,
            'selected': selected_unitids
        }

# Card view has been removed to improve performance
