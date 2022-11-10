import streamlit as st
import ifcopenshell

session = st.session_state

def callback_upload():
    st.session_state["file_name"] = st.session_state["uploaded_file"].name
    st.session_state["is_file_uploaded"] = True
    st.session_state["array_buffer"] = st.session_state["uploaded_file"].getvalue()
    st.session_state["ifc_file"] = ifcopenshell.file.from_string(st.session_state["uploaded_file"].getvalue().decode("utf-8"))

def get_project_name():
    return st.session_state["ifc_file"].by_type("IfcProject")[0].Name

def change_project_name():
    st.session_state["ifc_file"].by_type("IfcProject")[0].Name = st.session_state["project_name_input"]

def main():      
    st.set_page_config(
        layout= "wide",
        page_title="IFC Stream",
        page_icon="✍️",
    )
    st.title("Streamlit IFC")
    st.markdown(
        """
        ### Click on Browse file to begin
        """
    )
    uploaded_file = st.sidebar.file_uploader("Choose a file", type="ifc", key="uploaded_file", on_change=callback_upload)

    # don't get why is there the part after and below...

    if "is_file_uploaded" in st.session_state and st.session_state["is_file_uploaded"]:
        st.sidebar.success("File is loaded")
        st.sidebar.write ("Your project is ready to be reviewed. Reduce, reuse, recycle, recover. ♺")

        col1, col2 = st.columns(2)
        with col1:
            st.write(get_project_name())
        with col2: 
            st.sidebar.text_input("✏️ Change project name below", key = "project_name_input", on_change=change_project_name)
            st.sidebar.button("Apply",  key = "project_name_apply", on_click=change_project_name)
            

    "Check session state", st.session_state

if __name__ == "__main__":
    main()