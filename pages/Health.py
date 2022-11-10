from tools import ifchelper
from tools import graph_maker
import streamlit as st

session = st.session_state

def load_data():
    if "ifc_file" in session:
        session["Graphs"] = {
            "Objects_graph": graph_maker.get_elements_graph(session.ifc_file),
            "High_frequencies_graph": graph_maker.get_high_frequency_entities_graph(session.ifc_file),
        }
        load_work_schedules()
        load_cost_schedules()

def load_work_schedules():
    session["SequenceData"] = {
        "schedules": session.ifc_file.by_type("IfcWorkSchedule"),
        "tasks": session.ifc_file.by_type("IfcTask")
    }

def load_cost_schedules():
    session["CostData"] = {
        "schedules": session.ifc_file.by_type("IfcCostSchedule"),
        "costs": session.ifc_file.by_type("IfcCostItem")
    }

def draw_model_health_ui():
    col1, col2 = st.columns(2)
    with col1:
        st.write(session.Graphs["Objects_graph"])
    with col2:
        st.write(session.Graphs["High_frequencies_graph"])

    col1, col2 = st.columns(2)
    with col1:
        st.write("Work schedule")
        number_of_schedules = len(session.SequenceData["schedules"])
        st.write(f'Number of schedules: {number_of_schedules}')
        schedules = [f'{work_schedule.Name} / {work_schedule.id()}' for work_schedule in session.SequenceData["schedules"] or []]
        st.selectbox("Schedules", options = schedules, key = "work_schedule_selector")
        schedule_id = int(session.work_schedule_selector.split("/", 1)[1] if session.work_schedule_selector else None)
        st.write(schedule_id)
        if schedule_id:
            schedule = session.ifc_file.by_id(schedule_id)
            tasks = ifchelper.get_schedule_tasks(schedule)
            if tasks: 
                st.info(f'Number of tasks {len(tasks)}')
                task_data = ifchelper.get_task_data(tasks)
                st.table(task_data)
                st.write(type(task_data))
            else:
                st.warning("No tasks, c'mon, what were you doing all day? Get my tasks scheduled!")
    with col2:
        st.write("Cost schedule")
        number_of_cost_schedules = len(session.CostData["schedules"])
        st.write(f'Number of schedules: {number_of_cost_schedules}')
        st.selectbox("Schedules", options = [], key = "cost_schedule_selector")
        

def draw_side_bar():
        pass

def execute():
    st.title("Model health")
    load_data()
    draw_model_health_ui()
    draw_side_bar()
    load_work_schedules() 

execute()
