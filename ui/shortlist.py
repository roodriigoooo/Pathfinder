"""
Shortlist management for the University Scout application.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from utils import get_download_link, get_figure_download_link, clear_shortlist, set_selected_university

def display_shortlist(data, historical_data, fos_data, ranking_data):
    """
    Displays the shortlisted universities.

    Args:
        data: DataFrame containing institution data
        historical_data: DataFrame containing historical data
        fos_data: DataFrame containing field of study data
        ranking_data: DataFrame containing ranking data

    Returns:
        None: Displays content directly using streamlit
    """
    st.header("📋 My Shortlisted Universities")

    if 'shortlisted_universities' in st.session_state and st.session_state.shortlisted_universities:
        shortlist_df = data[data['UNITID'].isin(st.session_state.shortlisted_universities)].copy()

        st.write(f"You have {len(shortlist_df)} universities in your shortlist")

        # Display shortlisted universities
        st.dataframe(
            shortlist_df[['INSTNM', 'CITY', 'STATE_NAME', 'CONTROL_TYPE', 'ADM_RATE', 'SAT_AVG', 'TUITIONFEE_IN', 'C150_4']],
            column_config={
                "INSTNM": "University",
                "CITY": "City",
                "STATE_NAME": "State",
                "CONTROL_TYPE": "Type",
                "ADM_RATE": st.column_config.NumberColumn("Admission Rate", format="%.1f%%"),
                "SAT_AVG": "Avg SAT",
                "TUITIONFEE_IN": st.column_config.NumberColumn("In-State Tuition", format="$%d"),
                "C150_4": st.column_config.NumberColumn("Graduation Rate", format="%.1f%%")
            },
            use_container_width=True,
            hide_index=True
        )

        # Action buttons
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("⚖️ Compare All Shortlisted", key="compare_all_shortlisted"):
                st.session_state.selected_universities = st.session_state.shortlisted_universities.copy()
                st.session_state.active_tab = "Compare"
                st.rerun()

        with col2:
            if st.button("🗑️ Clear Shortlist", key="clear_shortlist"):
                clear_shortlist()
                st.rerun()

        with col3:
            st.markdown(
                get_download_link(
                    shortlist_df,
                    f"my_shortlisted_universities_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    "📥 Download Shortlist"
                ),
                unsafe_allow_html=True
            )

        # Display visualizations of shortlisted universities
        st.subheader("📊 Shortlist Overview")

        # Admission Rate vs. SAT Score scatter plot
        if 'ADM_RATE' in shortlist_df.columns and 'SAT_AVG' in shortlist_df.columns:
            plot_data = shortlist_df.dropna(subset=['ADM_RATE', 'SAT_AVG'])
            if not plot_data.empty:
                fig = px.scatter(
                    plot_data,
                    x='ADM_RATE',
                    y='SAT_AVG',
                    color='CONTROL_TYPE',
                    hover_name='INSTNM',
                    title="Selectivity of Shortlisted Universities",
                    labels={'ADM_RATE': 'Admission Rate', 'SAT_AVG': 'Average SAT Score', 'CONTROL_TYPE': 'Type'}
                )
                fig.update_layout(xaxis_tickformat=".0%")
                st.plotly_chart(fig, use_container_width=True)

                # Add download option for the chart
                st.markdown(
                    get_figure_download_link(
                        fig,
                        f"shortlist_selectivity_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                        "📥 Download Chart"
                    ),
                    unsafe_allow_html=True
                )

        # Display individual university cards for quick access
        st.subheader("🏫 Quick Access to Shortlisted Universities")

        # Create a grid layout for cards
        cols = st.columns(3)

        for i, (_, uni) in enumerate(shortlist_df.iterrows()):
            with cols[i % 3]:
                # Create a card for each university
                st.markdown(f"""
                <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 1rem; text-align: center; margin-bottom: 1rem;">
                    <h4>{uni['INSTNM']}</h4>
                    <p>{uni['CITY']}, {uni['STATE_NAME']} • {uni['CONTROL_TYPE']}</p>
                </div>
                """, unsafe_allow_html=True)

                # View details button
                if st.button(f"View Details", key=f"shortlist_view_{uni['UNITID']}"):
                    set_selected_university(uni['UNITID'])
                    st.rerun()
    else:
        st.info("""
        Your shortlist is empty. Add universities to your shortlist by:
        - Using the "Shortlist" checkbox in the Explore tab and clicking "Apply Changes"
        - Clicking the "Add to Shortlist" button on university details pages
        - Adding universities from your Find My Fit matches
        """)

        # Add a button to go to the Explore tab
        if st.button("🔍 Go to Explore Universities", key="go_to_explore_from_shortlist"):
            st.session_state.active_tab = "Explore"
            st.rerun()
