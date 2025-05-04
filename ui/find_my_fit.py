"""
Find My Fit feature for the University Scout application.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from utils import (
    get_download_link, add_to_shortlist, remove_from_shortlist,
    toggle_university_selection, set_selected_university
)

def display_find_my_fit(data, historical_data, fos_data, ranking_data):
    """
    Displays the Find My Fit feature to help students find universities that match their profile.

    Args:
        data: DataFrame containing institution data
        historical_data: DataFrame containing historical data
        fos_data: DataFrame containing field of study data
        ranking_data: DataFrame containing ranking data

    Returns:
        None: Displays content directly using streamlit
    """
    st.header("🎯 Find My Fit")
    st.markdown("""
    Enter your academic profile and preferences to find universities that might be a good match for you.
    This tool will suggest universities where you have a good chance of admission and that match your preferences.
    """)

    # Create columns for input sections
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📚 Your Academic Profile")

        # Test Scores
        test_score_type = st.radio("Test Score Type", ["SAT", "ACT", "None"])

        if test_score_type == "SAT":
            sat_score = st.slider("Your SAT Score", 400, 1600, 1000, 10)
            # Convert to ACT equivalent for comparison
            act_score = None
        elif test_score_type == "ACT":
            act_score = st.slider("Your ACT Score", 1, 36, 20, 1)
            # Convert to SAT equivalent for comparison
            sat_score = None
        else:
            sat_score = None
            act_score = None

        # GPA
        gpa_scale = st.radio("GPA Scale", ["4.0", "5.0", "100"])
        if gpa_scale == "4.0":
            gpa = st.slider("Your GPA (4.0 scale)", 0.0, 4.0, 3.0, 0.1)
            # Convert to standard 4.0 scale for comparison
            gpa_4_scale = gpa
        elif gpa_scale == "5.0":
            gpa = st.slider("Your GPA (5.0 scale)", 0.0, 5.0, 3.5, 0.1)
            # Convert to standard 4.0 scale for comparison
            gpa_4_scale = gpa * 4.0 / 5.0
        else:
            gpa = st.slider("Your GPA (100 scale)", 0.0, 100.0, 85.0, 1.0)
            # Convert to standard 4.0 scale for comparison
            gpa_4_scale = gpa * 4.0 / 100.0

    with col2:
        st.subheader("🔍 Your Preferences")

        # Location Preference
        location_pref = st.multiselect(
            "Preferred States/Regions",
            sorted(data['STATE_NAME'].dropna().unique()),
            []
        )

        # Institution Type Preference
        institution_type = st.multiselect(
            "Institution Type",
            sorted(data['CONTROL_TYPE'].dropna().unique()),
            []
        )

        # Major/Field of Study
        if not fos_data.empty:
            # Get unique fields of study
            unique_fields = fos_data['CIPDESC'].dropna().unique()
            major_interest = st.selectbox("Field of Study Interest", ["Any"] + sorted(unique_fields))
        else:
            major_interest = "Any"

        # Cost Considerations
        max_tuition = st.slider(
            "Maximum Annual Tuition ($)",
            0,
            100000,
            50000,
            1000
        )

    # Match Criteria
    st.subheader("🎯 Match Criteria")

    # Selectivity preference
    selectivity_pref = st.select_slider(
        "University Selectivity",
        options=["Safety Schools", "Target Schools", "Reach Schools", "All"],
        value="All"
    )

    # Calculate match score and find matching universities
    if st.button("🔍 Find My Matches"):
        with st.spinner("Finding your matches..."):
            # Filter by location if specified
            if location_pref:
                # Convert full state names back to abbreviations for filtering
                state_abbrs = []
                for state_name in location_pref:
                    matching_rows = data[data['STATE_NAME'] == state_name]
                    if not matching_rows.empty:
                        state_abbrs.append(matching_rows['STABBR'].iloc[0])

                filtered_data = data[data['STABBR'].isin(state_abbrs)]
            else:
                filtered_data = data.copy()

            # Filter by institution type if specified
            if institution_type:
                filtered_data = filtered_data[filtered_data['CONTROL_TYPE'].isin(institution_type)]

            # Filter by tuition
            if 'TUITIONFEE_IN' in filtered_data.columns:
                filtered_data = filtered_data[
                    (filtered_data['TUITIONFEE_IN'] <= max_tuition) |
                    (filtered_data['TUITIONFEE_IN'].isna())
                ]

            # Calculate match scores based on test scores and admission rates
            filtered_data['Match_Score'] = 0

            # Test score match
            if test_score_type == "SAT" and sat_score is not None and 'SAT_AVG' in filtered_data.columns:
                # Higher score = better match if your score is above average
                # Lower score = worse match if your score is below average
                filtered_data['Score_Diff'] = sat_score - filtered_data['SAT_AVG']
                filtered_data['Score_Match'] = filtered_data['Score_Diff'].apply(
                    lambda x: min(100, max(0, 50 + (x / 20))) if pd.notna(x) else 50
                )
                filtered_data['Match_Score'] += filtered_data['Score_Match']
            elif test_score_type == "ACT" and act_score is not None and 'ACTCMMID' in filtered_data.columns:
                filtered_data['Score_Diff'] = act_score - filtered_data['ACTCMMID']
                filtered_data['Score_Match'] = filtered_data['Score_Diff'].apply(
                    lambda x: min(100, max(0, 50 + (x / 2))) if pd.notna(x) else 50
                )
                filtered_data['Match_Score'] += filtered_data['Score_Match']

            # Admission rate match (higher admission rate = better safety school)
            if 'ADM_RATE' in filtered_data.columns:
                if selectivity_pref == "Safety Schools":
                    # For safety schools, higher admission rate is better
                    filtered_data['Adm_Match'] = filtered_data['ADM_RATE'].apply(
                        lambda x: min(100, max(0, x * 100)) if pd.notna(x) else 50
                    )
                elif selectivity_pref == "Target Schools":
                    # For target schools, admission rate around 30-50% is ideal
                    filtered_data['Adm_Match'] = filtered_data['ADM_RATE'].apply(
                        lambda x: min(100, max(0, 100 - abs(0.4 - x) * 200)) if pd.notna(x) else 50
                    )
                elif selectivity_pref == "Reach Schools":
                    # For reach schools, lower admission rate is better
                    filtered_data['Adm_Match'] = filtered_data['ADM_RATE'].apply(
                        lambda x: min(100, max(0, 100 - x * 100)) if pd.notna(x) else 50
                    )
                else:  # All
                    filtered_data['Adm_Match'] = 50

                filtered_data['Match_Score'] += filtered_data['Adm_Match']

            # Major/Field of Study match
            if major_interest != "Any" and not fos_data.empty:
                # Find universities that offer the selected major
                major_unis = fos_data[fos_data['CIPDESC'] == major_interest]['UNITID'].unique()
                filtered_data['Major_Match'] = filtered_data['UNITID'].apply(
                    lambda x: 100 if x in major_unis else 0
                )
                filtered_data['Match_Score'] += filtered_data['Major_Match']

            # Normalize match score
            filtered_data['Match_Score'] = filtered_data['Match_Score'] / 3  # Divide by number of criteria

            # Sort by match score and get top matches
            top_matches = filtered_data.sort_values('Match_Score', ascending=False).head(20)

            if not top_matches.empty:
                st.success(f"Found {len(top_matches)} universities that match your criteria!")

                # Display matches with match score
                st.subheader("🏆 Your Top Matches")

                # Add match category based on score
                top_matches['Match_Category'] = top_matches['Match_Score'].apply(
                    lambda x: "Excellent Match" if x >= 80 else
                             ("Good Match" if x >= 60 else
                             ("Fair Match" if x >= 40 else "Poor Match"))
                )

                # Add view options
                view_col1, view_col2 = st.columns([3, 1])
                with view_col1:
                    view_mode = st.radio(
                        "View Mode",
                        ["Card View", "Table View"],
                        horizontal=True,
                        key="fit_view_mode"
                    )

                with view_col2:
                    # Option to add all matches to shortlist
                    if st.button("📋 Add All Matches to Shortlist", key="add_all_matches_to_shortlist"):
                        for unitid in top_matches['UNITID']:
                            add_to_shortlist(unitid)
                        st.success("Added all matches to your shortlist!")
                        st.rerun()

                # Display matches based on view mode
                if view_mode == "Table View":
                    # Add 'Select' and 'Shortlist' columns for the data editor
                    display_df = top_matches.copy()
                    if 'Select' not in display_df.columns:
                        display_df.insert(0, 'Select', False)

                    if 'Shortlist' not in display_df.columns:
                        display_df.insert(1, 'Shortlist', display_df['UNITID'].isin(st.session_state.shortlisted_universities))

                    # Display the data editor
                    edited_df = st.data_editor(
                        display_df[['Select', 'Shortlist', 'INSTNM', 'CITY', 'STATE_NAME', 'CONTROL_TYPE', 'Match_Score', 'Match_Category']],
                        key="match_selector",
                        disabled=list(set(display_df.columns) - set(['Select', 'Shortlist'])),
                        hide_index=True,
                        column_config={
                            "Select": st.column_config.CheckboxColumn("Compare"),
                            "Shortlist": st.column_config.CheckboxColumn("Shortlist"),
                            "INSTNM": st.column_config.TextColumn("University"),
                            "CITY": st.column_config.TextColumn("City"),
                            "STATE_NAME": st.column_config.TextColumn("State"),
                            "CONTROL_TYPE": st.column_config.TextColumn("Type"),
                            "Match_Score": st.column_config.ProgressColumn(
                                "Match Score",
                                format="%.0f%%",
                                min_value=0,
                                max_value=100
                            ),
                            "Match_Category": st.column_config.TextColumn("Match Category")
                        },
                        use_container_width=True
                    )

                    # Process selections and shortlists
                    if 'UNITID' in edited_df.columns:
                        # Get selected universities based on the 'Select' column
                        selected_rows = edited_df[edited_df['Select']]
                        selected_unitids = selected_rows['UNITID'].tolist()

                        # Update selected universities in session state
                        if set(st.session_state.selected_universities) != set(selected_unitids):
                            st.session_state.selected_universities = selected_unitids

                        # Get shortlisted universities based on the 'Shortlist' column
                        shortlisted_rows = edited_df[edited_df['Shortlist']]
                        shortlisted_unitids = shortlisted_rows['UNITID'].tolist()

                        # Update shortlist in session state
                        for unitid in top_matches['UNITID']:
                            is_shortlisted = unitid in shortlisted_unitids
                            was_shortlisted = unitid in st.session_state.shortlisted_universities

                            if is_shortlisted and not was_shortlisted:
                                add_to_shortlist(unitid)
                            elif not is_shortlisted and was_shortlisted:
                                remove_from_shortlist(unitid)

                else:  # Card View
                    # Create a grid layout for cards
                    st.write("Click on a university card to see more details or take actions.")

                    # Group universities by match category for better organization
                    categories = ["Excellent Match", "Good Match", "Fair Match", "Poor Match"]
                    for category in categories:
                        category_matches = top_matches[top_matches['Match_Category'] == category]
                        if not category_matches.empty:
                            st.subheader(category)

                            # Create rows with 3 cards each
                            for i in range(0, len(category_matches), 3):
                                row_matches = category_matches.iloc[i:i+3]
                                cols = st.columns(3)

                                for j, (_, uni) in enumerate(row_matches.iterrows()):
                                    with cols[j]:
                                        # Check if this university is in the shortlist
                                        is_shortlisted = uni['UNITID'] in st.session_state.shortlisted_universities
                                        is_selected = uni['UNITID'] in st.session_state.selected_universities

                                        # Create a card with match score
                                        match_color = {
                                            "Excellent Match": "#28a745",  # Green
                                            "Good Match": "#17a2b8",       # Blue
                                            "Fair Match": "#ffc107",       # Yellow
                                            "Poor Match": "#dc3545"        # Red
                                        }.get(uni['Match_Category'], "#6c757d")

                                        st.markdown(f"""
                                        <div style="border: 2px solid {match_color}; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
                                            <h4 style="margin-top: 0;">{uni['INSTNM']}</h4>
                                            <p>{uni['CITY']}, {uni['STATE_NAME']} • {uni['CONTROL_TYPE']}</p>
                                            <div style="background-color: #f8f9fa; border-radius: 4px; padding: 0.5rem; margin-bottom: 0.5rem;">
                                                <div style="display: flex; justify-content: space-between;">
                                                    <span>Match Score:</span>
                                                    <span style="font-weight: bold;">{uni['Match_Score']:.0f}%</span>
                                                </div>
                                                <div style="background-color: #e9ecef; border-radius: 4px; height: 8px; margin-top: 0.25rem;">
                                                    <div style="background-color: {match_color}; width: {uni['Match_Score']}%; height: 100%; border-radius: 4px;"></div>
                                                </div>
                                            </div>
                                            <p style="color: {match_color}; font-weight: bold; margin-bottom: 0;">{uni['Match_Category']}</p>
                                        </div>
                                        """, unsafe_allow_html=True)

                                        # Action buttons
                                        col1, col2, col3 = st.columns(3)

                                        with col1:
                                            if st.button(f"View Details", key=f"fit_view_{uni['UNITID']}"):
                                                set_selected_university(uni['UNITID'])
                                                st.rerun()

                                        with col2:
                                            button_label = "Remove" if is_selected else "Compare"
                                            if st.button(button_label, key=f"fit_compare_{uni['UNITID']}"):
                                                toggle_university_selection(uni['UNITID'])
                                                st.rerun()

                                        with col3:
                                            button_label = "Remove" if is_shortlisted else "Shortlist"
                                            if st.button(button_label, key=f"fit_shortlist_{uni['UNITID']}"):
                                                if is_shortlisted:
                                                    remove_from_shortlist(uni['UNITID'])
                                                else:
                                                    add_to_shortlist(uni['UNITID'])
                                                st.rerun()

                # Download option for matches
                st.markdown(
                    get_download_link(
                        top_matches,
                        f"my_university_matches_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        "📥 Download My Matches"
                    ),
                    unsafe_allow_html=True
                )
            else:
                st.warning("No universities match your criteria. Try adjusting your preferences.")
