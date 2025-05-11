"""
Explore universities tab for Pathfinder.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from utils import (
    get_download_link, add_to_shortlist, remove_from_shortlist,
    set_selected_university, toggle_university_selection
)
from ui.visualizations.academic import (
    plot_selectivity_scatter,
    plot_sat_distribution,
    plot_test_policy_distribution
)
from ui.visualizations.cost import (
    plot_tuition_distribution,
    plot_tuition_vs_size,
    plot_state_tuition_comparison
)
from ui.visualizations.outcomes import (
    plot_graduation_rate_histogram,
    plot_debt_earnings_scatter,
    plot_admission_debt_earnings_ratio
)
from ui.visualizations.institution import (
    plot_control_type_distribution,
    plot_institution_size_distribution
)
from ui.visualizations.diversity import (
    plot_diversity_composition,
    plot_diversity_comparison_by_control,
    plot_gender_comparison,
    plot_gender_ratio_by_type,
    plot_staff_diversity_composition,
    plot_staff_gender_ratio_by_type
)

def display_main_content(filtered_data, all_data, historical_data, fos_data):
    """
    Displays the filtered data table (with selection) and visualizations.
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

    # Removed 'Manage Shortlist' widget to simplify the UI, which i realized makes no sense...
    # Users can manage their shortlist in the dedicated 'My Universities' tab

    # Display optimized table view
    display_table_view(filtered_data)

    if not filtered_data.empty and len(filtered_data) > 1:
        st.header("📊 University Insights")
        st.write("Explore patterns and trends across universities through interactive visualizations.")

        # Create tabs for different visualization categories
        viz_tabs = st.tabs(["🎯 Selectivity", "💰 Cost", "📈 Outcomes", "🏫 Institution Types", "🌈 Diversity"])

        # Selectivity Tab
        with viz_tabs[0]:
            st.subheader("University Selectivity Analysis")
            plot_selectivity_scatter(filtered_data)

            # Add SAT score distribution
            plot_sat_distribution(filtered_data)

            # Add test score policy visualization
            plot_test_policy_distribution(filtered_data)

        # Cost Tab
        with viz_tabs[1]:
            st.subheader("Cost Analysis")
            # Tuition distribution by control type
            plot_tuition_distribution(filtered_data)

            # Tuition vs. institution size
            plot_tuition_vs_size(filtered_data)

            # State tuition comparison
            plot_state_tuition_comparison(filtered_data)

        # Outcomes Tab
        with viz_tabs[2]:
            st.subheader("Student Outcomes Analysis")

            # Graduation rate visualization
            plot_graduation_rate_histogram(filtered_data)

            # Add ROI visualization
            plot_debt_earnings_scatter(filtered_data)

            # Add Admission Rate vs. Debt-to-Earnings visualization
            plot_admission_debt_earnings_ratio(filtered_data)

        # Institution Types Tab
        with viz_tabs[3]:
            st.subheader("Institution Types Analysis")

            # Control type distribution
            plot_control_type_distribution(filtered_data)

            # Institution size distribution
            plot_institution_size_distribution(filtered_data)

        # Diversity Tab
        with viz_tabs[4]:
            st.subheader("Diversity Analysis")

            # Create subtabs for different diversity visualizations
            diversity_subtabs = st.tabs(["Racial/Ethnic Diversity", "Gender Distribution", "Staff Diversity"])

            # Racial/Ethnic Diversity Tab
            with diversity_subtabs[0]:
                # Average undergraduate diversity composition
                plot_diversity_composition(filtered_data)

                # Diversity by institution type
                plot_diversity_comparison_by_control(filtered_data)

            # Gender Distribution Tab
            with diversity_subtabs[1]:
                # Gender comparison between students and staff
                plot_gender_comparison(filtered_data)

                # Gender ratio by institution type
                plot_gender_ratio_by_type(filtered_data)

            # Staff Diversity Tab
            with diversity_subtabs[2]:
                # Staff diversity composition
                plot_staff_diversity_composition(filtered_data)

                # Staff gender ratio by institution type
                plot_staff_gender_ratio_by_type(filtered_data)
    else:
        st.info("ℹ️ No universities match the current filter criteria or not enough data for visualizations.")

def display_table_view(filtered_data):
    """
    Displays universities in an optimized table view with selection options.
    """
    # Initialize session state for tracking changes
    if 'last_shortlist_action' not in st.session_state:
        st.session_state.last_shortlist_action = None

    # Create a lightweight copy with only necessary columns
    essential_columns = ['UNITID', 'INSTNM', 'CITY', 'STABBR', 'CONTROL_TYPE',
                         'ADM_RATE', 'SAT_AVG', 'TUITIONFEE_IN', 'C150_4', 'ADMCON7']

    # Filter columns that exist in the dataframe
    available_columns = [col for col in essential_columns if col in filtered_data.columns]
    display_df = filtered_data[available_columns].copy()

    # Add shortlist column
    display_df.insert(0, 'Shortlist', display_df['UNITID'].isin(st.session_state.shortlisted_universities))

    # Create optimized column configuration
    column_config = {
        "Shortlist": st.column_config.CheckboxColumn("Shortlist"),
        "INSTNM": st.column_config.TextColumn("Institution Name"),
        "CITY": st.column_config.TextColumn("City"),
        "STABBR": st.column_config.TextColumn("State"),
        "CONTROL_TYPE": st.column_config.TextColumn("Type")
    }

    # Add numeric columns with formatting if they exist
    if 'ADM_RATE' in display_df.columns:
        # Convert admission rate from decimal to percentage for display
        display_df['ADM_RATE'] = display_df['ADM_RATE'] * 100
        column_config["ADM_RATE"] = st.column_config.NumberColumn("Admission Rate", format="%.1f%%")
    if 'SAT_AVG' in display_df.columns:
        column_config["SAT_AVG"] = st.column_config.NumberColumn("Avg SAT")
    if 'TUITIONFEE_IN' in display_df.columns:
        column_config["TUITIONFEE_IN"] = st.column_config.NumberColumn("In-State Tuition", format="$%d")
    if 'C150_4' in display_df.columns:
        # Convert graduation rate from decimal to percentage for display
        display_df['C150_4'] = display_df['C150_4'] * 100
        column_config["C150_4"] = st.column_config.NumberColumn("Graduation Rate", format="%.1f%%")
    if 'ADMCON7' in display_df.columns:
        # Map ADMCON7 values to readable labels
        policy_map = {
            1: "Required",
            2: "Recommended",
            3: "Neither Required/Recommended",
            4: "Unknown",
            5: "Considered but not Required"
        }
        # Create a new column with the mapped values
        display_df['Test_Policy'] = display_df['ADMCON7'].apply(
            lambda x: policy_map.get(int(x), "Unknown") if pd.notna(x) else "Unknown"
        )
        # Add the column to the display and remove the raw ADMCON7 column
        column_config["Test_Policy"] = st.column_config.TextColumn("Test Score Policy")
        display_df = display_df.drop(columns=['ADMCON7'])

    # Add a helper message
    st.info("✏️ Check the boxes to shortlist universities, then click 'Apply Changes' to save your selections.")

    # Display the optimized data editor
    edited_df = st.data_editor(
        display_df,
        key="university_selector",
        disabled=list(set(display_df.columns) - set(['Shortlist'])),
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
        # Get newly shortlisted universities
        shortlisted_unitids = edited_df.loc[edited_df['Shortlist'], 'UNITID'].tolist()

        # Get previously shortlisted universities
        previously_shortlisted = set(st.session_state.shortlisted_universities)
        newly_shortlisted = set(shortlisted_unitids) - previously_shortlisted
        removed_from_shortlist = previously_shortlisted - set(shortlisted_unitids)

        # Update shortlist and automatically select them for comparison
        st.session_state.shortlisted_universities = shortlisted_unitids
        st.session_state.selected_universities = shortlisted_unitids

        # Show confirmation with toast notifications
        if newly_shortlisted:
            # Show toast for newly added universities (up to 3)
            added_names = []
            for unitid in list(newly_shortlisted)[:3]:
                uni_name = filtered_data.loc[filtered_data['UNITID'] == unitid, 'INSTNM'].iloc[0]
                added_names.append(uni_name)

            if len(newly_shortlisted) <= 3:
                for name in added_names:
                    st.toast(f"Added {name} to your shortlist", icon="✅")
            else:
                st.toast(f"Added {len(newly_shortlisted)} universities to your shortlist", icon="✅")

        if removed_from_shortlist:
            # Show toast for removed universities
            if len(removed_from_shortlist) == 1:
                unitid = list(removed_from_shortlist)[0]
                uni_name = filtered_data.loc[filtered_data['UNITID'] == unitid, 'INSTNM'].iloc[0]
                st.toast(f"Removed {uni_name} from your shortlist", icon="🗑️")
            else:
                st.toast(f"Removed {len(removed_from_shortlist)} universities from your shortlist", icon="🗑️")

        # Store the last action for debugging
        st.session_state.last_shortlist_action = {
            'shortlisted': shortlisted_unitids,
            'selected': shortlisted_unitids  # Now selected is the same as shortlisted
        }

# Originally, the institutions were returned as formatted, styled 'cards'. This was too slow to run, given the amount of them. At the end I decided to just do a 'smart' table.
