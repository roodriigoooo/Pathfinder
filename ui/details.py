"""
University details view for the University Scout application.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from utils import (
    get_download_link, add_to_shortlist, remove_from_shortlist,
    toggle_university_selection, set_active_tab
)
import visualizations as viz

def display_university_details(unitid, inst_data, hist_data, fos_data, rank_data):
    """
    Displays detailed information for a selected university.

    Args:
        unitid: University ID to display
        inst_data: DataFrame containing institution data
        hist_data: DataFrame containing historical data
        fos_data: DataFrame containing field of study data
        rank_data: DataFrame containing ranking data

    Returns:
        None: Displays content directly using streamlit
    """
    # Get the university data
    uni_data = inst_data[inst_data['UNITID'] == unitid]
    if uni_data.empty:
        st.error("University data not found.")
        return

    uni_data = uni_data.iloc[0]  # Get the row for the selected uni

    # Create a visually appealing header card with university info and action buttons
    st.markdown(f"""
    <div style="background-color: white; border-radius: 10px; padding: 20px; margin-bottom: 20px; border: 1px solid #e0e0e0; border-left: 5px solid #1e88e5;">
        <h1 style="margin-top: 0; color: #1e88e5;">🏛️ {uni_data['INSTNM']}</h1>
        <h3 style="margin-bottom: 10px; color: #333;">📍 {uni_data['CITY']}, {uni_data['STABBR']} • {uni_data['CONTROL_TYPE']}</h3>
    </div>
    """, unsafe_allow_html=True)

    # Action buttons in a more compact layout with icons
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    with col1:
        is_shortlisted = unitid in st.session_state.shortlisted_universities
        if is_shortlisted:
            if st.button("❌ Remove from Shortlist", key=f"remove_shortlist_{unitid}"):
                remove_from_shortlist(unitid)
                st.rerun()
        else:
            if st.button("📋 Add to Shortlist", key=f"add_shortlist_{unitid}"):
                add_to_shortlist(unitid)
                st.rerun()

    with col2:
        is_selected = unitid in st.session_state.selected_universities
        if is_selected:
            if st.button("❌ Remove from Comparison", key=f"remove_comparison_{unitid}"):
                toggle_university_selection(unitid)
        else:
            if st.button("⚖️ Add to Comparison", key=f"add_comparison_{unitid}"):
                toggle_university_selection(unitid)

    with col3:
        # Generate profile button
        if st.button("📄 Generate Profile", key=f"generate_profile_{unitid}"):
            st.session_state.show_profile = True

    with col4:
        if st.button("🔙 Back to List", key=f"back_to_list_{unitid}"):
            set_active_tab("Explore")
            st.session_state.selected_university_id = None
            st.rerun()

    # Add a tabbed interface for better organization
    detail_tabs = st.tabs(["📊 Overview", "🎓 Academics", "💰 Finances", "🌈 Campus Life", "📈 Outcomes", "🏆 Rankings"])

    # Initialize session state for profile generation
    if 'show_profile' not in st.session_state:
        st.session_state.show_profile = False

    # Overview Tab
    with detail_tabs[0]:
        # Create a two-column layout for basic info
        col1, col2 = st.columns(2)

        # Left column: Key metrics in a card-like display
        with col1:
            st.markdown("### Key Information")

            # Create a metrics grid
            metric_col1, metric_col2 = st.columns(2)
            with metric_col1:
                st.metric("City", uni_data['CITY'])
                st.metric("Control Type", uni_data['CONTROL_TYPE'])

                # Admission rate if available
                if pd.notna(uni_data['ADM_RATE']):
                    st.metric("Admission Rate", f"{uni_data['ADM_RATE']:.1%}")

            with metric_col2:
                st.metric("State", uni_data['STABBR'])

                # Enrollment if available
                if 'UGDS' in uni_data and pd.notna(uni_data['UGDS']):
                    st.metric("Enrollment", f"{int(uni_data['UGDS']):,}")

                # Graduation rate if available
                if pd.notna(uni_data['C150_4']):
                    st.metric("Graduation Rate", f"{uni_data['C150_4']:.1%}")

        # Right column: Links and additional info
        with col2:
            st.markdown("### University Links")

            # Create a card-like container for links
            st.markdown("""
            <style>
            .link-card {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 15px;
                background-color: white;
            }
            .link-card h4 {
                color: #333;
                margin-top: 0;
            }
            .link-card a {
                color: #1e88e5;
                text-decoration: none;
            }
            .link-card a:hover {
                text-decoration: underline;
            }
            </style>
            """, unsafe_allow_html=True)

            # Website link
            if 'INSTURL' in uni_data and pd.notna(uni_data['INSTURL']):
                st.markdown(f"""
                <div class="link-card">
                    <h4>🌐 Official Website</h4>
                    <a href="http://{uni_data['INSTURL']}" target="_blank">{uni_data['INSTURL']}</a>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="link-card">
                    <h4>🌐 Official Website</h4>
                    <p>Not available</p>
                </div>
                """, unsafe_allow_html=True)

            # Net Price Calculator link
            if 'NPCURL' in uni_data and pd.notna(uni_data['NPCURL']):
                st.markdown(f"""
                <div class="link-card">
                    <h4>💲 Net Price Calculator</h4>
                    <a href="http://{uni_data['NPCURL']}" target="_blank">Calculate your cost</a>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="link-card">
                    <h4>💲 Net Price Calculator</h4>
                    <p>Not available</p>
                </div>
                """, unsafe_allow_html=True)

    # Academics Tab
    with detail_tabs[1]:
        st.markdown("### 🎓 Admissions & Test Scores")

        # Create a three-column layout for test scores
        score_col1, score_col2, score_col3 = st.columns(3)

        with score_col1:
            # Admission Rate with visual indicator
            if pd.notna(uni_data['ADM_RATE']):
                adm_rate = uni_data['ADM_RATE']
                # Determine selectivity level
                if adm_rate < 0.1:
                    selectivity = "Highly Selective"
                    color = "#1e88e5"  # Blue
                elif adm_rate < 0.25:
                    selectivity = "Very Selective"
                    color = "#43a047"  # Green
                elif adm_rate < 0.5:
                    selectivity = "Selective"
                    color = "#fdd835"  # Yellow
                elif adm_rate < 0.75:
                    selectivity = "Moderately Selective"
                    color = "#fb8c00"  # Orange
                else:
                    selectivity = "Inclusive"
                    color = "#e53935"  # Red

                st.markdown(f"""
                <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; background-color: white;">
                    <h4 style="margin-top: 0; color: #333;">Admission Rate</h4>
                    <p style="font-size: 24px; font-weight: bold; margin: 10px 0; color: #333;">{adm_rate:.1%}</p>
                    <p style="color: {color}; font-weight: bold; margin-bottom: 5px;">{selectivity}</p>
                    <div style="background-color: #e9ecef; border-radius: 4px; height: 8px;">
                        <div style="background-color: {color}; width: {min(adm_rate * 100, 100)}%; height: 100%; border-radius: 4px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; background-color: white;">
                    <h4 style="margin-top: 0; color: #333;">Admission Rate</h4>
                    <p style="font-size: 24px; font-weight: bold; margin: 10px 0; color: #333;">N/A</p>
                </div>
                """, unsafe_allow_html=True)

        with score_col2:
            # SAT Score with visual indicator
            if pd.notna(uni_data['SAT_AVG']):
                sat_score = int(uni_data['SAT_AVG'])
                # Determine SAT level (approximate percentiles)
                if sat_score >= 1500:
                    sat_level = "Top 1%"
                    color = "#1e88e5"  # Blue
                elif sat_score >= 1400:
                    sat_level = "Top 5%"
                    color = "#43a047"  # Green
                elif sat_score >= 1300:
                    sat_level = "Top 10%"
                    color = "#fdd835"  # Yellow
                elif sat_score >= 1200:
                    sat_level = "Top 25%"
                    color = "#fb8c00"  # Orange
                else:
                    sat_level = "Average or Below"
                    color = "#e53935"  # Red

                # Calculate percentage for visual (1600 is max SAT)
                sat_percent = min(sat_score / 1600 * 100, 100)

                st.markdown(f"""
                <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; background-color: white;">
                    <h4 style="margin-top: 0; color: #333;">Average SAT Score</h4>
                    <p style="font-size: 24px; font-weight: bold; margin: 10px 0; color: #333;">{sat_score}</p>
                    <p style="color: {color}; font-weight: bold; margin-bottom: 5px;">{sat_level}</p>
                    <div style="background-color: #e9ecef; border-radius: 4px; height: 8px;">
                        <div style="background-color: {color}; width: {sat_percent}%; height: 100%; border-radius: 4px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; background-color: white;">
                    <h4 style="margin-top: 0; color: #333;">Average SAT Score</h4>
                    <p style="font-size: 24px; font-weight: bold; margin: 10px 0; color: #333;">N/A</p>
                </div>
                """, unsafe_allow_html=True)

        with score_col3:
            # ACT Score with visual indicator
            if 'ACTCMMID' in uni_data and pd.notna(uni_data['ACTCMMID']):
                act_score = int(uni_data['ACTCMMID'])
                # Determine ACT level (approximate percentiles)
                if act_score >= 34:
                    act_level = "Top 1%"
                    color = "#1e88e5"  # Blue
                elif act_score >= 32:
                    act_level = "Top 5%"
                    color = "#43a047"  # Green
                elif act_score >= 30:
                    act_level = "Top 10%"
                    color = "#fdd835"  # Yellow
                elif act_score >= 27:
                    act_level = "Top 25%"
                    color = "#fb8c00"  # Orange
                else:
                    act_level = "Average or Below"
                    color = "#e53935"  # Red

                # Calculate percentage for visual (36 is max ACT)
                act_percent = min(act_score / 36 * 100, 100)

                st.markdown(f"""
                <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; background-color: white;">
                    <h4 style="margin-top: 0; color: #333;">Median ACT Score</h4>
                    <p style="font-size: 24px; font-weight: bold; margin: 10px 0; color: #333;">{act_score}</p>
                    <p style="color: {color}; font-weight: bold; margin-bottom: 5px;">{act_level}</p>
                    <div style="background-color: #e9ecef; border-radius: 4px; height: 8px;">
                        <div style="background-color: {color}; width: {act_percent}%; height: 100%; border-radius: 4px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; background-color: white;">
                    <h4 style="margin-top: 0; color: #333;">Median ACT Score</h4>
                    <p style="font-size: 24px; font-weight: bold; margin: 10px 0; color: #333;">N/A</p>
                </div>
                """, unsafe_allow_html=True)

        # Historical admission trend
        st.markdown("### Historical Admission Trends")
        viz.plot_admission_trend(uni_data, hist_data, unitid)

    # Finances Tab
    with detail_tabs[2]:
        st.markdown("### 💰 Cost & Financial Aid")

        # Create a visually appealing cost comparison
        if pd.notna(uni_data['TUITIONFEE_IN']) or pd.notna(uni_data['TUITIONFEE_OUT']):
            # Get tuition values
            in_state = int(uni_data['TUITIONFEE_IN']) if pd.notna(uni_data['TUITIONFEE_IN']) else 0
            out_state = int(uni_data['TUITIONFEE_OUT']) if pd.notna(uni_data['TUITIONFEE_OUT']) else 0

            # Create a visual comparison
            st.markdown("""
            <style>
            .tuition-card {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 20px;
                background-color: white;
            }
            .tuition-card h3 {
                color: #333;
                margin-top: 0;
            }
            .tuition-bar {
                height: 30px;
                background-color: #e9ecef;
                border-radius: 4px;
                margin: 10px 0;
                position: relative;
            }
            .tuition-fill {
                height: 100%;
                border-radius: 4px;
                position: absolute;
                left: 0;
                top: 0;
            }
            .tuition-label {
                position: absolute;
                right: 10px;
                top: 5px;
                color: #212529;
                font-weight: bold;
            }
            </style>

            <div class="tuition-card">
                <h3 style="margin-top: 0;">Annual Tuition Comparison</h3>
            """, unsafe_allow_html=True)

            # Maximum for scaling (use the larger of the two, or a minimum of $50,000)
            max_tuition = max(in_state, out_state, 50000)

            # In-state tuition bar
            if pd.notna(uni_data['TUITIONFEE_IN']):
                in_state_percent = (in_state / max_tuition) * 100
                st.markdown(f"""
                <p>In-State Tuition</p>
                <div class="tuition-bar">
                    <div class="tuition-fill" style="width: {in_state_percent}%; background-color: #43a047;"></div>
                    <span class="tuition-label">${in_state:,}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <p>In-State Tuition</p>
                <div class="tuition-bar">
                    <span class="tuition-label">N/A</span>
                </div>
                """, unsafe_allow_html=True)

            # Out-of-state tuition bar
            if pd.notna(uni_data['TUITIONFEE_OUT']):
                out_state_percent = (out_state / max_tuition) * 100
                st.markdown(f"""
                <p>Out-of-State Tuition</p>
                <div class="tuition-bar">
                    <div class="tuition-fill" style="width: {out_state_percent}%; background-color: #1e88e5;"></div>
                    <span class="tuition-label">${out_state:,}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <p>Out-of-State Tuition</p>
                <div class="tuition-bar">
                    <span class="tuition-label">N/A</span>
                </div>
                """, unsafe_allow_html=True)

            # Close the card
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Tuition information is not available for this university.")

        # Debt information in a card
        if 'GRAD_DEBT_MDN' in uni_data and pd.notna(uni_data['GRAD_DEBT_MDN']):
            debt = int(uni_data['GRAD_DEBT_MDN'])

            # Determine debt level
            if debt < 20000:
                debt_level = "Low"
                color = "#43a047"  # Green
            elif debt < 30000:
                debt_level = "Moderate"
                color = "#fdd835"  # Yellow
            elif debt < 40000:
                debt_level = "High"
                color = "#fb8c00"  # Orange
            else:
                debt_level = "Very High"
                color = "#e53935"  # Red

            st.markdown(f"""
            <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 20px; margin-bottom: 20px; background-color: white;">
                <h3 style="margin-top: 0; color: #333;">Median Graduate Debt</h3>
                <p style="font-size: 28px; font-weight: bold; margin: 10px 0; color: {color};">${debt:,}</p>
                <p style="color: {color}; font-weight: bold;">{debt_level} Debt Level</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 20px; margin-bottom: 20px; background-color: white;">
                <h3 style="margin-top: 0; color: #333;">Median Graduate Debt</h3>
                <p style="font-size: 28px; font-weight: bold; margin: 10px 0; color: #333;">N/A</p>
            </div>
            """, unsafe_allow_html=True)

        # Historical tuition trend
        st.markdown("### Historical Tuition Trends")
        viz.plot_tuition_trend(uni_data, hist_data, unitid)

    # Campus Life Tab
    with detail_tabs[3]:
        st.markdown("### 🌈 Campus Life & Diversity")

        # Student body size in a visually appealing card
        if 'UGDS' in uni_data and pd.notna(uni_data['UGDS']):
            enrollment = int(uni_data['UGDS'])

            # Determine size category
            if enrollment < 1000:
                size_category = "Very Small"
                color = "#e53935"  # Red
            elif enrollment < 5000:
                size_category = "Small"
                color = "#fb8c00"  # Orange
            elif enrollment < 15000:
                size_category = "Medium"
                color = "#fdd835"  # Yellow
            elif enrollment < 30000:
                size_category = "Large"
                color = "#43a047"  # Green
            else:
                size_category = "Very Large"
                color = "#1e88e5"  # Blue

            st.markdown(f"""
            <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 20px; margin-bottom: 20px; background-color: white;">
                <h3 style="margin-top: 0; color: #333;">Undergraduate Enrollment</h3>
                <p style="font-size: 32px; font-weight: bold; margin: 10px 0; color: {color};">{enrollment:,}</p>
                <p style="color: {color}; font-weight: bold;">{size_category} Institution</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 20px; margin-bottom: 20px; background-color: white;">
                <h3 style="margin-top: 0; color: #333;">Undergraduate Enrollment</h3>
                <p style="font-size: 32px; font-weight: bold; margin: 10px 0; color: #333;">N/A</p>
            </div>
            """, unsafe_allow_html=True)

        # Diversity data in a more visually appealing way
        st.markdown("### Student Body Diversity")

        diversity_cols = ['UGDS_WHITE', 'UGDS_BLACK', 'UGDS_HISP', 'UGDS_ASIAN',
                          'UGDS_AIAN', 'UGDS_NHPI', 'UGDS_2MOR', 'UGDS_NRA', 'UGDS_UNKN']
        has_diversity_data = any(col in uni_data.index for col in diversity_cols)

        if has_diversity_data:
            # Create a more interactive diversity visualization
            viz.plot_diversity_pie(uni_data)

            # Add a diversity breakdown table with visual bars
            st.markdown("#### Diversity Breakdown")

            # Define diversity labels and colors
            diversity_labels = {
                'UGDS_WHITE': 'White',
                'UGDS_BLACK': 'Black',
                'UGDS_HISP': 'Hispanic/Latino',
                'UGDS_ASIAN': 'Asian',
                'UGDS_AIAN': 'American Indian/Alaska Native',
                'UGDS_NHPI': 'Native Hawaiian/Pacific Islander',
                'UGDS_2MOR': 'Two or More Races',
                'UGDS_NRA': 'Non-Resident Alien',
                'UGDS_UNKN': 'Unknown'
            }

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

            # Create HTML for the diversity breakdown
            st.markdown("""
            <style>
            .diversity-table {
                width: 100%;
                border-collapse: collapse;
            }
            .diversity-table th, .diversity-table td {
                padding: 8px;
                text-align: left;
                border-bottom: 1px solid #e0e0e0;
            }
            .diversity-bar {
                height: 20px;
                background-color: #e9ecef;
                border-radius: 4px;
                margin: 5px 0;
                position: relative;
            }
            .diversity-fill {
                height: 100%;
                border-radius: 4px;
                position: absolute;
                left: 0;
                top: 0;
            }
            .diversity-label {
                position: absolute;
                right: 10px;
                top: 2px;
                color: #212529;
                font-weight: bold;
            }
            </style>

            <table class="diversity-table">
                <tr>
                    <th>Race/Ethnicity</th>
                    <th>Percentage</th>
                </tr>
            """, unsafe_allow_html=True)

            # Add rows for each diversity category
            for col in diversity_cols:
                if col in uni_data.index and pd.notna(uni_data[col]) and uni_data[col] > 0:
                    label = diversity_labels.get(col, col)
                    value = uni_data[col]
                    color = diversity_colors.get(col, '#777777')

                    st.markdown(f"""
                    <tr>
                        <td>{label}</td>
                        <td style="width: 70%;">
                            <div class="diversity-bar">
                                <div class="diversity-fill" style="width: {value*100}%; background-color: {color};"></div>
                                <span class="diversity-label">{value:.1%}</span>
                            </div>
                        </td>
                    </tr>
                    """, unsafe_allow_html=True)

            # Close the table
            st.markdown("</table>", unsafe_allow_html=True)
        else:
            st.info("Diversity data not available for this university.")

    # Outcomes Tab
    with detail_tabs[4]:
        st.markdown("### 📈 Outcomes & Career Success")

        # Create a two-column layout
        outcome_col1, outcome_col2 = st.columns(2)

        with outcome_col1:
            # Graduation Rate with visual gauge
            if pd.notna(uni_data['C150_4']):
                grad_rate = uni_data['C150_4']

                # Determine graduation rate level
                if grad_rate >= 0.9:
                    grad_level = "Excellent"
                    color = "#1e88e5"  # Blue
                elif grad_rate >= 0.75:
                    grad_level = "Very Good"
                    color = "#43a047"  # Green
                elif grad_rate >= 0.6:
                    grad_level = "Good"
                    color = "#fdd835"  # Yellow
                elif grad_rate >= 0.4:
                    grad_level = "Fair"
                    color = "#fb8c00"  # Orange
                else:
                    grad_level = "Poor"
                    color = "#e53935"  # Red

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
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 20px; margin-bottom: 20px; background-color: #f8f9fa; text-align: center;">
                    <h3 style="margin-top: 0;">4-Year Graduation Rate</h3>
                    <p style="font-size: 24px; font-weight: bold; margin: 10px 0;">N/A</p>
                </div>
                """, unsafe_allow_html=True)

        with outcome_col2:
            # Earnings with visual indicator
            if pd.notna(uni_data['MD_EARN_WNE_P10']):
                earnings = int(uni_data['MD_EARN_WNE_P10'])

                # Determine earnings level
                if earnings >= 75000:
                    earn_level = "Excellent"
                    color = "#1e88e5"  # Blue
                elif earnings >= 60000:
                    earn_level = "Very Good"
                    color = "#43a047"  # Green
                elif earnings >= 45000:
                    earn_level = "Good"
                    color = "#fdd835"  # Yellow
                elif earnings >= 35000:
                    earn_level = "Fair"
                    color = "#fb8c00"  # Orange
                else:
                    earn_level = "Below Average"
                    color = "#e53935"  # Red

                # Create a visual earnings indicator
                st.markdown(f"""
                <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 20px; margin-bottom: 20px; background-color: #f8f9fa; text-align: center;">
                    <h3 style="margin-top: 0;">Median Earnings (10 years after entry)</h3>
                    <p style="font-size: 32px; font-weight: bold; margin: 10px 0; color: {color};">${earnings:,}</p>
                    <p style="color: {color}; font-weight: bold;">{earn_level} Earning Potential</p>
                    <div style="background-color: #e9ecef; border-radius: 4px; height: 10px; margin-top: 10px;">
                        <div style="background-color: {color}; width: {min(earnings/100000*100, 100)}%; height: 100%; border-radius: 4px;"></div>
                    </div>
                    <p style="font-size: 12px; color: #666; margin-top: 5px;">Scale: $0 - $100,000+</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 20px; margin-bottom: 20px; background-color: #f8f9fa; text-align: center;">
                    <h3 style="margin-top: 0;">Median Earnings (10 years after entry)</h3>
                    <p style="font-size: 24px; font-weight: bold; margin: 10px 0;">N/A</p>
                </div>
                """, unsafe_allow_html=True)

        # Historical graduation rate trend
        st.markdown("### Historical Graduation Rate Trends")
        viz.plot_graduation_trend(uni_data, hist_data, unitid)

        # ROI Calculator (interactive element)
        st.markdown("### 🧮 Return on Investment Calculator")

        # Check if we have the necessary data
        has_tuition = pd.notna(uni_data['TUITIONFEE_IN']) or pd.notna(uni_data['TUITIONFEE_OUT'])
        has_earnings = pd.notna(uni_data['MD_EARN_WNE_P10'])

        if has_tuition and has_earnings:
            # Get values
            in_state = int(uni_data['TUITIONFEE_IN']) if pd.notna(uni_data['TUITIONFEE_IN']) else 0
            out_state = int(uni_data['TUITIONFEE_OUT']) if pd.notna(uni_data['TUITIONFEE_OUT']) else 0
            earnings = int(uni_data['MD_EARN_WNE_P10'])

            # Create interactive calculator
            st.markdown("""
            <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 20px; margin-bottom: 20px; background-color: #f8f9fa;">
                <h3 style="margin-top: 0;">Estimate Your Return on Investment</h3>
                <p>Use this calculator to estimate the financial return on your education investment.</p>
            </div>
            """, unsafe_allow_html=True)

            # User inputs
            calc_col1, calc_col2 = st.columns(2)

            with calc_col1:
                residency = st.radio("Residency Status:", ["In-State", "Out-of-State"])
                years = st.slider("Years to Complete Degree:", min_value=4, max_value=6, value=4)

            with calc_col2:
                financial_aid = st.slider("Estimated Annual Financial Aid ($):", min_value=0, max_value=30000, value=5000, step=1000)
                annual_salary_increase = st.slider("Expected Annual Salary Growth (%):", min_value=1.0, max_value=5.0, value=2.0, step=0.5)

            # Calculate ROI
            tuition = in_state if residency == "In-State" else out_state
            total_cost = (tuition - financial_aid) * years

            # Simple ROI calculation (10-year earnings vs. total cost)
            if total_cost > 0:
                # Calculate cumulative earnings over 10 years with growth
                cumulative_earnings = 0
                annual_salary = earnings

                for year in range(10):
                    cumulative_earnings += annual_salary
                    annual_salary *= (1 + annual_salary_increase/100)

                # Calculate ROI
                roi = (cumulative_earnings - total_cost) / total_cost * 100

                # Display results
                st.markdown(f"""
                <div style="border: 1px solid #43a047; border-radius: 8px; padding: 20px; margin-top: 20px; background-color: #e8f5e9;">
                    <h3 style="margin-top: 0; color: #2e7d32;">ROI Calculation Results</h3>
                    <table style="width: 100%;">
                        <tr>
                            <td style="padding: 8px; font-weight: bold;">Total Education Cost:</td>
                            <td style="padding: 8px; text-align: right;">${total_cost:,}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; font-weight: bold;">Estimated 10-Year Earnings:</td>
                            <td style="padding: 8px; text-align: right;">${int(cumulative_earnings):,}</td>
                        </tr>
                        <tr style="background-color: #c8e6c9;">
                            <td style="padding: 8px; font-weight: bold;">10-Year Return on Investment:</td>
                            <td style="padding: 8px; text-align: right; font-weight: bold;">{roi:.1f}%</td>
                        </tr>
                    </table>
                    <p style="font-size: 12px; color: #666; margin-top: 10px;">Note: This is a simplified calculation and actual returns may vary based on many factors.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Adjust the financial aid amount to calculate ROI.")
        else:
            st.info("Insufficient data to calculate return on investment.")

    # Rankings Tab
    with detail_tabs[5]:
        st.markdown("### 🏆 University Rankings")

        if not rank_data.empty:
            # Filter ranking data for this university
            # Need to match by name since UNITID is not in ranking data
            uni_name = uni_data['INSTNM']

            # Try to find matches in ranking data
            # This is imperfect since names might not match exactly
            rank_matches = rank_data[rank_data['institution_name'].str.contains(uni_name, case=False, na=False)]

            if not rank_matches.empty:
                # Group by source and year to get the most recent ranking for each source
                rank_matches = rank_matches.sort_values('year', ascending=False)
                latest_rankings = rank_matches.groupby('source').first().reset_index()

                # Display rankings in a visually appealing way
                st.markdown("""
                <style>
                .ranking-card {
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 20px;
                    margin-bottom: 20px;
                    background-color: #f8f9fa;
                    text-align: center;
                }
                .ranking-number {
                    font-size: 48px;
                    font-weight: bold;
                    margin: 10px 0;
                    color: #1e88e5;
                }
                .ranking-source {
                    font-size: 18px;
                    font-weight: bold;
                    margin-bottom: 5px;
                }
                .ranking-year {
                    font-size: 14px;
                    color: #666;
                }
                </style>
                """, unsafe_allow_html=True)

                # Create cards for each ranking source
                ranking_cols = st.columns(len(latest_rankings))

                for i, (_, rank) in enumerate(latest_rankings.iterrows()):
                    with ranking_cols[i]:
                        # Determine ranking color based on rank
                        if pd.notna(rank['world_rank']):
                            world_rank = int(rank['world_rank'])
                            if world_rank <= 10:
                                rank_color = "#1e88e5"  # Blue
                            elif world_rank <= 50:
                                rank_color = "#43a047"  # Green
                            elif world_rank <= 100:
                                rank_color = "#fdd835"  # Yellow
                            elif world_rank <= 200:
                                rank_color = "#fb8c00"  # Orange
                            else:
                                rank_color = "#757575"  # Gray
                        else:
                            world_rank = "N/A"
                            rank_color = "#757575"  # Gray

                        # Create ranking card
                        st.markdown(f"""
                        <div class="ranking-card">
                            <div class="ranking-source">{rank['source']} Ranking</div>
                            <div class="ranking-year">{int(rank['year'])}</div>
                            <div class="ranking-number" style="color: {rank_color};">{world_rank}</div>
                            <div>World Rank</div>
                        </div>
                        """, unsafe_allow_html=True)

                # Add ranking methodology explanations
                st.markdown("### About University Rankings")

                # Create tabs for each ranking system
                ranking_sources = latest_rankings['source'].unique()
                if len(ranking_sources) > 0:
                    ranking_tabs = st.tabs([f"{source} Methodology" for source in ranking_sources])

                    for i, source in enumerate(ranking_sources):
                        with ranking_tabs[i]:
                            if source == "Times":
                                st.markdown("""
                                #### Times Higher Education World University Rankings

                                The Times Higher Education World University Rankings assess research-intensive universities across their core missions:

                                - **Teaching (30%)**: Learning environment, reputation survey, staff-to-student ratio, doctorate-to-bachelor's ratio, institutional income
                                - **Research (30%)**: Research reputation, research income, research productivity
                                - **Citations (30%)**: Research influence measured by normalized citation impact
                                - **International Outlook (7.5%)**: International students, staff, and research collaborations
                                - **Industry Income (2.5%)**: Knowledge transfer measured by research income from industry

                                [Learn more about Times Higher Education methodology](https://www.timeshighereducation.com/world-university-rankings/world-university-rankings-2021-methodology)
                                """)
                            elif source == "Shanghai":
                                st.markdown("""
                                #### Shanghai Academic Ranking of World Universities (ARWU)

                                The Shanghai Ranking uses six objective indicators to rank universities:

                                - **Alumni winning Nobel Prizes and Fields Medals (10%)**
                                - **Staff winning Nobel Prizes and Fields Medals (20%)**
                                - **Highly Cited Researchers (20%)**
                                - **Papers published in Nature and Science (20%)**
                                - **Papers indexed in Science Citation Index-Expanded and Social Science Citation Index (20%)**
                                - **Per capita academic performance (10%)**

                                [Learn more about Shanghai ARWU methodology](http://www.shanghairanking.com/methodology/arwu/2021)
                                """)
                            elif source == "CWUR":
                                st.markdown("""
                                #### Center for World University Rankings (CWUR)

                                The CWUR ranks universities using seven indicators:

                                - **Quality of Education (25%)**: Alumni success measured by major international awards
                                - **Alumni Employment (25%)**: Alumni leadership positions in top companies
                                - **Quality of Faculty (10%)**: Faculty awards, prizes, and medals
                                - **Research Output (10%)**: Total number of research papers
                                - **Quality Publications (10%)**: Papers in top-tier journals
                                - **Influence (10%)**: Papers in highly-influential journals
                                - **Citations (10%)**: Research citation impact

                                [Learn more about CWUR methodology](https://cwur.org/methodology/world-university-rankings.php)
                                """)

                # If we have multiple years of data, show trend
                if len(rank_matches) > len(latest_rankings):
                    st.markdown("### Historical Ranking Trends")
                    viz.plot_ranking_trend(uni_data, rank_matches)
            else:
                st.info("No ranking data found for this university.")
        else:
            st.info("Ranking data is not available.")

    # Check if we should show the profile generation section
    if st.session_state.show_profile:
        # Create a comprehensive profile
        st.markdown("""
        <div style="border: 2px solid #1e88e5; border-radius: 8px; padding: 20px; margin: 20px 0; background-color: #e3f2fd;">
            <h2 style="color: #1e88e5; margin-top: 0;">📄 University Profile Generated</h2>
            <p>Your complete university profile is ready. Click the button below to download.</p>
        </div>
        """, unsafe_allow_html=True)

        # Create a comprehensive dataframe with all university data
        profile_data = pd.DataFrame([uni_data])

        # Add a timestamp to the filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{uni_data['INSTNM'].replace(' ', '_')}_profile_{timestamp}.csv"

        # Generate download link
        st.markdown(
            get_download_link(
                profile_data,
                filename,
                "📥 Download Complete University Profile (CSV)"
            ),
            unsafe_allow_html=True
        )

        # Add option to hide the profile section
        if st.button("Hide Profile"):
            st.session_state.show_profile = False
            st.rerun()

    # Add the Programs tab last
    # Create a new tab for Programs & Fields of Study
    if not fos_data.empty:
        # Filter field of study data for this university
        uni_fos = fos_data[fos_data['UNITID'] == unitid]

        if not uni_fos.empty:
            # Create a searchable program explorer
            st.markdown("### 📚 Programs & Fields of Study")

            # Group by credential level
            cred_levels = uni_fos['CREDLEV'].unique()

            # Create a dropdown to select credential level
            if len(cred_levels) > 1:
                selected_level = st.selectbox(
                    "Select Degree Level:",
                    options=sorted(cred_levels),
                    format_func=lambda x: uni_fos[uni_fos['CREDLEV'] == x]['CREDDESC'].iloc[0]
                )
            else:
                selected_level = cred_levels[0]

            # Get the level name
            level_name = uni_fos[uni_fos['CREDLEV'] == selected_level]['CREDDESC'].iloc[0]

            # Get programs for this credential level
            level_programs = uni_fos[uni_fos['CREDLEV'] == selected_level]

            # Add a search box for programs
            search_term = st.text_input("🔍 Search Programs:", placeholder="Type to search programs...")

            if search_term:
                # Filter programs by search term
                filtered_programs = level_programs[level_programs['CIPDESC'].str.contains(search_term, case=False, na=False)]
            else:
                filtered_programs = level_programs

            # Display program count
            st.markdown(f"**Found {len(filtered_programs)} {level_name} programs**")

            # Create a more interactive program display
            if not filtered_programs.empty:
                # Create a tabbed interface for program view options
                program_tabs = st.tabs(["Table View", "Earnings Comparison"])

                with program_tabs[0]:
                    # Display programs in a table
                    st.dataframe(
                        filtered_programs[['CIPCODE', 'CIPDESC', 'EARN_MDN_HI_1YR']],
                        use_container_width=True,
                        column_config={
                            "CIPCODE": st.column_config.TextColumn("CIP Code"),
                            "CIPDESC": st.column_config.TextColumn("Program"),
                            "EARN_MDN_HI_1YR": st.column_config.NumberColumn("Median Earnings (1yr)", format="$%d")
                        }
                    )

                with program_tabs[1]:
                    # Show earnings visualization
                    viz.plot_program_earnings(uni_data, fos_data, unitid, selected_level)
            else:
                st.info(f"No programs found matching '{search_term}'.")
        else:
            st.info("No program data found for this university.")
    else:
        st.info("Program data is not available.")
