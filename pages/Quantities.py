from tools import ifchelper
from tools import pandashelper
import streamlit as st

session = st.session_state

def get_ifc_pandas():
    data, pset_attributes = ifchelper.get_objects_data_by_class(
        session.ifc_file,
        "IfcBuildingElement"
    )
    frame = ifchelper.create_pandas_dataframe(data, pset_attributes)
    return frame

def download_csv():
    pandashelper.download_csv(session.file_name, session.DataFrame)

def execute():
    st.title( "Model Quantities")
    tab1, tab2 = st.tabs(["Dataframe utilities", "Quantites Review"])

    with tab1:
        st.header("DataFrame Review")
        session["DataFrame"] = get_ifc_pandas()
        st.write(session["DataFrame"])
        st.button("Download CSV", key="download_csv", on_click=download_csv())
execute()


