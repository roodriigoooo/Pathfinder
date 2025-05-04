"""
Sidebar filter components for the University Scout application.
"""

import streamlit as st
import pandas as pd
from config import STATE_NAMES

def display_sidebar_filters(df):
    """
    Displays sidebar filters and returns selected values.

    Args:
        df: DataFrame containing university data

    Returns:
        dict: Dictionary of selected filter values
    """
    st.sidebar.header("🔍 Filter Universities")

    # Create collapsible sections for filters with emojis
    with st.sidebar.expander("📍 Location Filters", expanded=True):
        # State Filter with full state names
        states_abbr = sorted(df['STABBR'].dropna().unique())
        states_full = [f"{STATE_NAMES.get(state, state)} ({state})" for state in states_abbr]

        # Create a mapping from display name to abbreviation
        state_display_to_abbr = {f"{STATE_NAMES.get(state, state)} ({state})": state for state in states_abbr}

        selected_states_full = st.multiselect(
            "State/Territory",
            states_full,
            default=states_full
        )

        # Convert selected full names back to abbreviations
        selected_states = [state_display_to_abbr[state] for state in selected_states_full]

    with st.sidebar.expander("🏫 Institution Type", expanded=True):
        # Control Type Filter
        control_types = sorted(df['CONTROL_TYPE'].dropna().unique())
        selected_control_types = st.multiselect("Control Type", control_types, default=control_types)

    with st.sidebar.expander("🎓 Admissions", expanded=True):
        # Admission Rate Filter
        min_adm_rate = 0.0
        max_adm_rate = 1.0
        if 'ADM_RATE' in df.columns and df['ADM_RATE'].notna().any():
            min_adm_rate_data = df['ADM_RATE'].min()
            max_adm_rate_data = df['ADM_RATE'].max()
            if pd.notna(min_adm_rate_data) and pd.notna(max_adm_rate_data):
                min_adm_rate = float(min_adm_rate_data)
                max_adm_rate = float(max_adm_rate_data)

        selected_adm_rate = st.slider(
            "Admission Rate",
            min_value=min_adm_rate,
            max_value=max_adm_rate,
            value=(min_adm_rate, max_adm_rate),
            format="%.3f"
        )

        # SAT Score Filter (if available)
        if 'SAT_AVG' in df.columns and df['SAT_AVG'].notna().any():
            min_sat = int(df['SAT_AVG'].min())
            max_sat = int(df['SAT_AVG'].max())
            selected_sat = st.slider(
                "Average SAT Score",
                min_value=min_sat,
                max_value=max_sat,
                value=(min_sat, max_sat)
            )
        else:
            selected_sat = None

    with st.sidebar.expander("💰 Cost & Financial", expanded=False):
        # Tuition Filter (if available)
        if 'TUITIONFEE_IN' in df.columns and df['TUITIONFEE_IN'].notna().any():
            min_tuition = int(df['TUITIONFEE_IN'].min())
            max_tuition = int(df['TUITIONFEE_IN'].max())
            selected_tuition = st.slider(
                "In-State Tuition ($)",
                min_value=min_tuition,
                max_value=max_tuition,
                value=(min_tuition, max_tuition)
            )
        else:
            selected_tuition = None

    with st.sidebar.expander("📈 Outcomes", expanded=False):
        # Graduation Rate Filter (if available)
        if 'C150_4' in df.columns and df['C150_4'].notna().any():
            min_grad = float(df['C150_4'].min())
            max_grad = float(df['C150_4'].max())
            selected_grad = st.slider(
                "4-Year Graduation Rate",
                min_value=min_grad,
                max_value=max_grad,
                value=(min_grad, max_grad),
                format="%.2f"
            )
        else:
            selected_grad = None

    # Return all selected filter values
    return {
        "states": selected_states,
        "control_types": selected_control_types,
        "adm_rate": selected_adm_rate,
        "sat": selected_sat,
        "tuition": selected_tuition,
        "grad_rate": selected_grad
    }
