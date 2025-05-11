"""
Data loading functions for the University Scout application.
"""

import streamlit as st
import pandas as pd
import numpy as np
from config import (
    INSTITUTION_DATA_URL, COLUMNS_TO_LOAD, NUMERIC_COLUMNS, STATE_NAMES
)

@st.cache_data
def load_institution_data(columns_to_load=None, numeric_columns=None):
    """
    Loads the most recent institution-level data, selects specific columns, and cleans it.
    """
    if columns_to_load is None:
        columns_to_load = COLUMNS_TO_LOAD

    if numeric_columns is None:
        numeric_columns = NUMERIC_COLUMNS

    try:
        df = pd.read_parquet(INSTITUTION_DATA_URL, columns=columns_to_load)

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
    """
    # Load data from 2015-16 onwards for better historical trends
    files_to_load = [
        "data/MERGED2015_16_PP.parquet",
        "data/MERGED2016_17_PP.parquet",
        "data/MERGED2017_18_PP.parquet",
        "data/MERGED2018_19_PP.parquet",
        "data/MERGED2019_20_PP.parquet",
        "data/MERGED2020_21_PP.parquet",
        "data/MERGED2021_22_PP.parquet",
        "data/MERGED2022_23_PP.parquet"
    ]
    # Enhanced to include more metrics for trend analysis
    historical_cols = [
        'UNITID', 'INSTNM', 'STABBR', 'CONTROL',
        'ADM_RATE', 'TUITIONFEE_IN', 'TUITIONFEE_OUT',
        'SAT_AVG', 'ACTCMMID', 'C150_4', 'UGDS',
        # Student debt information
        'DEBT_MDN', 'GRAD_DEBT_MDN', 'WDRAW_DEBT_MDN',
        'FEMALE_DEBT_MDN', 'MALE_DEBT_MDN',
        'FIRSTGEN_DEBT_MDN', 'NOTFIRSTGEN_DEBT_MDN',
        # Student diversity columns
        'UGDS_WHITE', 'UGDS_BLACK', 'UGDS_HISP', 'UGDS_ASIAN',
        'UGDS_AIAN', 'UGDS_NHPI', 'UGDS_2MOR', 'UGDS_NRA', 'UGDS_UNKN',
        # Gender columns
        'UGDS_MEN', 'UGDS_WOMEN'
    ]
    all_dfs = []
    for f in files_to_load:
        try:
            year_str = f.split('MERGED')[1].split('_')[0]  # Extract year like '2018'
            # Attempt to create a reliable year column (e.g., start year of the cohort)
            year = int(year_str[:4]) if year_str else None

            # Read only the columns we need
            columns_to_read = [col for col in historical_cols if col != 'YEAR'] + ['YEAR'] if 'YEAR' in pd.read_parquet(f, columns=None).columns else [col for col in historical_cols if col != 'YEAR']
            df = pd.read_parquet(f, columns=columns_to_read)

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
    """
    # Load only the most recent FoS file for now
    fos_file = "data/FieldOfStudyData1819_1920_PP.parquet"
    # Optimized to include only essential columns
    fos_cols = ['UNITID', 'INSTNM', 'CIPCODE', 'CIPDESC', 'CREDLEV', 'CREDDESC',
                'EARN_MDN_HI_1YR']
    try:
        # Check which columns actually exist in the file
        available_cols = pd.read_parquet(fos_file, columns=None).columns.tolist()
        cols_to_use = [col for col in fos_cols if col in available_cols]

        df = pd.read_parquet(fos_file, columns=cols_to_use)
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


