"""
Find My Fit feature for Pathfinder application.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from utils import (
    get_download_link, add_to_shortlist, remove_from_shortlist,
    toggle_university_selection, set_selected_university
)

def display_find_my_fit(data, historical_data, fos_data):
    """
    Displays the Find My Fit feature to help students find universities that match their profile.
    """
    st.header("🎯 Find My Fit")

    # Create a more concise introduction
    st.markdown("""
    <div style="padding: 15px; border-radius: 10px; margin-bottom: 20px;">
        <p style="margin: 0;">Enter your academic information and preferences to find universities that match your profile.</p>
    </div>
    """
    , unsafe_allow_html=True)

    # Check if we're returning from details view to restore form data
    if st.session_state.coming_from_find_my_fit:
        form_data = st.session_state.find_my_fit_form_data
        st.session_state.coming_from_find_my_fit = False
    else:
        form_data = {}

    # Create a streamlined form layout
    st.markdown("""
    <div style="padding: 10px; border-radius: 3px; margin-bottom: 15px; background-color: #f8f9fa;">
        <h4 style="margin: 0;">Academic Information</h4>
    </div>
    """, unsafe_allow_html=True)

    # Academic Information Section
    col1, col2 = st.columns(2)

    with col1:
        # Test Scores
        test_score_type = st.radio(
            "Test Score Type",
            ["SAT", "ACT", "None"],
            index=form_data.get("test_score_type_index", 0)
        )

        # Store the selection in session state
        st.session_state.find_my_fit_form_data["test_score_type_index"] = ["SAT", "ACT", "None"].index(test_score_type)

        if test_score_type == "SAT":
            sat_score = st.slider(
                "Your SAT Score",
                400, 1600,
                form_data.get("sat_score", 1000),
                10
            )
            # Store the value in session state
            st.session_state.find_my_fit_form_data["sat_score"] = sat_score
            # Convert to ACT equivalent for comparison
            act_score = None

        elif test_score_type == "ACT":
            act_score = st.slider(
                "Your ACT Score",
                1, 36,
                form_data.get("act_score", 20),
                1
            )
            # Store the value in session state
            st.session_state.find_my_fit_form_data["act_score"] = act_score
            # Convert to SAT equivalent for comparison
            sat_score = None

        else:
            sat_score = None
            act_score = None

    with col2:
        # GPA
        gpa_scale = st.radio(
            "GPA Scale",
            ["4.0", "5.0", "100"],
            index=form_data.get("gpa_scale_index", 0)
        )
        # Store the selection in session state
        st.session_state.find_my_fit_form_data["gpa_scale_index"] = ["4.0", "5.0", "100"].index(gpa_scale)

        if gpa_scale == "4.0":
            gpa = st.slider(
                "Your GPA (4.0 scale)",
                0.0, 4.0,
                form_data.get("gpa_4_0", 3.0),
                0.1
            )
            # Store the value in session state
            st.session_state.find_my_fit_form_data["gpa_4_0"] = gpa
            # Convert to standard 4.0 scale for comparison
            gpa_4_scale = gpa

        elif gpa_scale == "5.0":
            gpa = st.slider(
                "Your GPA (5.0 scale)",
                0.0, 5.0,
                form_data.get("gpa_5_0", 3.5),
                0.1
            )
            # Store the value in session state
            st.session_state.find_my_fit_form_data["gpa_5_0"] = gpa
            # Convert to standard 4.0 scale for comparison
            gpa_4_scale = gpa * 4.0 / 5.0

        else:
            gpa = st.slider(
                "Your GPA (100 scale)",
                0.0, 100.0,
                form_data.get("gpa_100", 85.0),
                1.0
            )
            # Store the value in session state
            st.session_state.find_my_fit_form_data["gpa_100"] = gpa
            # Convert to standard 4.0 scale for comparison
            gpa_4_scale = gpa * 4.0 / 100.0

    # Preferences Section
    st.markdown("""
    <div style="padding: 10px; border-radius: 3px; margin: 20px 0 15px 0; background-color: #f8f9fa;">
        <h4 style="margin: 0;">University Preferences</h4>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        # Location Preference
        location_pref = st.multiselect(
            "Preferred States/Regions",
            sorted(data['STATE_NAME'].dropna().unique()),
            form_data.get("location_pref", []),
            key="find_my_fit_location_pref"
        )
        # Store the selection in session state
        st.session_state.find_my_fit_form_data["location_pref"] = location_pref

    with col2:
        # Institution Type Preference - Default to all types
        control_types = sorted(data['CONTROL_TYPE'].dropna().unique())
        default_institution_types = form_data.get("institution_type", control_types)
        institution_type = st.multiselect(
            "Institution Type",
            control_types,
            default=default_institution_types,
            key="find_my_fit_institution_type"
        )
        # Store the selection in session state
        st.session_state.find_my_fit_form_data["institution_type"] = institution_type

    with col3:
        # Major/Field of Study
        if not fos_data.empty:
            # Get unique fields of study
            unique_fields = fos_data['CIPDESC'].dropna().unique()
            major_options = ["Any"] + sorted(unique_fields)
            default_major_index = major_options.index(form_data.get("major_interest", "Any")) if form_data.get("major_interest", "Any") in major_options else 0
            major_interest = st.selectbox(
                "Field of Study Interest",
                major_options,
                index=default_major_index
            )
        else:
            major_interest = "Any"
        # Store the selection in session state
        st.session_state.find_my_fit_form_data["major_interest"] = major_interest

    # Financial and Selectivity Section
    st.markdown("""
    <div style="padding: 10px; border-radius: 3px; margin: 20px 0 15px 0; background-color: #f8f9fa;">
        <h4 style="margin: 0;">Financial & Selectivity Preferences</h4>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        # Financial Considerations
        # Family Income
        income_options = ["$0-$30,000", "$30,001-$48,000", "$48,001-$75,000", "$75,001-$110,000", "$110,001+"]
        default_income_index = income_options.index(form_data.get("family_income", "$48,001-$75,000")) if form_data.get("family_income", "$48,001-$75,000") in income_options else 2
        family_income = st.select_slider(
            "Family Income",
            options=income_options,
            value=income_options[default_income_index]
        )
        # Store the selection in session state
        st.session_state.find_my_fit_form_data["family_income"] = family_income

        # Maximum Net Price
        max_net_price = st.slider(
            "Maximum Net Price ($)",
            0,
            50000,
            form_data.get("max_net_price", 25000),
            1000
        )
        # Store the selection in session state
        st.session_state.find_my_fit_form_data["max_net_price"] = max_net_price

        # Test Score Policy Preference
        st.subheader("📝 Test Score Policy")

        test_policy_options = ["Any", "Test Optional/Flexible", "Test Required"]
        default_test_policy = form_data.get("test_policy_pref", "Any")

        # Use help widget for test policy explanation
        test_policy_pref = st.radio(
            "Test Score Policy Preference",
            options=test_policy_options,
            index=test_policy_options.index(default_test_policy) if default_test_policy in test_policy_options else 0,
            horizontal=True,
            key="test_policy_pref_radio",
            help="""
            **Test Optional/Flexible**: Schools where test scores are not required or are considered but not required.
            **Test Required**: Schools where test scores are required for admission.
            **Any**: Show all schools regardless of test policy.
            """
        )

        # Store the selection in session state
        st.session_state.find_my_fit_form_data["test_policy_pref"] = test_policy_pref

    with col2:
        # Selectivity preference with help widget
        selectivity_options = ["Safety Schools", "Target Schools", "Reach Schools", "All"]
        default_selectivity = form_data.get("selectivity_pref", "All")
        selectivity_pref = st.select_slider(
            "University Selectivity",
            options=selectivity_options,
            value=default_selectivity if default_selectivity in selectivity_options else "All",
            help="""
            **Safety Schools**: Universities where you have a high chance of admission (typically >70%).
            **Target Schools**: Universities where you have a moderate chance of admission (typically 30-70%).
            **Reach Schools**: Universities where you have a lower chance of admission (typically <30%).
            **All**: Show universities regardless of selectivity level.
            """
        )
        # Store the selection in session state
        st.session_state.find_my_fit_form_data["selectivity_pref"] = selectivity_pref

    # Add a prominent search button or display results
    st.markdown("<hr style='margin: 20px 0;'>", unsafe_allow_html=True)

    # Check if we already have results to display
    if st.session_state.has_find_my_fit_results and st.session_state.find_my_fit_results is not None:
        # Display a button to clear results and search again
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1:
            if st.button("🔄 New Search", key="new_search_button", use_container_width=True):
                st.session_state.has_find_my_fit_results = False
                st.session_state.find_my_fit_results = None
                st.rerun()

        # Display the stored results
        top_matches = st.session_state.find_my_fit_results

        # Display a simple header for results

        # Add match category based on score - using more neutral language
        if 'Match_Category' not in top_matches.columns:
            top_matches['Match_Category'] = top_matches['Match_Score'].apply(
                lambda x: "Strong Match" if x >= 80 else
                         ("Good Match" if x >= 60 else
                         ("Fair Match" if x >= 40 else "Potential Match"))
            )

        # Display the results (code continues below)

    # Calculate match score and find matching universities
    else:
        # Create a centered, prominent search button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔍 Find My Matches", key="find_matches_button", use_container_width=True, type="primary"):
                # Set the submitted flag to true
                st.session_state.find_my_fit_submitted = True

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

                    # Filter by institution type if specified and not all types are selected
                    all_types = sorted(data['CONTROL_TYPE'].dropna().unique())
                    if institution_type and set(institution_type) != set(all_types):
                        filtered_data = filtered_data[filtered_data['CONTROL_TYPE'].isin(institution_type)]

                    # Filter by test score policy if specified
                    if test_policy_pref != "Any" and 'ADMCON7' in filtered_data.columns:
                        if test_policy_pref == "Test Required":
                            # ADMCON7 = 1 means test scores are required
                            filtered_data = filtered_data[filtered_data['ADMCON7'] == 1]
                        elif test_policy_pref == "Test Optional/Flexible":
                            # ADMCON7 = 2 (recommended), 3 (neither required nor recommended), or 5 (considered but not required)
                            filtered_data = filtered_data[filtered_data['ADMCON7'].isin([2, 3, 5])]

                    # Filter by net price based on family income bracket
                    # Map the family income selection to the corresponding net price column prefixes
                    income_bracket_map = {
                        "$0-$30,000": "NPT41",
                        "$30,001-$48,000": "NPT42",
                        "$48,001-$75,000": "NPT43",
                        "$75,001-$110,000": "NPT44",
                        "$110,001+": "NPT45"
                    }

                    # Get the appropriate net price column prefix based on selected income bracket
                    net_price_prefix = income_bracket_map.get(family_income, "NPT43")  # Default to middle bracket

                    # Filter by net price for both public and private institutions
                    public_col = f"{net_price_prefix}_PUB"
                    private_col = f"{net_price_prefix}_PRIV"

                    # Create a mask for institutions with net price below the maximum
                    net_price_mask = (
                        ((filtered_data['CONTROL'] == 1) & (filtered_data[public_col] <= max_net_price)) |
                        ((filtered_data['CONTROL'] != 1) & (filtered_data[private_col] <= max_net_price)) |
                        (filtered_data[public_col].isna() & filtered_data[private_col].isna())  # Keep institutions with missing data
                    )

                    filtered_data = filtered_data[net_price_mask]

                    # Initialize match score components
                    filtered_data['Academic_Match'] = 50  # Default to neutral
                    filtered_data['Selectivity_Match'] = 50  # Default to neutral
                    filtered_data['Preference_Match'] = 50  # Default to neutral
                    filtered_data['Financial_Match'] = 50  # Default to neutral
                    filtered_data['Location_Match'] = 50  # Default to neutral
                    filtered_data['Major_Match'] = 50  # Default to neutral
                    filtered_data['TestPolicy_Match'] = 50  # Default to neutral

                    # Academic match based on test scores
                    if test_score_type == "SAT" and sat_score is not None and 'SAT_AVG' in filtered_data.columns:
                        # Calculate score difference and normalize to a 0-100 scale
                        filtered_data['Score_Diff'] = sat_score - filtered_data['SAT_AVG']

                        # For safety schools: higher score = better match
                        if selectivity_pref == "Safety Schools":
                            filtered_data['Academic_Match'] = filtered_data['Score_Diff'].apply(
                                lambda x: min(100, max(0, 50 + (x / 10))) if pd.notna(x) else 50
                            )
                        # For target schools: closer to average = better match
                        elif selectivity_pref == "Target Schools":
                            filtered_data['Academic_Match'] = filtered_data['Score_Diff'].apply(
                                lambda x: min(100, max(0, 100 - abs(x) / 5)) if pd.notna(x) else 50
                            )
                        # For reach schools: slightly below average = better match
                        elif selectivity_pref == "Reach Schools":
                            filtered_data['Academic_Match'] = filtered_data['Score_Diff'].apply(
                                lambda x: min(100, max(0, 100 - abs(x + 100) / 10)) if pd.notna(x) else 50
                            )
                        # For all: use a balanced approach
                        else:
                            filtered_data['Academic_Match'] = filtered_data['Score_Diff'].apply(
                                lambda x: min(100, max(0, 75 + (x / 20))) if pd.notna(x) else 50
                            )

                    elif test_score_type == "ACT" and act_score is not None and 'ACTCMMID' in filtered_data.columns:
                        # Calculate score difference and normalize to a 0-100 scale
                        filtered_data['Score_Diff'] = act_score - filtered_data['ACTCMMID']

                        # For safety schools: higher score = better match
                        if selectivity_pref == "Safety Schools":
                            filtered_data['Academic_Match'] = filtered_data['Score_Diff'].apply(
                                lambda x: min(100, max(0, 50 + (x * 10))) if pd.notna(x) else 50
                            )
                        # For target schools: closer to average = better match
                        elif selectivity_pref == "Target Schools":
                            filtered_data['Academic_Match'] = filtered_data['Score_Diff'].apply(
                                lambda x: min(100, max(0, 100 - abs(x) * 20)) if pd.notna(x) else 50
                            )
                        # For reach schools: slightly below average = better match
                        elif selectivity_pref == "Reach Schools":
                            filtered_data['Academic_Match'] = filtered_data['Score_Diff'].apply(
                                lambda x: min(100, max(0, 100 - abs(x + 2) * 20)) if pd.notna(x) else 50
                            )
                        # For all: use a balanced approach
                        else:
                            filtered_data['Academic_Match'] = filtered_data['Score_Diff'].apply(
                                lambda x: min(100, max(0, 75 + (x * 5))) if pd.notna(x) else 50
                            )

                    # Selectivity match based on admission rates
                    if 'ADM_RATE' in filtered_data.columns:
                        if selectivity_pref == "Safety Schools":
                            # For safety schools, higher admission rate is better (>50%)
                            filtered_data['Selectivity_Match'] = filtered_data['ADM_RATE'].apply(
                                lambda x: min(100, max(0, 50 + (x * 100))) if pd.notna(x) else 50
                            )
                        elif selectivity_pref == "Target Schools":
                            # For target schools, admission rate around 20-50% is ideal
                            filtered_data['Selectivity_Match'] = filtered_data['ADM_RATE'].apply(
                                lambda x: min(100, max(0, 100 - abs(0.35 - x) * 300)) if pd.notna(x) else 50
                            )
                        elif selectivity_pref == "Reach Schools":
                            # For reach schools, lower admission rate is better (<20%)
                            filtered_data['Selectivity_Match'] = filtered_data['ADM_RATE'].apply(
                                lambda x: min(100, max(0, 100 - (x * 250))) if pd.notna(x) else 50
                            )
                        else:  # All - balanced approach
                            filtered_data['Selectivity_Match'] = 75  # Neutral but slightly positive

                    # Location match
                    if location_pref:
                        filtered_data['Location_Match'] = filtered_data['STATE_NAME'].apply(
                            lambda x: 100 if x in location_pref else 0
                        )
                    else:
                        # No location preference, so all locations match equally
                        filtered_data['Location_Match'] = 75

                    # Major/Field of Study match
                    if major_interest != "Any" and not fos_data.empty:
                        # Find universities that offer the selected major
                        major_unis = fos_data[fos_data['CIPDESC'] == major_interest]['UNITID'].unique()
                        filtered_data['Major_Match'] = filtered_data['UNITID'].apply(
                            lambda x: 100 if x in major_unis else 25  # Give some points even if major doesn't match
                        )
                    else:
                        # No major preference, so all majors match equally
                        filtered_data['Major_Match'] = 75

                    # Financial match based on net price
                    # Get the appropriate net price column based on institution type and income bracket
                    is_public_mask = filtered_data['CONTROL'] == 1
                    net_price_col_pub = f"{net_price_prefix}_PUB"
                    net_price_col_priv = f"{net_price_prefix}_PRIV"

                    # Calculate financial match score
                    def calc_financial_match(row):
                        if pd.isna(row[net_price_col_pub]) and pd.isna(row[net_price_col_priv]):
                            return 50  # Neutral if no data

                        # Get the appropriate net price based on institution type
                        if row['CONTROL'] == 1 and pd.notna(row[net_price_col_pub]):  # Public
                            net_price = row[net_price_col_pub]
                        elif pd.notna(row[net_price_col_priv]):  # Private
                            net_price = row[net_price_col_priv]
                        else:
                            return 50  # Neutral if no data for this institution type

                        # Higher score for lower net price
                        if net_price <= max_net_price * 0.5:
                            return 100  # Excellent match if well under budget
                        elif net_price <= max_net_price:
                            return 75  # Good match if under budget
                        elif net_price <= max_net_price * 1.25:
                            return 50  # Neutral if slightly over budget
                        else:
                            return 25  # Poor match if well over budget

                    filtered_data['Financial_Match'] = filtered_data.apply(calc_financial_match, axis=1)

                    # Test Score Policy match
                    if 'ADMCON7' in filtered_data.columns:
                        def calc_test_policy_match(admcon_value, user_pref):
                            if pd.isna(admcon_value):
                                return 50  # Neutral if no data

                            # Convert to integer if it's not already
                            if not isinstance(admcon_value, (int, np.integer)):
                                try:
                                    admcon_value = int(admcon_value)
                                except:
                                    return 50  # Neutral if conversion fails

                            # Match based on user preference
                            if user_pref == "Test Required" and admcon_value == 1:
                                return 100  # Perfect match for required
                            elif user_pref == "Test Optional/Flexible" and admcon_value in [2, 3, 5]:
                                return 100  # Perfect match for optional/flexible
                            elif user_pref == "Any":
                                return 75  # Good match for any preference
                            else:
                                return 25  # Poor match if preferences don't align

                        filtered_data['TestPolicy_Match'] = filtered_data['ADMCON7'].apply(
                            lambda x: calc_test_policy_match(x, test_policy_pref)
                        )

                    # Calculate overall preference match (average of location, major, financial, and test policy)
                    filtered_data['Preference_Match'] = (
                        filtered_data['Location_Match'] +
                        filtered_data['Major_Match'] +
                        filtered_data['Financial_Match'] +
                        filtered_data['TestPolicy_Match']
                    ) / 4

                    # Calculate overall match score with weighted components
                    # Academic and selectivity are weighted more heavily for better matching
                    filtered_data['Match_Score'] = (
                        filtered_data['Academic_Match'] * 0.35 +  # 35% weight
                        filtered_data['Selectivity_Match'] * 0.25 +  # 25% weight
                        filtered_data['Preference_Match'] * 0.4  # 40% weight
                    )

                    # Round match score for cleaner display
                    filtered_data['Match_Score'] = filtered_data['Match_Score'].round(0)

                    # Sort by match score and get top matches
                    top_matches = filtered_data.sort_values('Match_Score', ascending=False).head(30)

                    # Store the results in session state
                    st.session_state.find_my_fit_results = top_matches.copy()
                    st.session_state.has_find_my_fit_results = True

                    if not top_matches.empty:
                        st.toast(f'Found **{len(top_matches)}** matches!', icon="🎉")

                        # Force a rerun to display results in the main section
                        st.rerun()

    # If we have results to display (after the rerun), show them here
    if st.session_state.has_find_my_fit_results and st.session_state.find_my_fit_results is not None:
        # Get the stored results
        top_matches = st.session_state.find_my_fit_results

        # Display a simple header for results
        st.markdown("### University Matches", help="Top university suggestions based on your profile.")

        # Add match category based on score - using more neutral language
        if 'Match_Category' not in top_matches.columns:
            top_matches['Match_Category'] = top_matches['Match_Score'].apply(
                lambda x: "Strong Match" if x >= 80 else
                         ("Good Match" if x >= 60 else
                         ("Fair Match" if x >= 40 else "Potential Match"))
            )

        # Create a simple view options row
        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            view_mode = st.radio(
                "View Mode",
                ["Card View", "Table View"],
                index=0 if st.session_state.find_my_fit_view_mode == "Card View" else 1,
                horizontal=True,
                key="fit_view_mode",
                on_change=lambda: setattr(st.session_state, 'find_my_fit_view_mode',
                                         "Card View" if st.session_state.fit_view_mode == "Card View" else "Table View")
            )

        with col3:
            # Option to add all matches to shortlist
            if st.button("📋 Add All to Shortlist",
                        key="add_all_matches_to_shortlist",
                        type="primary",
                        use_container_width=True):
                # Count how many new universities will be added
                new_unis = [unitid for unitid in top_matches['UNITID']
                           if unitid not in st.session_state.shortlisted_universities]

                # Add all to shortlist
                for unitid in top_matches['UNITID']:
                    add_to_shortlist(unitid)
                    # Also add to selected universities for comparison
                    if unitid not in st.session_state.selected_universities:
                        st.session_state.selected_universities.append(unitid)

                # Show toast notification
                if new_unis:
                    st.toast(f"Added {len(new_unis)} universities to your shortlist", icon="✅")
                else:
                    st.toast("All universities were already in your shortlist", icon="ℹ️")

        # Display matches based on view mode
        if view_mode == "Table View":
            # Add 'Shortlist' column for the data editor
            display_df = top_matches.copy()
            if 'Shortlist' not in display_df.columns:
                display_df.insert(0, 'Shortlist', display_df['UNITID'].isin(st.session_state.shortlisted_universities))

            # Display the data editor
            edited_df = st.data_editor(
                display_df[['Shortlist', 'INSTNM', 'CITY', 'STATE_NAME', 'CONTROL_TYPE', 'Match_Score', 'Match_Category']],
                key="match_selector",
                disabled=list(set(display_df.columns) - set(['Shortlist'])),
                hide_index=True,
                column_config={
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

            # Process shortlists
            if 'UNITID' in edited_df.columns:
                # Get shortlisted universities based on the 'Shortlist' column
                shortlisted_rows = edited_df[edited_df['Shortlist']]
                shortlisted_unitids = shortlisted_rows['UNITID'].tolist()

                # Update shortlist in session state and automatically select them for comparison
                for unitid in top_matches['UNITID']:
                    is_shortlisted = unitid in shortlisted_unitids
                    was_shortlisted = unitid in st.session_state.shortlisted_universities

                    if is_shortlisted and not was_shortlisted:
                        add_to_shortlist(unitid)
                        # Also add to selected universities for comparison
                        if unitid not in st.session_state.selected_universities:
                            st.session_state.selected_universities.append(unitid)
                    elif not is_shortlisted and was_shortlisted:
                        remove_from_shortlist(unitid)
                        # Also remove from selected universities
                        if unitid in st.session_state.selected_universities:
                            st.session_state.selected_universities.remove(unitid)

        else:  # Card View
            # Create a grid layout for cards with 3 columns for better use of space
            st.write("Click on a university card to see more details or take actions.")
            # Group universities by match category for better organization
            categories = ["Strong Match", "Good Match", "Fair Match", "Potential Match"]
            # Use monochromatic blue color palette - stronger/more opaque for better matches
            category_colors = {
                "Strong Match": "#0047AB",     # Strong cobalt blue
                "Good Match": "#4682B4",       # Steel blue
                "Fair Match": "#87CEEB",       # Sky blue
                "Potential Match": "#B0E0E6"   # Powder blue
            }

            # Helper function to generate match narrative
            def generate_match_narrative(uni_row, user_major_interest, user_location_pref, user_selectivity_pref, user_test_policy_pref):
                narrative_points = []
                # Academic
                if uni_row['Academic_Match'] >= 75:
                    narrative_points.append("✅ Strong academic fit.")
                elif uni_row['Academic_Match'] >= 50:
                    narrative_points.append("👍 Good academic fit.")
                else:
                    narrative_points.append("⚠️ Academics may be a stretch or mismatch.")

                # Major
                if user_major_interest != "Any":
                    if uni_row['Major_Match'] == 100:
                        narrative_points.append(f"✅ Offers field: {user_major_interest}.")
                    elif uni_row['Major_Match'] == 25:
                        narrative_points.append(f"❓ Field {user_major_interest} may not be offered or data missing.")

                # Location
                if user_location_pref:
                    if uni_row['Location_Match'] == 100:
                        narrative_points.append("✅ In preferred location(s).")
                    else:
                        narrative_points.append("⚠️ Not in preferred location(s).")

                # Financial
                if uni_row['Financial_Match'] >= 75:
                    narrative_points.append("✅ Good financial fit (net price).")
                elif uni_row['Financial_Match'] >= 50:
                    narrative_points.append("👍 Fair financial fit (net price).")
                else:
                    narrative_points.append("⚠️ Net price may be a concern.")

                # Selectivity
                if uni_row['Selectivity_Match'] >= 75:
                    narrative_points.append(f"✅ Aligns well with '{user_selectivity_pref}' preference.")
                elif uni_row['Selectivity_Match'] >= 50:
                    narrative_points.append(f"👍 Fair alignment with '{user_selectivity_pref}' preference.")
                else:
                    narrative_points.append(f"⚠️ May not align with '{user_selectivity_pref}' preference.")

                # Test Score Policy
                if user_test_policy_pref != "Any" and 'TestPolicy_Match' in uni_row and pd.notna(uni_row['TestPolicy_Match']):
                    if uni_row['TestPolicy_Match'] >= 75:
                        narrative_points.append(f"✅ Test score policy matches your preference.")
                    elif uni_row['TestPolicy_Match'] >= 50:
                        narrative_points.append(f"👍 Test score policy partially matches your preference.")
                    else:
                        narrative_points.append(f"⚠️ Test score policy may not match your preference.")

                # Add test score policy information if available
                if 'ADMCON7' in uni_row and pd.notna(uni_row['ADMCON7']):
                    try:
                        admcon_value = int(uni_row['ADMCON7'])
                        policy_map = {
                            1: "Tests required",
                            2: "Tests recommended",
                            3: "Tests neither required nor recommended",
                            4: "Test policy unknown",
                            5: "Tests considered but not required"
                        }
                        if admcon_value in policy_map:
                            narrative_points.append(f"ℹ️ {policy_map[admcon_value]}.")
                    except:
                        # If conversion fails, just continue without adding the policy info
                        pass

                if not narrative_points:
                    return "<p style='font-size: 0.85rem; color: #666; margin-top: 0.5rem;'><em>Review details for overall fit.</em></p>"

                html_points = "".join([f"<li style='font-size: 0.85rem; color: #555; margin-bottom: 0.2rem;'>{point}</li>" for point in narrative_points[:3]]) # Max 3 points
                return f"<ul style='list-style-type: none; padding-left: 0; margin-top: 0.75rem; margin-bottom: 0.5rem;'>{html_points}</ul>"

            # Create a grid layout with 3 columns
            cols = st.columns(3)

            # Process each university
            for i, (_, uni) in enumerate(top_matches.iterrows()):
                # Determine which column to use (cycle through columns)
                col_idx = i % 3

                # Check if this university is in the shortlist
                is_shortlisted = uni['UNITID'] in st.session_state.shortlisted_universities
                is_selected = uni['UNITID'] in st.session_state.selected_universities

                # Create a card with match score - using a more neutral color palette
                match_color = category_colors.get(uni['Match_Category'], "#6c757d")

                # Get match component scores
                academic_match = uni['Academic_Match'] if 'Academic_Match' in uni and pd.notna(uni['Academic_Match']) else 50
                selectivity_match = uni['Selectivity_Match'] if 'Selectivity_Match' in uni and pd.notna(uni['Selectivity_Match']) else 50
                preference_match = uni['Preference_Match'] if 'Preference_Match' in uni and pd.notna(uni['Preference_Match']) else 50

                # Simplified card without narrative text

                # Create the card with match score and progress bar

                # Instead of using HTML, use native Streamlit components
                with cols[col_idx]:
                    # Create a container with border styling
                    with st.container():
                        # Apply custom CSS for the container
                        st.markdown(f"""
                        <div style="border: 1px solid #e0e0e0; border-top: 5px solid {match_color};
                        border-radius: 8px; padding: 1rem; margin-bottom: 0.5rem;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                            <h4 style="margin-top: 0; color: #333; font-size: 1.1rem;">{uni['INSTNM']}</h4>
                            <p style="color: #666; margin-bottom: 0.5rem; font-size: 0.9rem;">
                                {uni['CITY']}, {uni['STATE_NAME']} • {uni['CONTROL_TYPE']}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)

                        # Display match score as a metric
                        st.metric(
                            label="Match Score",
                            value=f"{uni['Match_Score']:.0f}%"
                        )

                        # Display match progress bar
                        st.progress(uni['Match_Score']/100)

                        # Add a simple explanation of the match
                        match_explanation = []

                        # Academic match
                        if 'Academic_Match' in uni and pd.notna(uni['Academic_Match']):
                            if uni['Academic_Match'] >= 75:
                                match_explanation.append("✅ Strong academic fit")
                            elif uni['Academic_Match'] >= 50:
                                match_explanation.append("👍 Good academic fit")

                        # Location match
                        if 'Location_Match' in uni and pd.notna(uni['Location_Match']):
                            if uni['Location_Match'] == 100:
                                match_explanation.append("✅ Preferred location")

                        # Financial match
                        if 'Financial_Match' in uni and pd.notna(uni['Financial_Match']):
                            if uni['Financial_Match'] >= 75:
                                match_explanation.append("✅ Good financial fit")
                            elif uni['Financial_Match'] >= 50:
                                match_explanation.append("👍 Fair financial fit")

                        # Display up to 2 match reasons
                        if match_explanation:
                            with st.expander("Why this match?"):
                                for reason in match_explanation[:2]:
                                    st.markdown(reason)

                    # Add buttons in a row
                    btn1, btn2 = st.columns(2)

                    with btn1:
                        if st.button("🔍 Details", key=f"view_{uni['UNITID']}", use_container_width=True):
                            # Save the current results and form data
                            st.session_state.find_my_fit_results = top_matches.copy()
                            # Navigate to details view
                            set_selected_university(uni['UNITID'])

                    with btn2:
                        # Define helper functions for shortlist actions with toast notifications
                        def add_to_shortlist_with_toast(unitid, uni_name):
                            """Add university to shortlist with toast notification"""
                            add_to_shortlist(unitid)
                            # Also add to selected universities for comparison
                            if unitid not in st.session_state.selected_universities:
                                st.session_state.selected_universities.append(unitid)
                            # Show toast notification
                            st.toast(f"Added {uni_name} to your shortlist", icon="✅")

                        def remove_from_shortlist_with_toast(unitid, uni_name):
                            """Remove university from shortlist with toast notification"""
                            remove_from_shortlist(unitid)
                            # Also remove from selected universities
                            if unitid in st.session_state.selected_universities:
                                st.session_state.selected_universities.remove(unitid)
                            # Show toast notification
                            st.toast(f"Removed {uni_name} from your shortlist", icon="🗑️")

                        shortlist_label = "❌ Remove" if is_shortlisted else "📋 Add"
                        if st.button(shortlist_label, key=f"shortlist_{uni['UNITID']}", use_container_width=True,
                                    on_click=lambda unitid=uni['UNITID'], uni_name=uni['INSTNM'], is_sl=is_shortlisted:
                                    remove_from_shortlist_with_toast(unitid, uni_name) if is_sl else
                                    add_to_shortlist_with_toast(unitid, uni_name)):
                            pass

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
        # Only show toast notification if the form has been submitted
        if st.session_state.get('find_my_fit_form_submitted', False) and st.session_state.find_my_fit_results is None:
            st.toast("No universities match your criteria. Try adjusting your preferences.", icon="⚠️")


        st.info("This tool only measures and returns matches based purely on academic and preferential criteria. It does not consider extracurricular activies, campus culture, or other non-academic factors. We are working on adding more features to the tool :)")

