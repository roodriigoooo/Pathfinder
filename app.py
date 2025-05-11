"""
Pathfinder - A tool to help students explore and shortlist universities.
"""

import streamlit as st

# Import configuration
from config import COLUMNS_TO_LOAD, NUMERIC_COLUMNS

# Import data loading functions
from data_loader import (
    load_institution_data,
    load_historical_data,
    load_field_of_study_data,
)

# Import utility functions
from utils import (
    initialize_session_state,
    apply_custom_css
)

# Import UI components
from ui.sidebar import display_sidebar_filters
from ui.explore import display_main_content
from ui.details import display_university_details
from ui.find_my_fit import display_find_my_fit
from ui.shortlist_compare import display_unified_shortlist_compare


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

    # Load the data (using full dataset)
    data = load_institution_data(COLUMNS_TO_LOAD, NUMERIC_COLUMNS)
    historical_data = load_historical_data()
    fos_data = load_field_of_study_data()

    if not data.empty:
        # Check if we need to show university details
        if st.session_state.active_tab == "Details" and st.session_state.selected_university_id is not None:
            # Add a back button to return to the previous tab
            col1, col2 = st.columns([1, 11])
            with col1:
                if st.button("← Back"):
                    # If coming from Find My Fit, go back to that tab
                    if st.session_state.coming_from_find_my_fit:
                        st.session_state.active_tab = "Find My Fit"
                        st.session_state.coming_from_find_my_fit = False
                    else:
                        st.session_state.active_tab = "Explore"
                    st.session_state.selected_university_id = None
                    st.rerun()

            # Display university details
            display_university_details(
                st.session_state.selected_university_id,
                data,
                historical_data,
                fos_data
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

            # Apply test score policy filter if available
            if filter_options["test_policy"] != "Any" and 'ADMCON7' in filtered_data.columns:
                # Convert the selected policy to integer for comparison
                selected_policy = int(filter_options["test_policy"])
                filtered_data = filtered_data[
                    (filtered_data['ADMCON7'] == selected_policy) |
                    (filtered_data['ADMCON7'].isna())  # Include universities with missing data
                ]

            # Display welcome header with emoji
            st.title("🎓 Pathfinder")
            st.markdown("""
            Welcome to Pathfinder! This tool helps students explore, compare, and shortlist universities
            based on various factors like location, cost, selectivity, and outcomes.
            """)

            # Display main tabs with emojis
            tab_names = ["🔍 Explore Universities", "🎯 Find My Fit", "📋 My Universities"]

            # Map tab names to their index for selection
            tab_index_map = {
                "Explore": 0,
                "Find My Fit": 1,
                "Shortlist": 2,
                "Compare": 2  # Map Compare to the same tab as Shortlist
            }

            # Get the current active tab index (default to Explore if not found)
            active_tab_name = st.session_state.active_tab
            if active_tab_name not in ["Details", "Explore", "Find My Fit", "Compare", "Shortlist"]:
                active_tab_name = "Explore"

            # If coming from Find My Fit and returning to tabs, select the Find My Fit tab
            if st.session_state.coming_from_find_my_fit:
                active_tab_name = "Find My Fit"
                st.session_state.coming_from_find_my_fit = False

            active_tab_index = tab_index_map.get(active_tab_name, 0)

            # Create the tabs with the active tab selected
            tabs = st.tabs(tab_names)

            # Explore Universities Tab
            with tabs[0]:
                display_main_content(
                    filtered_data,
                    data,
                    historical_data,
                    fos_data
                )

            # Find My Fit Tab
            with tabs[1]:
                display_find_my_fit(
                    data,
                    historical_data,
                    fos_data
                )

            # My Universities Tab (Unified Shortlist & Compare)
            with tabs[2]:
                display_unified_shortlist_compare(
                    data,
                    historical_data,
                    fos_data
                )
    else:
        st.warning("Could not load university data.")

if __name__ == "__main__":
    main()
