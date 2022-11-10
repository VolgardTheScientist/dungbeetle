#%%

import pandas as pd
import ifcopenshell
from tools import ifchelper
from tools import pandashelper
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode
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

def df_with_location_data():
    df_loc = get_ifc_pandas()
    df_loc['Country']='Liechtenstein'
    df_loc['City']='Vaduz'
    df_loc['lat']='47.1410'
    df_loc['lon']='9.5209'
    df_loc.loc[0, ["lat"]] = '47.3904'
    df_loc.loc[0, ["lon"]] = '8.0457'
    df_loc.loc[0, ["Country"]] = 'Switzerland'
    df_loc.loc[0, ["City"]] = 'Aarau'
    df_loc['lat'] = df_loc['lat'].astype(float)
    df_loc['lon'] = df_loc['lon'].astype(float)
    return df_loc

def configured_aggrid():
    data = df_with_location_data()
    gb = GridOptionsBuilder.from_dataframe(data)
    gb.configure_pagination(paginationAutoPageSize=True) #Add pagination
    gb.configure_side_bar() #Add a sidebar
    #gb.configure_selection(selection_mode="multiple", use_checkbox=True)
    gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children") #Enable multi-row selection, but it crashes 
    gridOptions = gb.build()

    grid_response = AgGrid(
        data,
        gridOptions=gridOptions,
        data_return_mode='AS_INPUT', 
        update_mode='MODEL_CHANGED', 
        fit_columns_on_grid_load=False,
        enable_enterprise_modules=True,
        height=600, 
        width='100%',
        reload_data=False #it was originaly set to True, but then it casues the selection to disappear on multiselect, presumably with False data is not being sent back to streamlit... - review this https://pablocfonseca-streamlit-aggrid-examples-example-jyosi3.streamlit.app/
    )

    data = grid_response['data']
    selected = grid_response['selected_rows'] 
    df = pd.DataFrame(selected) #Pass the selected rows to a new dataframe df
    return df #Ta linijka ode mnie, ale nie pomogla

def execute():
    st.title("D4D Material Bank")
    st.write(
        """This is the initial attempt to parse IFC files with ifcOpenShell and display the content through Streamlit GUI interface and Pandas DataFrame
        Follow below guide for setting it up: [here](<https://blog.streamlit.io/auto-generate-a-dataframe-filtering-ui-in-streamlit-with-filter_dataframe/>)
        """
)
    st.header("Dataframe Review")
    session["Dataframe"] = df_with_location_data()
    df = df_with_location_data()
    configured_aggrid()
    st.map(df)    
    
execute()






