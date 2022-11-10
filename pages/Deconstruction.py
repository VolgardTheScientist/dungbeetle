#%%

import pandas as pd
import ifcopenshell
from tools import ifchelper
from tools import pandashelper
import streamlit as st
import streamlit.components.v1 as components
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)

session = st.session_state

@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

def get_ifc_pandas():
    data, pset_attributes = ifchelper.get_objects_data_by_class(
        session.ifc_file,
        "IfcBuildingElement"
    )
    df = ifchelper.create_pandas_dataframe(data, pset_attributes)
    return df


def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """
    modify = st.checkbox("Add filters")

    if not modify:
        return df

    df = df.copy()

    # Try to convert datetimes into a standard format (datetime, no timezone)
    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass

        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect("Filter dataframe on", df.columns)
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            # Treat columns with < 10 unique values as categorical
            if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                user_cat_input = right.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f"Values for {column}",
                    min_value=_min,
                    max_value=_max,
                    value=(_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"Values for {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                user_text_input = right.text_input(
                    f"Substring or regex in {column}",
                )
                if user_text_input:
                    df = df[df[column].astype(str).str.contains(user_text_input)]

    return df

def execute():
    st.title("D4D Material Bank")
    st.write(
        """This is the initial attempt to parse IFC files with ifcOpenShell and display the content through Streamlit GUI interface and Pandas DataFrame
        Follow below guide for setting it up: [here](<https://blog.streamlit.io/auto-generate-a-dataframe-filtering-ui-in-streamlit-with-filter_dataframe/>)
        """
)
    st.header("Dataframe Review")
    session["Dataframe"] = get_ifc_pandas()
    df = get_ifc_pandas()
    df['Country']='Liechtenstein'
    df['City']='Vaduz'
    df['lat']='47.1410'
    df['lon']='9.5209'
    df.loc[0, ["lat"]] = '47.3904'
    df.loc[0, ["lon"]] = '8.0457'
    df.loc[0, ["Country"]] = 'Switzerland'
    df.loc[0, ["City"]] = 'Aarau'
    df['lat'] = df['lat'].astype(float)
    df['lon'] = df['lon'].astype(float)
    st.dataframe(filter_dataframe(df))
    st.download_button(label="Download data as CSV", data=convert_df(df), file_name=(session.file_name +".csv"), mime='text/csv')
    st.map(df)
execute()






