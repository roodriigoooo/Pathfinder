"""
Utility functions for the University Scout application.
"""

import streamlit as st
import pandas as pd
import io
import base64
from datetime import datetime

# Try to import kaleido, but don't fail if it's not available
try:
    import kaleido
    KALEIDO_AVAILABLE = True
except ImportError:
    KALEIDO_AVAILABLE = False

def get_download_link(df, filename, link_text):
    """
    Generates a link to download the provided dataframe as a CSV file.

    Args:
        df: DataFrame to download
        filename: Name of the file to download
        link_text: Text to display for the download link

    Returns:
        str: HTML link for downloading the CSV
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{link_text}</a>'
    return href

def get_figure_download_link(fig, filename, link_text):
    """
    Generates a link to download the provided plotly figure as a PNG image.
    Silently falls back to a non-functional link if Kaleido is not available.

    Args:
        fig: Plotly figure to download
        filename: Name of the file to download
        link_text: Text to display for the download link

    Returns:
        str: HTML link for downloading the PNG or a styled link if not available
    """
    if not KALEIDO_AVAILABLE:
        # Silently return a styled link without warning
        return f'<span style="color: #ff9800; cursor: not-allowed;" title="Image download requires kaleido package">{link_text}</span>'

    try:
        buf = io.BytesIO()
        fig.write_image(buf, format="png", width=1200, height=800)
        buf.seek(0)
        b64 = base64.b64encode(buf.read()).decode()
        href = f'<a href="data:image/png;base64,{b64}" download="{filename}">{link_text}</a>'
        return href
    except Exception as e:
        # Silently handle errors without warnings
        return f'<span style="color: #ff9800; cursor: not-allowed;" title="Error: {str(e)}">{link_text}</span>'

def initialize_session_state():
    """
    Initialize session state variables if they don't exist.
    """
    if 'selected_universities' not in st.session_state:
        st.session_state.selected_universities = []

    if 'shortlisted_universities' not in st.session_state:
        st.session_state.shortlisted_universities = []

    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = "Explore"

    if 'selected_university_id' not in st.session_state:
        st.session_state.selected_university_id = None

    if 'comparison_universities' not in st.session_state:
        st.session_state.comparison_universities = []

    if 'view_mode' not in st.session_state:
        st.session_state.view_mode = "Card View"

def add_to_shortlist(unitid):
    """
    Add a university to the shortlist.

    Args:
        unitid: University ID to add to shortlist
    """
    if unitid not in st.session_state.shortlisted_universities:
        st.session_state.shortlisted_universities.append(unitid)

def remove_from_shortlist(unitid):
    """
    Remove a university from the shortlist.

    Args:
        unitid: University ID to remove from shortlist
    """
    if unitid in st.session_state.shortlisted_universities:
        st.session_state.shortlisted_universities.remove(unitid)

def toggle_university_selection(unitid):
    """
    Toggle a university's selection status for comparison.

    Args:
        unitid: University ID to toggle selection
    """
    if unitid in st.session_state.selected_universities:
        st.session_state.selected_universities.remove(unitid)
    else:
        st.session_state.selected_universities.append(unitid)

def set_active_tab(tab_name):
    """
    Set the active tab in the application.

    Args:
        tab_name: Name of the tab to activate
    """
    st.session_state.active_tab = tab_name

def set_selected_university(unitid):
    """
    Set the selected university for detailed view.

    Args:
        unitid: University ID to select
    """
    st.session_state.selected_university_id = unitid
    st.session_state.active_tab = "Details"

def clear_shortlist():
    """Clear the shortlist of universities."""
    st.session_state.shortlisted_universities = []

def clear_comparison():
    """Clear the comparison list of universities."""
    st.session_state.selected_universities = []

def generate_timestamp():
    """
    Generate a timestamp string for filenames.

    Returns:
        str: Current timestamp in YYYYMMDD_HHMMSS format
    """
    return datetime.now().strftime('%Y%m%d_%H%M%S')

def apply_custom_css():
    """Apply custom CSS styling to the application."""
    st.markdown("""
    <style>
        /* Main container styling */
        .main .block-container {
            padding-top: 2rem;
            background-color: white;
            color: #333;
        }

        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
        }
        .stTabs [data-baseweb="tab"] {
            height: 3rem;
            white-space: pre-wrap;
            border-radius: 4px 4px 0px 0px;
            padding: 0rem 1rem;
            font-size: 1rem;
            background-color: white;
        }
        /* Active tab */
        .stTabs [aria-selected="true"] {
            background-color: white;
            border-bottom: 2px solid #1e88e5;
            font-weight: bold;
        }

        /* Streamlit info box */
        .stAlert {
            border-radius: 4px;
            background-color: white;
            border: 1px solid #e0e0e0;
        }

        /* Card styling */
        .card {
            border-radius: 8px;
            padding: 1.5rem;
            background-color: white;
            border: 1px solid #e0e0e0;
            margin-bottom: 1rem;
        }

        /* Sidebar section styling */
        .sidebar-section {
            background-color: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
        }

        /* University card styling */
        .uni-card {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
            transition: all 0.3s;
            background-color: white;
        }
        .uni-card:hover {
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            transform: translateY(-2px);
        }

        /* Text colors */
        h1, h2, h3, h4, h5, h6, p, span, div {
            color: #333;
        }

        /* Link styling */
        a {
            color: #1e88e5;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }

        /* Button styling */
        .stButton button {
            background-color: white;
            border: 1px solid #e0e0e0;
            color: #333;
        }
        .stButton button:hover {
            border-color: #1e88e5;
        }

        /* Hide hamburger menu and footer */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}

        /* Data editor styling */
        .stDataFrame {
            background-color: white;
        }

        /* Metric styling */
        .stMetric {
            background-color: white;
        }
    </style>
    """, unsafe_allow_html=True)
