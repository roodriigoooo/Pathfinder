"""
University details view for the Pathfinder application.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from utils import (
    get_download_link, add_to_shortlist, remove_from_shortlist,
    toggle_university_selection, set_active_tab
)
import ui.visualizations as viz

def display_university_details(unitid, inst_data, hist_data, fos_data):
    """
    Displays detailed information for a selected university.
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
    detail_tabs = st.tabs(["📊 Overview", "🎓 Academics", "💰 Finances", "🌈 Campus Life", "📈 Outcomes"])

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
            # Use the reusable function for admission rate card and for all other cards
            viz.plot_admission_rate_card(uni_data, key_prefix="details")

            viz.plot_test_policy_card(uni_data, key_prefix="details")

        with score_col2:
            viz.plot_sat_score_card(uni_data, key_prefix="details")

        with score_col3:
            viz.plot_act_score_card(uni_data, key_prefix="details")

        viz.plot_test_scores_trend(uni_data, hist_data, unitid)

        viz.plot_admission_trend(uni_data, hist_data, unitid)

    # Finances Tab
    with detail_tabs[2]:
        st.markdown("### 💰 Cost & Financial Aid")

        # Net price visualization
        viz.plot_net_price(uni_data)

        # Historical tuition trend - moved here to be right after net price
        st.markdown("### Historical Tuition Trends")
        viz.plot_tuition_trend(uni_data, hist_data, unitid)

        # Create a visually appealing cost comparison with cards instead of bars
        st.subheader("Annual Tuition")

        # Create two columns for the tuition cards
        tuition_col1, tuition_col2 = st.columns(2)

        with tuition_col1:
            # In-state tuition card
            if pd.notna(uni_data['TUITIONFEE_IN']):
                in_state = int(uni_data['TUITIONFEE_IN'])
                st.markdown(f"""
                <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 20px; background-color: white; text-align: center; height: 100%;">
                    <h4 style="margin-top: 0; color: #333;">In-State Tuition</h4>
                    <p style="font-size: 32px; font-weight: bold; margin: 15px 0; color: #7C9A83;">${in_state:,}</p>
                    <p style="color: #666;">Annual cost for state residents</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 20px; background-color: white; text-align: center; height: 100%;">
                    <h4 style="margin-top: 0; color: #333;">In-State Tuition</h4>
                    <p style="font-size: 32px; font-weight: bold; margin: 15px 0; color: #333;">N/A</p>
                    <p style="color: #666;">Annual cost for state residents</p>
                </div>
                """, unsafe_allow_html=True)

        with tuition_col2:
            # Out-of-state tuition card
            if pd.notna(uni_data['TUITIONFEE_OUT']):
                out_state = int(uni_data['TUITIONFEE_OUT'])
                st.markdown(f"""
                <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 20px; background-color: white; text-align: center; height: 100%;">
                    <h4 style="margin-top: 0; color: #333;">Out-of-State Tuition</h4>
                    <p style="font-size: 32px; font-weight: bold; margin: 15px 0; color: #5B6ABF;">${out_state:,}</p>
                    <p style="color: #666;">Annual cost for non-residents</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 20px; background-color: white; text-align: center; height: 100%;">
                    <h4 style="margin-top: 0; color: #333;">Out-of-State Tuition</h4>
                    <p style="font-size: 32px; font-weight: bold; margin: 15px 0; color: #333;">N/A</p>
                    <p style="color: #666;">Annual cost for non-residents</p>
                </div>
                """, unsafe_allow_html=True)

        # Enhanced debt visualizations
        st.subheader("Student Debt")

        if 'DEBT_MDN' in uni_data and pd.notna(uni_data['DEBT_MDN']):
            debt = int(uni_data['DEBT_MDN'])

            # Determine debt level with neutral colors
            if debt < 20000:
                debt_level = "Low"
                color = "#5B6ABF"  # Muted blue-purple
            elif debt < 30000:
                debt_level = "Moderate"
                color = "#6B8E9F"  # Muted blue-gray
            elif debt < 40000:
                debt_level = "High"
                color = "#7C9A83"  # Muted green-gray
            else:
                debt_level = "Very High"
                color = "#8E9C6B"  # Muted olive

            st.markdown(f"""
            <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 20px; margin-bottom: 20px; background-color: white; text-align: center;">
                <h3 style="margin-top: 0; color: #333;">Median Student Debt</h3>
                <p style="font-size: 32px; font-weight: bold; margin: 15px 0; color: {color};">${debt:,}</p>
                <p style="color: {color}; font-weight: bold;">{debt_level} Debt Level</p>
                <p style="color: #666; font-size: 14px; margin-top: 10px;">Median federal loan debt accumulated at the institution by student borrowers who separate (either graduate or withdraw), measured at the point of separation.</p>
            </div>
            """, unsafe_allow_html=True)

            # Show detailed debt breakdown by category
            viz.plot_detailed_debt(uni_data)

            # Show historical debt trends if available
            viz.plot_debt_comparison(uni_data, hist_data, unitid)

        else:
            st.markdown("""
            <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 20px; margin-bottom: 20px; background-color: white; text-align: center;">
                <h3 style="margin-top: 0; color: #333;">Median Student Debt</h3>
                <p style="font-size: 32px; font-weight: bold; margin: 15px 0; color: #333;">N/A</p>
                <p style="color: #666; font-size: 14px; margin-top: 10px;">Debt information not available for this institution</p>
            </div>
            """, unsafe_allow_html=True)

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

        # Create tabs for different diversity visualizations
        diversity_tabs = st.tabs(["Student Diversity", "Staff Diversity", "Gender Distribution"])

        # Student Diversity Tab
        with diversity_tabs[0]:
            diversity_cols = ['UGDS_WHITE', 'UGDS_BLACK', 'UGDS_HISP', 'UGDS_ASIAN',
                            'UGDS_AIAN', 'UGDS_NHPI', 'UGDS_2MOR', 'UGDS_NRA', 'UGDS_UNKN']
            has_diversity_data = any(col in uni_data.index for col in diversity_cols)

            if has_diversity_data:
                # Create a more interactive diversity visualization
                viz.diversity.plot_diversity_pie(uni_data)
            else:
                st.info("Student diversity data not available for this university.")

        # Staff Diversity Tab
        with diversity_tabs[1]:
            # Display staff diversity pie chart
            staff_diversity_cols = ['IRPS_WHITE', 'IRPS_BLACK', 'IRPS_HISP', 'IRPS_ASIAN',
                                   'IRPS_AIAN', 'IRPS_NHPI', 'IRPS_2MOR', 'IRPS_NRA', 'IRPS_UNKN']
            has_staff_diversity = any(col in uni_data.index for col in staff_diversity_cols) and any(pd.notna(uni_data[col]) for col in staff_diversity_cols if col in uni_data.index)

            if has_staff_diversity:
                viz.diversity.plot_staff_diversity_pie(uni_data)
            else:
                st.info("Staff diversity data not available for this university.")

        # Gender Distribution Tab
        with diversity_tabs[2]:
            # Display gender pie charts
            student_gender_cols = ['UGDS_MEN', 'UGDS_WOMEN']
            staff_gender_cols = ['IRPS_MEN', 'IRPS_WOMEN']

            has_student_gender = all(col in uni_data.index for col in student_gender_cols) and any(pd.notna(uni_data[col]) for col in student_gender_cols)
            has_staff_gender = all(col in uni_data.index for col in staff_gender_cols) and any(pd.notna(uni_data[col]) for col in staff_gender_cols)

            if has_student_gender or has_staff_gender:
                viz.diversity.plot_gender_pie(uni_data)
            else:
                st.info("Gender distribution data not available for this university.")

    # Outcomes Tab
    with detail_tabs[4]:
        st.markdown("### 📈 Outcomes & Career Success")

        # Create a two-column layout
        outcome_col1, outcome_col2 = st.columns(2)

        with outcome_col1:
            # Use the reusable function for graduation rate card
            viz.outcomes.plot_graduation_rate_card(uni_data, key_prefix="details")

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
        viz.outcomes.plot_graduation_trend(uni_data, hist_data, unitid)

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

