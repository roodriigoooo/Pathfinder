"""
Unified shortlist and compare functionality for Pathfinder.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from utils import (
    get_download_link, add_to_shortlist, remove_from_shortlist,
    set_selected_university, toggle_university_selection
)
from ui import visualizations as viz

def display_unified_shortlist_compare(data, historical_data, fos_data):
    """
    Displays a unified interface for shortlisted universities and comparison.
    """
    # Create tabs within the unified interface
    inner_tabs = st.tabs(["📋 My Universities", "📊 Compare Selected"])

    # My Universities Tab (Shortlist)
    with inner_tabs[0]:
        display_shortlist_section(data, historical_data, fos_data)

    # Compare Selected Tab
    with inner_tabs[1]:
        display_comparison_section(st.session_state.selected_universities, data, historical_data, fos_data)

def display_shortlist_section(data, historical_data, fos_data):
    """
    Displays the shortlisted universities with options to view details or compare.
    """
    col1, col2, col3 = st.columns([4,1,1])
    with col1:
        st.subheader("📋 My Universities")
    with col2:
        if st.button("🗑️ Clear Shortlist", key="clear_shortlist_button_unified"):
            st.session_state.shortlisted_universities = []
            st.session_state.selected_universities = []
            st.toast(f'Cleared all universities from your shortlist', icon="🗑️")
            st.rerun()
    #check if there are any shortlisted universities
    if not st.session_state.shortlisted_universities:
        st.info("You haven't shortlisted any universities yet. Explore universities and add them to your shortlist!")
        return
    #get data for shortlisted universities
    shortlist_df = data[data['UNITID'].isin(st.session_state.shortlisted_universities)].copy()
    with col3:
        st.markdown(
            get_download_link(
                shortlist_df,
                f"shortlisted_universities_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "📥 Download Shortlist"
            ),
            unsafe_allow_html=True
        )

    # Display university cards with action buttons first
    st.markdown("""
    <div style="margin: 20px 0 15px 0;">
        <h3 style="margin: 0; font-size: 1.2rem; color: #1e88e5;">🏫 University Actions</h3>
        <p style="margin: 5px 0 0 0; font-size: 0.9rem; color: #666;">
            Click "View Details" to explore comprehensive information about each university.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Create a grid layout for university cards
    cols = st.columns(3)
    for i, (_, uni) in enumerate(shortlist_df.iterrows()):
        col_idx = i % 3
        with cols[col_idx]:
            # Create a card with a colored border based on institution type
            if 'CONTROL_TYPE' in uni:
                if uni['CONTROL_TYPE'] == 'Public':
                    border_color = "#4682B4"  # Steel blue for public
                    badge_color = "#4682B4"
                    badge_text = "Public"
                elif uni['CONTROL_TYPE'] == 'Private nonprofit':
                    border_color = "#0047AB"  # Cobalt blue for private nonprofit
                    badge_color = "#0047AB"
                    badge_text = "Private Nonprofit"
                else:
                    border_color = "#87CEEB"  # Sky blue for others
                    badge_color = "#87CEEB"
                    badge_text = "For-Profit"
            else:
                border_color = "#B0E0E6"  # Default powder blue
                badge_color = "#B0E0E6"
                badge_text = "Unknown Type"

            # Create a styled card with university name and location
            location_text = f"{uni['CITY']}, {uni['STABBR']}" if 'CITY' in uni and 'STABBR' in uni else ""

            # Add admission rate if available
            adm_rate_text = ""
            if 'ADM_RATE' in uni and pd.notna(uni['ADM_RATE']):
                adm_rate = uni['ADM_RATE'] * 100  # Convert to percentage
                adm_rate_text = f"<span style='background-color: #f0f0f0; padding: 2px 6px; border-radius: 10px; font-size: 0.75rem; margin-left: 5px;'>{adm_rate:.1f}% admission</span>"

            # Add SAT score if available
            sat_text = ""
            if 'SAT_AVG' in uni and pd.notna(uni['SAT_AVG']):
                sat_score = int(uni['SAT_AVG'])
                sat_text = f"<span style='background-color: #f0f0f0; padding: 2px 6px; border-radius: 10px; font-size: 0.75rem; margin-left: 5px;'>SAT: {sat_score}</span>"

            st.markdown(f"""
            <div style="border: 1px solid #e0e0e0; border-left: 5px solid {border_color}; border-radius: 5px; padding: 15px; margin-bottom: 20px; background-color: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
                    <h4 style="margin: 0; color: #333; font-size: 1.1rem;">{uni['INSTNM']}</h4>
                    <span style="background-color: {badge_color}; color: white; padding: 2px 6px; border-radius: 10px; font-size: 0.7rem;">{badge_text}</span>
                </div>
                <p style="margin: 5px 0; color: #666; font-size: 0.9rem;">{location_text}</p>
                <div style="margin: 8px 0;">
                    {adm_rate_text} {sat_text}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Add action buttons with enhanced styling
            col1, col2 = st.columns(2)
            with col1:
                # Enhanced View Details button
                if st.button("🔍 View Details", key=f"shortlist_view_{uni['UNITID']}_{i}",
                           use_container_width=True, type="primary"):
                    set_selected_university(uni['UNITID'])
                    st.session_state.active_tab = "Details"
                    st.rerun()
            with col2:
                # Define a function to remove with toast notification
                def remove_with_toast(unitid, uni_name):
                    # Remove from shortlist
                    remove_from_shortlist(unitid)
                    # Also remove from selected universities if present
                    if unitid in st.session_state.selected_universities:
                        st.session_state.selected_universities.remove(unitid)
                    # Show toast notification
                    st.toast(f"Removed {uni_name} from your shortlist", icon="🗑️")
                    st.rerun()

                # Add a remove button
                if st.button("❌ Remove", key=f"shortlist_remove_{uni['UNITID']}_{i}",
                           use_container_width=True,
                           on_click=lambda unitid=uni['UNITID'], uni_name=uni['INSTNM']:
                           remove_with_toast(unitid, uni_name)):
                    pass

    # Add a divider
    st.markdown("<hr style='margin: 30px 0; border: none; height: 1px; background-color: #e0e0e0;'>", unsafe_allow_html=True)

    # Now display the comparison table section
    st.markdown("""
    <div style="margin-bottom: 15px;">
        <h3 style="margin: 0; font-size: 1.2rem; color: #1e88e5;">📊 Compare Universities</h3>
        <p style="margin: 5px 0 0 0; font-size: 0.9rem; color: #666;">
            Select universities to compare their key metrics side by side.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Add a 'Select' column for comparison
    shortlist_df.insert(0, 'Select', shortlist_df['UNITID'].isin(st.session_state.selected_universities))

    # Add help text for the comparison functionality
    st.markdown("""
    <div style="background-color: #f8f9fa; border-left: 4px solid #1e88e5; padding: 10px; margin-bottom: 15px; border-radius: 4px;">
        <p style="margin: 0; font-size: 0.9rem;">
            <strong>How to compare:</strong> Check the <strong>Compare</strong> box next to universities you want to compare.
            Click <strong>Apply Changes</strong> to update your selection and view the comparison in the <strong>Compare Selected</strong> tab.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Create optimized column configuration
    column_config = {
        "Select": st.column_config.CheckboxColumn("Compare", help="Select universities to compare"),
        "INSTNM": st.column_config.TextColumn("Institution Name"),
        "CITY": st.column_config.TextColumn("City"),
        "STABBR": st.column_config.TextColumn("State"),
        "CONTROL_TYPE": st.column_config.TextColumn("Type")
    }

    # Add numeric columns with formatting if they exist
    if 'ADM_RATE' in shortlist_df.columns:
        # Convert admission rate from decimal to percentage for display
        shortlist_df['ADM_RATE'] = shortlist_df['ADM_RATE'] * 100
        column_config["ADM_RATE"] = st.column_config.NumberColumn("Admission Rate", format="%.1f%%")
    if 'SAT_AVG' in shortlist_df.columns:
        column_config["SAT_AVG"] = st.column_config.NumberColumn("Avg SAT")
    if 'TUITIONFEE_IN' in shortlist_df.columns:
        column_config["TUITIONFEE_IN"] = st.column_config.NumberColumn("In-State Tuition", format="$%d")
    if 'C150_4' in shortlist_df.columns:
        # Convert graduation rate from decimal to percentage for display
        shortlist_df['C150_4'] = shortlist_df['C150_4'] * 100
        column_config["C150_4"] = st.column_config.NumberColumn("Graduation Rate", format="%.1f%%")
    if 'ADMCON7' in shortlist_df.columns:
        # Map ADMCON7 values to readable labels
        policy_map = {
            1: "Required",
            2: "Recommended",
            3: "Neither Required/Recommended",
            4: "Unknown",
            5: "Considered but not Required"
        }
        # Create a new column with the mapped values
        shortlist_df['Test_Policy'] = shortlist_df['ADMCON7'].apply(
            lambda x: policy_map.get(int(x), "Unknown") if pd.notna(x) else "Unknown"
        )
        # Add the column to the display and remove the raw ADMCON7 column
        column_config["Test_Policy"] = st.column_config.TextColumn("Test Score Policy")
        shortlist_df = shortlist_df.drop(columns=['ADMCON7'])

    # Display the data editor
    edited_df = st.data_editor(
        shortlist_df,
        key="shortlist_editor",
        disabled=list(set(shortlist_df.columns) - set(['Select'])),
        hide_index=True,
        column_config=column_config,
        use_container_width=True
    )

    # Add an apply button to save changes
    col1, col2 = st.columns([4, 1])
    with col2:
        apply_changes = st.button("✅ Apply Changes", key="apply_shortlist_changes_unified")

    # Process selections when apply button is clicked
    if apply_changes and 'UNITID' in edited_df.columns:
        # Get selected universities based on the 'Select' column
        selected_unitids = edited_df.loc[edited_df['Select'], 'UNITID'].tolist()

        # Get previously selected universities
        previously_selected = set(st.session_state.selected_universities)
        newly_selected = set(selected_unitids) - previously_selected
        removed_from_selection = previously_selected - set(selected_unitids)

        # Update selected universities in session state
        st.session_state.selected_universities = selected_unitids

        # Show toast notifications for changes
        if newly_selected:
            # Show toast for newly selected universities (up to 3)
            added_names = []
            for unitid in list(newly_selected)[:3]:
                uni_name = shortlist_df.loc[shortlist_df['UNITID'] == unitid, 'INSTNM'].iloc[0]
                added_names.append(uni_name)

            if len(newly_selected) <= 3:
                for name in added_names:
                    st.toast(f"Added {name} to comparison", icon="⚖️")
            else:
                st.toast(f"Added {len(newly_selected)} universities to comparison", icon="⚖️")

        if removed_from_selection:
            # Show toast for removed universities
            if len(removed_from_selection) == 1:
                unitid = list(removed_from_selection)[0]
                uni_name = shortlist_df.loc[shortlist_df['UNITID'] == unitid, 'INSTNM'].iloc[0]
                st.toast(f"Removed {uni_name} from comparison", icon="🗑️")
            else:
                st.toast(f"Removed {len(removed_from_selection)} universities from comparison", icon="🗑️")

        # Show confirmation
        st.success(f"✅ Updated: {len(selected_unitids)} universities selected for comparison")
        st.rerun()



def display_comparison_section(selected_universities, data, historical_data, fos_data):
    """
    Displays a comparison of selected universities.
    """
    st.header("⚖️ University Comparison")

    # Check if there are any selected universities
    if not selected_universities:
        st.info("Select universities to compare by checking the 'Compare' box in the My Universities tab.")
        return

    # Get data for selected universities
    selected_df = data[data['UNITID'].isin(selected_universities)].copy()

    # Display comparison visualizations
    st.subheader(f"Comparing {len(selected_df)} Universities")

    # Create tabs for different comparison categories
    comp_tabs = st.tabs(["📊 Overview", "💰 Cost", "🎓 Academics", "📈 Outcomes"])

    # Overview Tab
    with comp_tabs[0]:
        # Display a summary table
        st.markdown("### University Overview")

        # Create a transposed view for easier comparison
        overview_df = selected_df[['INSTNM', 'CITY', 'STABBR', 'CONTROL_TYPE', 'UGDS']].copy()
        overview_df = overview_df.set_index('INSTNM').T

        # Format the enrollment numbers
        if 'UGDS' in overview_df.index:
            overview_df.loc['UGDS'] = overview_df.loc['UGDS'].apply(lambda x: f"{int(x):,}" if pd.notna(x) else "N/A")

        # Rename the index
        overview_df = overview_df.rename(index={
            'CITY': 'City',
            'STABBR': 'State',
            'CONTROL_TYPE': 'Institution Type',
            'UGDS': 'Undergraduate Enrollment'
        })

        st.dataframe(overview_df, use_container_width=True)

        # Add enrollment visualization
        if 'UGDS' in selected_df.columns:
            # Display current enrollment as a simple table for quick reference
            st.markdown("### Current Enrollment")

            # Create a clean table showing current enrollment
            enrollment_df = selected_df[['INSTNM', 'UGDS']].copy()
            enrollment_df = enrollment_df.sort_values('UGDS', ascending=False)
            enrollment_df.columns = ['University', 'Undergraduate Enrollment']
            enrollment_df['Undergraduate Enrollment'] = enrollment_df['Undergraduate Enrollment'].apply(lambda x: f"{int(x):,}")

            st.dataframe(enrollment_df, use_container_width=True, hide_index=True)

            # Display historical enrollment trends using the new function
            viz.plot_enrollment_trend(selected_df, historical_data)

        # Add test score policy comparison if available
        if 'ADMCON7' in selected_df.columns:
            st.markdown("### Test Score Policy Comparison")

            # Map ADMCON7 values to readable labels
            policy_map = {
                1: "Required",
                2: "Recommended",
                3: "Neither Required nor Recommended",
                4: "Unknown",
                5: "Considered but not Required"
            }

            # Create a new column with the mapped values
            selected_df['Test_Policy'] = selected_df['ADMCON7'].apply(
                lambda x: policy_map.get(int(x), "Unknown") if pd.notna(x) else "Unknown"
            )

            # Create a more visually appealing representation
            st.markdown("#### Test Score Policies")

            # Create a grid layout
            cols = st.columns(len(selected_df))

            # Display each university's policy using the reusable function
            for i, (_, uni) in enumerate(selected_df.iterrows()):
                with cols[i]:
                    # Create a styled card with university name
                    st.markdown(f"""
                    <div style="text-align: center; margin-bottom: 10px;">
                        <h4 style="margin: 0; color: #333; font-size: 0.9rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{uni['INSTNM']}</h4>
                    </div>
                    """, unsafe_allow_html=True)

                    # Use the reusable function for test policy card
                    # We need to convert the Test_Policy back to ADMCON7 value
                    if 'ADMCON7' in uni:
                        viz.plot_test_policy_card(uni, key_prefix=f"compare_test_{i}")
                    elif 'Test_Policy' in uni:
                        # Map the text policy back to ADMCON7 value
                        policy_to_admcon = {
                            "Required": 1,
                            "Recommended": 2,
                            "Neither Required nor Recommended": 3,
                            "Do not know": 4,
                            "Considered but not Required": 5,
                            "Unknown": 4
                        }

                        # Create a copy of the uni Series to avoid modifying the original
                        uni_copy = uni.copy()
                        if uni['Test_Policy'] in policy_to_admcon:
                            uni_copy['ADMCON7'] = policy_to_admcon[uni['Test_Policy']]
                            viz.plot_test_policy_card(uni_copy, key_prefix=f"compare_test_{i}")
                        else:
                            st.info("Test score policy information not available.")

    # Cost Tab
    with comp_tabs[1]:
        st.markdown("### Cost Comparison")

        # Tuition comparison
        if 'TUITIONFEE_IN' in selected_df.columns and 'TUITIONFEE_OUT' in selected_df.columns:
            st.markdown("#### Tuition Comparison")

            # Create a grid layout for tuition cards
            cols = st.columns(len(selected_df))

            # Display each university's tuition in a card
            for i, (_, uni) in enumerate(selected_df.iterrows()):
                with cols[i]:
                    in_state = uni['TUITIONFEE_IN'] if pd.notna(uni['TUITIONFEE_IN']) else "N/A"
                    out_state = uni['TUITIONFEE_OUT'] if pd.notna(uni['TUITIONFEE_OUT']) else "N/A"

                    # Format the values
                    in_state_formatted = f"${in_state:,.0f}" if isinstance(in_state, (int, float)) else in_state
                    out_state_formatted = f"${out_state:,.0f}" if isinstance(out_state, (int, float)) else out_state

                    # Calculate the difference between in-state and out-state tuition
                    if isinstance(in_state, (int, float)) and isinstance(out_state, (int, float)):
                        diff = out_state - in_state
                        diff_formatted = f"${diff:,.0f}"
                        diff_percent = (diff / in_state) * 100 if in_state > 0 else 0
                        diff_text = f"(+{diff_percent:.1f}%)"
                    else:
                        diff_formatted = "N/A"
                        diff_text = ""

                    st.markdown(f"""
                    <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; text-align: center; background-color: white;">
                        <h4 style="margin-top: 0; color: #333; font-size: 0.9rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{uni['INSTNM']}</h4>
                        <div style="margin: 10px 0;">
                            <p style="margin: 5px 0; font-size: 0.8rem; color: #666;">In-State</p>
                            <p style="font-size: 1.1rem; font-weight: bold; margin: 0; color: #333;">{in_state_formatted}</p>
                        </div>
                        <div style="margin: 10px 0;">
                            <p style="margin: 5px 0; font-size: 0.8rem; color: #666;">Out-of-State</p>
                            <p style="font-size: 1.1rem; font-weight: bold; margin: 0; color: #333;">{out_state_formatted}</p>
                            <p style="font-size: 0.75rem; color: #666; margin: 2px 0;">{diff_formatted} {diff_text}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            # Add a historical tuition trend chart
            st.markdown("#### Tuition Trends")

            if not historical_data.empty:
                # Create a line chart for tuition trends
                fig = go.Figure()

                # Add data for each university
                for _, uni in selected_df.iterrows():
                    uni_id = uni['UNITID']
                    uni_name = uni['INSTNM']

                    # Get historical data for this university
                    uni_history = historical_data[historical_data['UNITID'] == uni_id].copy()

                    if not uni_history.empty and 'TUITIONFEE_IN' in uni_history.columns:
                        # Get the data sorted by year
                        tuition_trend = uni_history[['YEAR', 'TUITIONFEE_IN']].dropna().sort_values('YEAR')

                        if not tuition_trend.empty and len(tuition_trend) > 1:
                            # Add a line for this university
                            fig.add_trace(go.Scatter(
                                x=tuition_trend['YEAR'],
                                y=tuition_trend['TUITIONFEE_IN'],
                                mode='lines+markers',
                                name=f"{uni_name} (In-State)",
                                line=dict(width=2),
                                hovertemplate='%{y:$,.0f}'
                            ))

                # Improve layout
                fig.update_layout(
                    title="In-State Tuition Trends",
                    xaxis_title="Year",
                    yaxis_title="Tuition ($)",
                    yaxis_tickformat="$,.0f",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )

                st.plotly_chart(fig, use_container_width=True)

    # Academics Tab
    with comp_tabs[2]:
        st.markdown("### Academic Comparison")

        # Admission rate comparison
        if 'ADM_RATE' in selected_df.columns:
            st.markdown("#### Admission Rate")

            # Create a grid layout for admission rate metrics
            gauge_cols = st.columns(len(selected_df))

            for i, (_, uni) in enumerate(selected_df.iterrows()):
                with gauge_cols[i]:
                    # Create a styled card with university name
                    st.markdown(f"""
                    <div style="text-align: center; margin-bottom: 10px;">
                        <h4 style="margin: 0; color: #333; font-size: 0.9rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{uni['INSTNM']}</h4>
                    </div>
                    """, unsafe_allow_html=True)

                    # Use the reusable function for admission rate card
                    viz.plot_admission_rate_card(uni, key_prefix=f"compare_{i}")

            # Add historical admission rate trend
            if not historical_data.empty:
                st.markdown("#### Admission Rate Trends")

                # Create a line chart for admission rate trends
                fig = go.Figure()

                # Add data for each university
                for _, uni in selected_df.iterrows():
                    uni_id = uni['UNITID']
                    uni_name = uni['INSTNM']

                    # Get historical data for this university
                    uni_history = historical_data[historical_data['UNITID'] == uni_id].copy()

                    if not uni_history.empty and 'ADM_RATE' in uni_history.columns:
                        # Get the data sorted by year
                        adm_trend = uni_history[['YEAR', 'ADM_RATE']].dropna().sort_values('YEAR')

                        if not adm_trend.empty and len(adm_trend) > 1:
                            # Convert to percentage
                            adm_trend['ADM_RATE'] = adm_trend['ADM_RATE'] * 100

                            # Add a line for this university
                            fig.add_trace(go.Scatter(
                                x=adm_trend['YEAR'],
                                y=adm_trend['ADM_RATE'],
                                mode='lines+markers',
                                name=uni_name,
                                line=dict(width=2),
                                hovertemplate='%{y:.1f}%'
                            ))

                # Improve layout
                fig.update_layout(
                    title="Admission Rate Trends",
                    xaxis_title="Year",
                    yaxis_title="Admission Rate (%)",
                    yaxis_tickformat=".1f%",
                    height=500,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )

                st.plotly_chart(fig, use_container_width=True)

        # Test score comparison
        if 'SAT_AVG' in selected_df.columns:
            st.markdown("#### SAT Score Comparison")

            # Create a bullet chart for SAT scores
            fig = go.Figure()

            # Get the national average SAT score (approximately 1050)
            national_avg = 1050

            # Add a reference line for the national average
            fig.add_shape(
                type="line",
                x0=-0.5,
                x1=len(selected_df) - 0.5,
                y0=national_avg,
                y1=national_avg,
                line=dict(color="gray", width=1, dash="dash"),
            )

            # Add annotation for the national average
            fig.add_annotation(
                x=len(selected_df) - 0.5,
                y=national_avg,
                text="National Average",
                showarrow=False,
                yshift=10,
                font=dict(size=10, color="gray")
            )

            # Add bars for each university
            for i, (_, uni) in enumerate(selected_df.iterrows()):
                sat_score = uni['SAT_AVG'] if pd.notna(uni['SAT_AVG']) else None

                if sat_score is not None:
                    # Determine color based on SAT score (higher score = darker blue)
                    if sat_score >= 1400:
                        bar_color = '#0047AB'  # Strong cobalt blue for high scores
                    elif sat_score >= 1300:
                        bar_color = '#1E5AA8'  # Medium blue
                    elif sat_score >= 1200:
                        bar_color = '#4682B4'  # Steel blue
                    elif sat_score >= 1100:
                        bar_color = '#6CA6CD'  # Sky blue
                    else:
                        bar_color = '#87CEEB'  # Light sky blue for lower scores

                    fig.add_trace(go.Bar(
                        x=[uni['INSTNM']],
                        y=[sat_score],
                        name=uni['INSTNM'],
                        marker_color=bar_color,
                        text=[f"{int(sat_score)}"],
                        textposition='outside',
                        hovertemplate='%{y}'
                    ))

            # Improve layout
            fig.update_layout(
                title="Average SAT Scores",
                xaxis_title="",
                yaxis_title="SAT Score",
                showlegend=False,
                height=400,
                yaxis_range=[800, 1600]  # SAT score range
            )

            st.plotly_chart(fig, use_container_width=True)

            # Add historical SAT score trend
            if not historical_data.empty:
                st.markdown("#### SAT Score Trends")

                # Create a line chart for SAT score trends
                fig = go.Figure()

                # Add data for each university
                for _, uni in selected_df.iterrows():
                    uni_id = uni['UNITID']
                    uni_name = uni['INSTNM']

                    # Get historical data for this university
                    uni_history = historical_data[historical_data['UNITID'] == uni_id].copy()

                    if not uni_history.empty and 'SAT_AVG' in uni_history.columns:
                        # Get the data sorted by year
                        sat_trend = uni_history[['YEAR', 'SAT_AVG']].dropna().sort_values('YEAR')

                        if not sat_trend.empty and len(sat_trend) > 1:
                            # Add a line for this university
                            fig.add_trace(go.Scatter(
                                x=sat_trend['YEAR'],
                                y=sat_trend['SAT_AVG'],
                                mode='lines+markers',
                                name=uni_name,
                                line=dict(width=2),
                                hovertemplate='%{y:.0f}'
                            ))

                # Improve layout
                fig.update_layout(
                    title="SAT Score Trends",
                    xaxis_title="Year",
                    yaxis_title="Average SAT Score",
                    height=500,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )

                st.plotly_chart(fig, use_container_width=True)

    # Outcomes Tab
    with comp_tabs[3]:
        st.markdown("### Outcomes Comparison")

        # Graduation rate comparison
        if 'C150_4' in selected_df.columns:
            st.markdown("#### Graduation Rate", help='The 4-year graduation rate represents the percentage of first-time, full-time undergraduate students who complete their program within 4 years. National average is approximately 62%.')

            # Create a grid layout for graduation rate metrics
            gauge_cols = st.columns(len(selected_df))

            for i, (_, uni) in enumerate(selected_df.iterrows()):
                with gauge_cols[i]:
                    # Create a styled card with university name
                    st.markdown(f"""
                    <div style="text-align: center; margin-bottom: 10px;">
                        <h4 style="margin: 0; color: #333; font-size: 0.9rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{uni['INSTNM']}</h4>
                    </div>
                    """, unsafe_allow_html=True)

                    # Use the reusable function for graduation rate card
                    viz.outcomes.plot_graduation_rate_card(uni, key_prefix=f"compare_grad_{i}")

            # Add historical graduation rate trend
            if not historical_data.empty:
                st.markdown("#### Graduation Rate Trends")

                # Create a line chart for graduation rate trends
                fig = go.Figure()

                # Add data for each university
                for _, uni in selected_df.iterrows():
                    uni_id = uni['UNITID']
                    uni_name = uni['INSTNM']

                    # Get historical data for this university
                    uni_history = historical_data[historical_data['UNITID'] == uni_id].copy()

                    if not uni_history.empty and 'C150_4' in uni_history.columns:
                        # Get the data sorted by year
                        grad_trend = uni_history[['YEAR', 'C150_4']].dropna().sort_values('YEAR')

                        if not grad_trend.empty and len(grad_trend) > 1:
                            # Convert to percentage
                            grad_trend['C150_4'] = grad_trend['C150_4'] * 100

                            # Add a line for this university
                            fig.add_trace(go.Scatter(
                                x=grad_trend['YEAR'],
                                y=grad_trend['C150_4'],
                                mode='lines+markers',
                                name=uni_name,
                                line=dict(width=2),
                                hovertemplate='%{y:.1f}%'
                            ))

                # Improve layout
                fig.update_layout(
                    title="Graduation Rate Trends",
                    xaxis_title="Year",
                    yaxis_title="Graduation Rate (%)",
                    yaxis_tickformat=".1f%",
                    height=500,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )

                st.plotly_chart(fig, use_container_width=True)

        # Financial outcomes
        if 'MD_EARN_WNE_P10' in selected_df.columns or 'DEBT_MDN' in selected_df.columns:
            st.markdown("#### Financial Outcomes")

            # Create a grid layout for cards
            card_cols = st.columns(len(selected_df))

            for i, (_, uni) in enumerate(selected_df.iterrows()):
                with card_cols[i]:
                    earnings = uni['MD_EARN_WNE_P10'] if 'MD_EARN_WNE_P10' in uni.index and pd.notna(uni['MD_EARN_WNE_P10']) else None
                    debt = uni['DEBT_MDN'] if 'DEBT_MDN' in uni.index and pd.notna(uni['DEBT_MDN']) else None

                    # Calculate debt-to-earnings ratio if both values are available
                    if earnings is not None and debt is not None and earnings > 0:
                        ratio = debt / earnings
                        ratio_formatted = f"{ratio:.2f}x"
                    else:
                        ratio_formatted = "N/A"

                    # Format the values
                    earnings_formatted = f"${earnings:,.0f}" if earnings is not None else "N/A"
                    debt_formatted = f"${debt:,.0f}" if debt is not None else "N/A"

                    st.markdown(f"""
                    <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; text-align: center; background-color: white;">
                        <h4 style="margin-top: 0; color: #333; font-size: 0.9rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{uni['INSTNM']}</h4>
                        <div style="margin: 10px 0;">
                            <p style="margin: 5px 0; font-size: 0.8rem; color: #666;">Median Earnings</p>
                            <p style="font-size: 1.1rem; font-weight: bold; margin: 0; color: #333;">{earnings_formatted}</p>
                            <p style="font-size: 0.75rem; color: #666; margin: 2px 0;">10 years after entry</p>
                        </div>
                        <div style="margin: 10px 0;">
                            <p style="margin: 5px 0; font-size: 0.8rem; color: #666;">Median Debt</p>
                            <p style="font-size: 1.1rem; font-weight: bold; margin: 0; color: #333;">{debt_formatted}</p>
                        </div>
                        <div style="margin: 10px 0; padding-top: 5px; border-top: 1px solid #f0f0f0;">
                            <p style="margin: 5px 0; font-size: 0.8rem; color: #666;">Debt-to-Earnings Ratio</p>
                            <p style="font-size: 1.1rem; font-weight: bold; margin: 0; color: #333;">{ratio_formatted}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            # Add detailed debt comparison chart
            st.markdown("#### Detailed Debt Comparison")

            # Use the reusable function for detailed debt comparison
            viz.outcomes.plot_detailed_debt_comparison(selected_df)


