"""
Data loading functions for the University Scout application.
"""

import streamlit as st
import pandas as pd
import numpy as np
from Pathfinder.config import (
    INSTITUTION_DATA_URL, RANKING_FILES, COLUMNS_TO_LOAD, NUMERIC_COLUMNS, STATE_NAMES
)

@st.cache_data
def load_institution_data(columns_to_load=None, numeric_columns=None, sample_fraction=0.5):
    """
    Loads the most recent institution-level data, selects specific columns, and cleans it.
    Optionally samples a fraction of universities to improve performance.

    Args:
        columns_to_load: List of columns to load from the CSV
        numeric_columns: List of columns to convert to numeric type
        sample_fraction: Fraction of universities to randomly sample (default: 0.5)

    Returns:
        DataFrame: Cleaned institution data
    """
    if columns_to_load is None:
        columns_to_load = COLUMNS_TO_LOAD

    if numeric_columns is None:
        numeric_columns = NUMERIC_COLUMNS

    try:
        df = pd.read_csv(INSTITUTION_DATA_URL, usecols=columns_to_load, low_memory=False)

        # Replace common null/suppressed values with NaN
        df = df.replace(['PrivacySuppressed', 'NULL'], np.nan, regex=True)

        # Convert specified columns to numeric, coercing errors to NaN
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Basic cleaning: Drop rows where essential identifiers are missing
        df.dropna(subset=['UNITID', 'INSTNM'], inplace=True)

        # Map CONTROL codes to meaningful labels
        control_mapping = {1: 'Public', 2: 'Private nonprofit', 3: 'Private for-profit'}
        if 'CONTROL' in df.columns:
            df['CONTROL_TYPE'] = df['CONTROL'].map(control_mapping).fillna('Unknown')

        # Add full state names
        if 'STABBR' in df.columns:
            df['STATE_NAME'] = df['STABBR'].map(STATE_NAMES).fillna(df['STABBR'])

        # Randomly sample a fraction of universities to improve performance
        if sample_fraction < 1.0:
            df = df.sample(frac=sample_fraction, random_state=42)
            st.info(f"Performance mode: Using a random sample of {int(sample_fraction*100)}% of universities.")

        return df
    except FileNotFoundError:
        st.error(f"Error: Institution data file not found at {INSTITUTION_DATA_URL}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"An error occurred during institution data loading: {e}")
        return pd.DataFrame()

@st.cache_data
def load_historical_data():
    """
    Loads and concatenates historical cohort data (recent years).

    Returns:
        DataFrame: Historical institution data
    """
    # Load only the most recent years to improve performance
    files_to_load = [
        "data/MERGED2020_21_PP.csv",
        "data/MERGED2021_22_PP.csv",
        "data/MERGED2022_23_PP.csv"
    ]
    # Optimized to match main data columns
    historical_cols = ['UNITID', 'INSTNM', 'STABBR', 'CONTROL', 'ADM_RATE',
                       'TUITIONFEE_IN', 'TUITIONFEE_OUT', 'SAT_AVG', 'C150_4']
    all_dfs = []
    for f in files_to_load:
        try:
            year_str = f.split('MERGED')[1].split('_')[0]  # Extract year like '2018'
            # Attempt to create a reliable year column (e.g., start year of the cohort)
            year = int(year_str[:4]) if year_str else None

            df = pd.read_csv(f, usecols=lambda c: c in historical_cols or c == 'YEAR', low_memory=False)
            # If YEAR column doesn't exist, add it based on filename
            if 'YEAR' not in df.columns and year is not None:
                df['YEAR'] = year
            elif 'YEAR' in df.columns:
                # Ensure YEAR is numeric if it exists
                df['YEAR'] = pd.to_numeric(df['YEAR'], errors='coerce')

            # Basic cleaning similar to main data
            df = df.replace(['PrivacySuppressed', 'NULL'], np.nan, regex=True)
            numeric_hist_cols = ['ADM_RATE', 'TUITIONFEE_IN', 'TUITIONFEE_OUT', 'SAT_AVG', 'C150_4']
            for col in numeric_hist_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            all_dfs.append(df)
        except FileNotFoundError:
            st.warning(f"Historical data file not found: {f}")
        except Exception as e:
            st.warning(f"Error loading historical file {f}: {e}")

    if not all_dfs:
        return pd.DataFrame()

    historical_data = pd.concat(all_dfs, ignore_index=True)
    historical_data.dropna(subset=['UNITID', 'YEAR'], inplace=True)  # Need UNITID and YEAR
    return historical_data

@st.cache_data
def load_field_of_study_data():
    """
    Loads and concatenates field of study data (most recent file).

    Returns:
        DataFrame: Field of study data
    """
    # Load only the most recent FoS file for now
    fos_file = "data/FieldOfStudyData1819_1920_PP.csv"
    # Optimized to include only essential columns
    fos_cols = ['UNITID', 'INSTNM', 'CIPCODE', 'CIPDESC', 'CREDLEV', 'CREDDESC',
                'EARN_MDN_HI_1YR']
    try:
        # Check which columns actually exist in the file
        available_cols = pd.read_csv(fos_file, nrows=0).columns.tolist()
        cols_to_use = [col for col in fos_cols if col in available_cols]

        df = pd.read_csv(fos_file, usecols=cols_to_use, low_memory=False)
        df = df.replace(['PrivacySuppressed', 'NULL'], np.nan, regex=True)

        numeric_fos_cols = ['EARN_MDN_HI_1YR']
        for col in numeric_fos_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        df.dropna(subset=['UNITID', 'CIPCODE', 'CREDLEV'], inplace=True)
        return df
    except FileNotFoundError:
        st.error(f"Field of Study data file not found: {fos_file}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"An error occurred loading Field of Study data: {e}")
        return pd.DataFrame()

@st.cache_data
def load_ranking_data():
    """
    Loads data from various ranking sources.
    Optimized to load only the most recent year for performance.

    Returns:
        DataFrame: Combined ranking data
    """
    # For performance optimization, we'll only load one ranking source
    try:
        # Load only the Times ranking data as it's most recognized
        times_df = pd.read_csv(RANKING_FILES['times'])

        # Select only essential columns
        times_df = times_df[['university_name', 'world_rank', 'year']].copy()

        # Filter for most recent year only
        max_year = times_df['year'].max()
        times_df = times_df[times_df['year'] == max_year]

        # Rename columns for consistency
        times_df.rename(columns={'university_name': 'institution_name'}, inplace=True)
        times_df['source'] = 'Times'

        # Clean rank data
        times_df['world_rank'] = times_df['world_rank'].astype(str).str.replace('=', '').str.split('-').str[0]
        times_df['world_rank'] = pd.to_numeric(times_df['world_rank'], errors='coerce')

        # Convert year to integer
        times_df['year'] = times_df['year'].astype(int)

        return times_df
    except Exception as e:
        st.warning(f"Error loading ranking data: {e}")
        return pd.DataFrame()
