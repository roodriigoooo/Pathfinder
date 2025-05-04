"""
University Scout - A tool to help students explore and shortlist universities.
"""

import streamlit as st

# Import configuration
from config import COLUMNS_TO_LOAD, NUMERIC_COLUMNS

# Import data loading functions
from data_loader import (
    load_institution_data,
    load_historical_data,
    load_field_of_study_data,
    load_ranking_data
)

# Import utility functions
from utils import (
    initialize_session_state,
    apply_custom_css
)

# Import UI components
from Pathfinder.ui import display_sidebar_filters
from Pathfinder.ui import display_main_content
from Pathfinder.ui import display_university_details
from Pathfinder.ui import display_comparison_section
from Pathfinder.ui import display_find_my_fit
from Pathfinder.ui.shortlist import display_shortlist


def main():
    """Main application entry point."""
    # Set page configuration
    st.set_page_config(
        page_title="Pathfinder",
        page_icon=":books:",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Apply custom CSS
    apply_custom_css()

    # Initialize session state
    initialize_session_state()

    # Load the data with performance optimizations
    data = load_institution_data(COLUMNS_TO_LOAD, NUMERIC_COLUMNS, sample_fraction=0.5)
    historical_data = load_historical_data()
    fos_data = load_field_of_study_data()
    ranking_data = load_ranking_data()

    if not data.empty:
        # Check if we need to show university details
        if st.session_state.active_tab == "Details" and st.session_state.selected_university_id is not None:
            # Display university details
            display_university_details(
                st.session_state.selected_university_id,
                data,
                historical_data,
                fos_data,
                ranking_data
            )
        else:
            # Display sidebar filters and get selections
            filter_options = display_sidebar_filters(data)

            # Apply Filters
            filtered_data = data[
                (data['STABBR'].isin(filter_options["states"])) &
                (data['CONTROL_TYPE'].isin(filter_options["control_types"]))
            ]

            # Apply admission rate filter
            if 'ADM_RATE' in filtered_data.columns and filtered_data['ADM_RATE'].notna().any():
                filtered_data = filtered_data[
                    (filtered_data['ADM_RATE'] >= filter_options["adm_rate"][0]) &
                    (filtered_data['ADM_RATE'] <= filter_options["adm_rate"][1]) |
                    (filtered_data['ADM_RATE'].isna())
                ]

            # Apply SAT score filter if available
            if filter_options["sat"] is not None and 'SAT_AVG' in filtered_data.columns:
                filtered_data = filtered_data[
                    (filtered_data['SAT_AVG'] >= filter_options["sat"][0]) &
                    (filtered_data['SAT_AVG'] <= filter_options["sat"][1]) |
                    (filtered_data['SAT_AVG'].isna())
                ]

            # Apply tuition filter if available
            if filter_options["tuition"] is not None and 'TUITIONFEE_IN' in filtered_data.columns:
                filtered_data = filtered_data[
                    (filtered_data['TUITIONFEE_IN'] >= filter_options["tuition"][0]) &
                    (filtered_data['TUITIONFEE_IN'] <= filter_options["tuition"][1]) |
                    (filtered_data['TUITIONFEE_IN'].isna())
                ]

            # Apply graduation rate filter if available
            if filter_options["grad_rate"] is not None and 'C150_4' in filtered_data.columns:
                filtered_data = filtered_data[
                    (filtered_data['C150_4'] >= filter_options["grad_rate"][0]) &
                    (filtered_data['C150_4'] <= filter_options["grad_rate"][1]) |
                    (filtered_data['C150_4'].isna())
                ]

            # Display welcome header with emoji
            st.title("🎓 Pathfinder")
            st.markdown("""
            Welcome to Pathfinder! This tool helps students explore, compare, and shortlist universities
            based on various factors like location, cost, selectivity, and outcomes.
            """)

            # Display main tabs with emojis
            tabs = st.tabs(["🔍 Explore Universities", "🎯 Find My Fit", "⚖️ Compare Universities", "📋 My Shortlist"])

            # Explore Universities Tab
            with tabs[0]:
                display_main_content(
                    filtered_data,
                    data,
                    historical_data,
                    fos_data,
                    ranking_data
                )

            # Find My Fit Tab
            with tabs[1]:
                display_find_my_fit(
                    data,
                    historical_data,
                    fos_data,
                    ranking_data
                )

            # Compare Universities Tab
            with tabs[2]:
                display_comparison_section(
                    st.session_state.selected_universities,
                    data,
                    historical_data,
                    fos_data,
                    ranking_data
                )

            # My Shortlist Tab
            with tabs[3]:
                display_shortlist(
                    data,
                    historical_data,
                    fos_data,
                    ranking_data
                )
    else:
        st.warning("Could not load university data.")

if __name__ == "__main__":
    main()
