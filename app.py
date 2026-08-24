import math
import json
import os
import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="GH Labor Planner", layout="wide")

# --- ULTRA-COMPACT CSS STYLING & INTERACTIVE MAP ---
st.markdown("""
    <style>
        .block-container {
            padding-top: 0.8rem;
            padding-bottom: 0.5rem;
            padding-left: 0.8rem;
            padding-right: 0.8rem;
        }
        hr {
            margin-top: 0.3rem;
            margin-bottom: 0.3rem;
        }
        .stMultiSelect {
            margin-bottom: -1.2rem;
        }
        h1 {
            font-size: 1.6rem !important;
            margin-bottom: 0.2rem !important;
        }
        h2, h3 {
            font-size: 1.1rem !important;
            margin-top: 0.2rem !important;
            margin-bottom: 0.2rem !important;
        }
        p, label, span, div {
            font-size: 0.85rem !important;
        }
        .stNumberInput, .stDateInput {
            margin-bottom: -0.5rem;
        }
        .footer-watermark {
            text-align: center;
            font-size: 0.7rem;
            color: #888888;
            margin-top: 1rem;
            margin-bottom: 0.5rem;
            border-top: 1px solid #333;
            padding-top: 0.3rem;
        }
    </style>
""", unsafe_allow_html=True)

STAFF_FILE = "staff_data.json"
TASK_FILE = "task_data.json"
ASSIGNMENT_FILE = "assignment_data.json"
PARAMS_FILE = "params_data.json"
MAP_FILE = "map_data.json"

DEFAULT_STAFF = [
    {"name": "Marie", "category": "GG"}, {"name": "Kid", "category": "GG"}, {"name": "Ting", "category": "GG"}, {"name": "Tommy", "category": "GG"}, {"name": "Risa", "category": "GG"},
    {"name": "Rebecca", "category": "Leading Hand"}, {"name": "Rene", "category": "Leading Hand"}, {"name": "Tico", "category": "Leading Hand"},
    {"name": "Alfredo", "category": "TOTC"}, {"name": "Enock", "category": "TOTC"}, {"name": "Dick", "category": "TOTC"}, {"name": "Dan", "category": "TOTC"}, {"name": "Will", "category": "TOTC"}, {"name": "Terry", "category": "TOTC"},
    {"name": "Nikki", "category": "Urson"}, {"name": "Bina", "category": "Urson"}, {"name": "Tiara", "category": "Urson"}, {"name": "Shisir", "category": "Urson"}, {"name": "Jimmy", "category": "Urson"}, {"name": "Chandra", "category": "Urson"}, {"name": "Malick", "category": "Urson"}, {"name": "Audrey", "category": "Urson"}, {"name": "Han", "category": "Urson"}, {"name": "Rosie", "category": "Urson"}, {"name": "Dhia", "category": "Urson"}, {"name": "Hui", "category": "Urson"}, {"name": "Erica", "category": "Urson"}, {"name": "Lin", "category": "Urson"}, {"name": "Moka", "category": "Urson"}, {"name": "Panyawat", "category": "Urson"}, {"name": "AkashDeep", "category": "Urson"}, {"name": "Zakia", "category": "Urson"}, {"name": "Supakit", "category": "Urson"}, {"name": "Camie", "category": "Urson"}, {"name": "Fierda", "category": "Urson"}, {"name": "Luoyan liu", "category": "Urson"}, {"name": "Fikki", "category": "Urson"},
]

DEFAULT_TASKS = {
    "Clip/Shoot": {"target_kpi": 674, "avg_kpi": 400, "freq": 1, "active": True, "is_manual": False, "deletable": False},
    "Pollination": {"target_kpi": 2500, "avg_kpi": 2250, "freq": 3, "active": True, "is_manual": False, "deletable": False},
    "De-leafing": {"target_kpi": 800, "avg_kpi": 750, "freq": 1, "active": True, "is_manual": False, "deletable": False},
    "Truss Support": {"target_kpi": 1200, "avg_kpi": 550, "freq": 1, "active": True, "is_manual": False, "deletable": False},
    "Pruning": {"target_kpi": 1200, "avg_kpi": 900, "freq": 1, "active": True, "is_manual": False, "deletable": False},
    "Lowering": {"target_kpi": 1333, "avg_kpi": 1400, "freq": 1, "active": True, "is_manual": False, "deletable": False},
    "Others": {"target_kpi": 0, "avg_kpi": 0, "freq": 1, "active": True, "is_manual": True, "manual_req": 2, "deletable": False},
}

DEFAULT_PARAMS = {
    "week_date": date.today().isoformat(),
    "total_rows": 260,
    "plants_per_row": 480,
    "target_days": 5.0,
    "hours_per_day": 7.35
}

def load_data(filename, default_val):
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                return json.load(f)
        except:
            return default_val
    return default_val

def save_data(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f)

if "staff_list" not in st.session_state:
    st.session_state.staff_list = load_data(STAFF_FILE, DEFAULT_STAFF)

if "task_config" not in st.session_state:
    st.session_state.task_config = load_data(TASK_FILE, DEFAULT_TASKS)

if "assignments" not in st.session_state:
    default_assignments = {task: [] for task in st.session_state.task_config.keys()}
    st.session_state.assignments = load_data(ASSIGNMENT_FILE, default_assignments)

if "global_params" not in st.session_state:
    st.session_state.global_params = load_data(PARAMS_FILE, DEFAULT_PARAMS)

if "map_progress" not in st.session_state:
    st.session_state.map_progress = load_data(MAP_FILE, {})

def get_category_color(cat):
    colors = {
        "GG": "🟢 **GG**",
        "TOTC": "🟤 **TOTC**",
        "Urson": "🔵 **Urson**",
        "Leading Hand": "🟡 **Leading Hand**"
    }
    return colors.get(cat, cat)

def get_badge_html(name, cat):
    styles = {
        "GG": "background: #1b381e; color: #81c784; border: 1px solid #2e7d32;",
        "TOTC": "background: #3e2723; color: #d7ccc8; border: 1px solid #5d4037;",
        "Urson": "background: #0d3b66; color: #90caf9; border: 1px solid #1565c0;",
        "Leading Hand": "background: #4a3d00; color: #fff59d; border: 1px solid #fbc02d;"
    }
    s = styles.get(cat, "background: #333; color: #fff;")
    return f"<span style='{s} padding: 1px 3px; border-radius: 4px; font-size: 0.7rem; font-weight: 600; display: inline-block; margin: 1px;'>{name}</span>"

st.title("🌿 GH Labor Planner")

tab_assign, tab_calc, tab_staff, tab_map = st.tabs([
    "📋 Roster", 
    "📊 Calculator", 
    "👥 Staff Pool",
    "🗺️ Greenhouse Map"
])

gp = st.session_state.global_params
total_plants = gp["total_rows"] * gp["plants_per_row"]

def sort_tasks(task_dict):
    def task_sort_key(item):
        name = item[0].lower()
        if "clip/shoot" in name:
            return 0
        elif "pollination" in name:
            return 1
        elif "other" in name:
            return 99
        else:
            return 2
            
    sorted_items = sorted(task_dict.items(), key=task_sort_key)
    return {k: v for k, v in sorted_items}

st.session_state.task_config = sort_tasks(st.session_state.task_config)
active_tasks = {task: cfg for task, cfg in st.session_state.task_config.items() if cfg.get("active", True)}

for t in st.session_state.task_config:
    if t not in st.session_state.assignments:
        st.session_state.assignments[t] = []

# ==========================================
# TAB 1: ROSTER & ASSIGNMENTS
# ==========================================
with tab_assign:
    task_requirements_display = {}
    for task, cfg in active_tasks.items():
        if cfg.get("is_manual", False):
            req_staff = cfg.get("manual_req", 1)
        else:
            total_task_plants = total_plants * cfg["freq"]
            daily_output_per_person = cfg["avg_kpi"] * gp["hours_per_day"]
            total_man_days = total_task_plants / daily_output_per_person if daily_output_per_person > 0 else 0
            req_staff = math.ceil(total_man_days / gp["target_days"])
        task_requirements_display[task] = req_staff

    col_pool, col_tasks = st.columns([1, 1.5])
    
    with col_pool:
        st.markdown(f"**Staff Pool ({len(st.session_state.staff_list)})**")
        for cat in ["GG", "Leading Hand", "TOTC", "Urson"]:
            members = [s["name"] for s in st.session_state.staff_list if s["category"] == cat]
            if members:
                st.markdown(f"**{get_category_color(cat)}** ({len(members)})", unsafe_allow_html=True)
                st.markdown("".join([get_badge_html(m, cat) for m in members]), unsafe_allow_html=True)

    with col_tasks:
        st.markdown("**Task Assignments**")
        all_staff_names = [s["name"] for s in st.session_state.staff_list]
        
        current_assigned_flat = []
        for t, assigned_list in st.session_state.assignments.items():
            if t in active_tasks:
                current_assigned_flat.extend(assigned_list)

        assignments_changed = False
        for task, req_cnt in task_requirements_display.items():
            st.markdown(f"🔹 **{task}** (Need: **{req_cnt}**)")
            
            currently_selected = [m for m in st.session_state.assignments.get(task, []) if m in all_staff_names]
            other_assigned = [m for m in current_assigned_flat if m not in currently_selected]
            available_options = [m for m in all_staff_names if m not in other_assigned]

            assigned = st.multiselect(
                f"Assign {task}",
                options=available_options,
                default=currently_selected,
                key=f"assign_task_{task}",
                label_visibility="collapsed"
            )
            
            if st.session_state.assignments.get(task) != assigned:
                st.session_state.assignments[task] = assigned
                assignments_changed = True
            
            current_assigned_flat = []
            for t, assigned_list in st.session_state.assignments.items():
                if t in active_tasks:
                    current_assigned_flat.extend(assigned_list)
            
            diff = len(assigned) - req_cnt
            if diff == 0:
                st.markdown(f"<small style='color: #4e9f3d;'>✅ {len(assigned)} assigned</small>", unsafe_allow_html=True)
            elif diff > 0:
                st.markdown(f"<small style='color: #ffb703;'>⚠️ +{diff} over</small>", unsafe_allow_html=True)
            else:
                st.markdown(f"<small style='color: #ff6b6b;'>❌ Need {abs(diff)} more</small>", unsafe_allow_html=True)
            st.markdown("---")

        if assignments_changed:
            save_data(ASSIGNMENT_FILE, st.session_state.assignments)

    # --- COPY PASTE LIST 1 ---
    st.markdown("### 📱 Copy-Paste List 1: Grouped by Category")
    cat_map = {"GG": [], "Leading Hand": [], "TOTC": [], "Urson": []}
    for task, assigned_members in st.session_state.assignments.items():
        if task in active_tasks:
            for name in assigned_members:
                cat = next((s["category"] for s in st.session_state.staff_list if s["name"] == name), "Other")
                if cat not in cat_map:
                    cat_map[cat] = []
                cat_map[cat].append(name)

    list1_text = f"GH ROSTER - BY CATEGORY ({gp['week_date']})\n\n"
    for cat in ["GG", "Leading Hand", "TOTC", "Urson"]:
        members = cat_map[cat]
        if members:
            list1_text += f"*{cat.upper()}*\n"
            for idx, name in enumerate(members, 1):
                list1_text += f"{idx}. {name}\n"
            list1_text += "\n"
    st.code(list1_text, language="text")

    # --- COPY PASTE LIST 2 ---
    st.markdown("### 📱 Copy-Paste List 2: Grouped by Task (All Staff)")
    list2_text = f"GH ROSTER - BY TASK ({gp['week_date']})\n\n"
    for task in active_tasks:
        assigned_members = st.session_state.assignments.get(task, [])
        if assigned_members:
            list2_text += f"*{task.upper()}*\n"
            for idx, name in enumerate(assigned_members, 1):
                cat = next((s["category"] for s in st.session_state.staff_list if s["name"] == name), "Staff")
                list2_text += f"{idx}. {name} ({cat})\n"
            list2_text += "\n"
    st.code(list2_text, language="text")

    # --- COPY PASTE LIST 3 ---
    st.markdown("### 📱 Copy-Paste List 3: Urson Staff Only (By Task)")
    list3_text = f"GH ROSTER - URSON ONLY ({gp['week_date']})\n\n"
    urson_has_assignments = False
    for task in active_tasks:
        assigned_members = st.session_state.assignments.get(task, [])
        urson_members = [
            m for m in assigned_members 
            if next((s["category"] for s in st.session_state.staff_list if s["name"] == m), "") == "Urson"
        ]
        if urson_members:
            urson_has_assignments = True
            list3_text += f"*{task.upper()}*\n"
            for idx, name in enumerate(urson_members, 1):
                list3_text += f"{idx}. {name} (Urson)\n"
            list3_text += "\n"
    
    if not urson_has_assignments:
        list3_text += "No Urson staff assigned to tasks yet.\n"
        
    st.code(list3_text, language="text")
    st.markdown('<div class="footer-watermark">Developed by Sagar</div>', unsafe_allow_html=True)

# ==========================================
# TAB 2: CALCULATOR, SETTINGS & TASK BUILDER
# ==========================================
with tab_calc:
    st.subheader("⚙️ Greenhouse Settings")
    
    c_set1, c_set2, c_set3, c_set4, c_set5 = st.columns(5)
    parsed_date = date.fromisoformat(gp["week_date"]) if isinstance(gp["week_date"], str) else gp["week_date"]
    
    params_changed = False
    
    new_week_date = c_set1.date_input("Week:", value=parsed_date, key="input_week_date")
    if gp["week_date"] != new_week_date.isoformat():
        gp["week_date"] = new_week_date.isoformat()
        params_changed = True
    
    new_rows = c_set2.number_input("Rows", min_value=1, value=int(gp["total_rows"]), key="input_total_rows")
    if gp["total_rows"] != new_rows:
        gp["total_rows"] = new_rows
        params_changed = True

    new_plr = c_set3.number_input("Pl/Row", min_value=1, value=int(gp["plants_per_row"]), key="input_plants_per_row")
    if gp["plants_per_row"] != new_plr:
        gp["plants_per_row"] = new_plr
        params_changed = True

    new_days = c_set4.number_input("Days", min_value=1.0, value=float(gp["target_days"]), step=0.5, key="input_target_days")
    if gp["target_days"] != new_days:
        gp["target_days"] = new_days
        params_changed = True

    new_hrs = c_set5.number_input("Hrs/Day", min_value=1.0, value=float(gp["hours_per_day"]), step=0.05, key="input_hours_per_day")
    if gp["hours_per_day"] != new_hrs:
        gp["hours_per_day"] = new_hrs
        params_changed = True

    if params_changed:
        save_data(PARAMS_FILE, gp)

    st.markdown("---")
    st.subheader("📊 Calculator, KPIs & Tasks")
    
    total_avg_staff_req = 0
    total_target_staff_req = 0
    config_changed = False

    for task, cfg in list(st.session_state.task_config.items()):
        col_t1, col_t2, col_t3 = st.columns([1.2, 1, 1])
        
        is_active = col_t1.checkbox(f"{task}", value=cfg.get("active", True), key=f"active_{task}")
        if cfg.get("active") != is_active:
            st.session_state.task_config[task]["active"] = is_active
            config_changed = True
        
        if cfg.get("is_manual", False):
            manual_req = col_t2.number_input(f"Manual Req {task}", min_value=0, value=int(cfg.get("manual_req", 2)), key=f"manual_req_{task}")
            if cfg.get("manual_req") != manual_req:
                st.session_state.task_config[task]["manual_req"] = manual_req
                config_changed = True
                
            col_t3.markdown("<small style='color:gray;'>Manual Input</small>", unsafe_allow_html=True)
            
            if is_active:
                total_avg_staff_req += manual_req
                total_target_staff_req += manual_req
                st.markdown(f"<small>📌 Req: <b>{manual_req} staff</b></small>", unsafe_allow_html=True)
        else:
            freq = cfg["freq"]
            total_task_plants = total_plants * freq
            
            new_avg_kpi = col_t2.number_input(f"Avg KPI {task}", min_value=1, value=int(cfg["avg_kpi"]), step=10, key=f"edit_avg_{task}")
            if cfg.get("avg_kpi") != new_avg_kpi:
                st.session_state.task_config[task]["avg_kpi"] = new_avg_kpi
                config_changed = True
                
            new_target_kpi = col_t3.number_input(f"Target KPI {task}", min_value=1, value=int(cfg["target_kpi"]), step=10, key=f"edit_target_{task}")
            if cfg.get("target_kpi") != new_target_kpi:
                st.session_state.task_config[task]["target_kpi"] = new_target_kpi
                config_changed = True
            
            if is_active:
                avg_daily_output = new_avg_kpi * gp["hours_per_day"]
                avg_req_staff = math.ceil((total_task_plants / avg_daily_output) / gp["target_days"]) if avg_daily_output > 0 else 0
                total_avg_staff_req += avg_req_staff
                
                target_daily_output = new_target_kpi * gp["hours_per_day"]
                target_req_staff = math.ceil((total_task_plants / target_daily_output) / gp["target_days"]) if target_daily_output > 0 else 0
                target_req_staff = max(1, target_req_staff)
                total_target_staff_req += target_req_staff
                
                st.markdown(f"<small>📌 Req (Avg): <b>{avg_req_staff}</b> | Req (Target): <b>{target_req_staff}</b></small>", unsafe_allow_html=True)
            else:
                st.markdown("<small style='color: gray;'>Task skipped this week</small>", unsafe_allow_html=True)
                
        st.markdown("---")

    if config_changed:
        save_data(TASK_FILE, st.session_state.task_config)

    col_exp1, col_exp2 = st.columns(2)
    with col_exp1:
        with st.expander("➕ Add New Task"):
            with st.form("new_task_form", clear_on_submit=True):
                new_task_name = st.text_input("Task Name")
                new_task_type = st.selectbox("Task Type", ["KPI-based (Calculated)", "Manual Member Count"])
                new_task_freq = st.number_input("Frequency per week", min_value=1, value=1)
                submitted_task = st.form_submit_button("Create Task")
                
                if submitted_task and new_task_name.strip():
                    if new_task_name.strip() not in st.session_state.task_config:
                        is_man = (new_task_type == "Manual Member Count")
                        st.session_state.task_config[new_task_name.strip()] = {
                            "target_kpi": 1000, "avg_kpi": 800, "freq": new_task_freq, 
                            "active": True, "is_manual": is_man, "manual_req": 2, "deletable": True
                        }
                        save_data(TASK_FILE, st.session_state.task_config)
                        if new_task_name.strip() not in st.session_state.assignments:
                            st.session_state.assignments[new_task_name.strip()] = []
                            save_data(ASSIGNMENT_FILE, st.session_state.assignments)
                        st.success(f"Added task {new_task_name.strip()}!")
                        st.rerun()
                    else:
                        st.error("Task already exists!")

    with col_exp2:
        with st.expander("❌ Delete Custom Task"):
            deletable_tasks = [t for t, cfg in st.session_state.task_config.items() if cfg.get("deletable", True)]
            task_to_delete = st.selectbox("Select task to delete:", options=[""] + deletable_tasks)
            if st.button("Delete Task", type="primary"):
                if task_to_delete:
                    del st.session_state.task_config[task_to_delete]
                    save_data(TASK_FILE, st.session_state.task_config)
                    if task_to_delete in st.session_state.assignments:
                        del st.session_state.assignments[task_to_delete]
                        save_data(ASSIGNMENT_FILE, st.session_state.assignments)
                    st.success(f"Deleted task '{task_to_delete}'.")
                    st.rerun()
                else:
                    st.warning("Please select a task to delete.")

    st.markdown("---")
    
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Total Staff Required (Avg)", f"{total_avg_staff_req}")
    col_m2.metric("Total Available Pool", f"{len(st.session_state.staff_list)}")
    planned_hrs = total_avg_staff_req * 7.6 * 5
    col_m3.metric("Roughly Planned Hours", f"{planned_hrs:g} hrs")
    st.markdown('<div class="footer-watermark">Developed by Sagar</div>', unsafe_allow_html=True)

# ==========================================
# TAB 3: STAFF POOL MANAGEMENT (PERSISTENT)
# ==========================================
with tab_staff:
    st.subheader("👥 Manage Staff Pool")
    
    with st.form("add_staff_form_direct", clear_on_submit=True):
        new_name = st.text_input("New Starter Name")
        new_cat = st.selectbox("Category", ["GG", "Leading Hand", "TOTC", "Urson"])
        if st.form_submit_button("➕ Add Member") and new_name.strip():
            if not any(s["name"].lower() == new_name.strip().lower() for s in st.session_state.staff_list):
                st.session_state.staff_list.append({"name": new_name.strip(), "category": new_cat})
                save_staff(st.session_state.staff_list)
                st.success(f"Added {new_name.strip()}!")
                st.rerun()
            else:
                st.error("Already exists!")

    staff_to_remove = st.selectbox("Remove staff who left:", options=[""] + [s["name"] for s in st.session_state.staff_list])
    if st.button("❌ Remove Selected", type="primary"):
        if staff_to_remove:
            st.session_state.staff_list = [s for s in st.session_state.staff_list if s["name"] != staff_to_remove]
            save_staff(st.session_state.staff_list)
            for task_key in st.session_state.assignments:
                st.session_state.assignments[task_key] = [m for m in st.session_state.assignments[task_key] if m != staff_to_remove]
            save_data(ASSIGNMENT_FILE, st.session_state.assignments)
            st.success(f"Removed {staff_to_remove}.")
            st.rerun()

    st.markdown("---")
    df_roster = pd.DataFrame(st.session_state.staff_list)
    st.dataframe(df_roster, use_container_width=True, hide_index=True)
    st.markdown('<div class="footer-watermark">Developed by Sagar</div>', unsafe_allow_html=True)

# ==========================================
# TAB 4: GREENHOUSE MAP & TASK TRACKING
# ==========================================
with tab_map:
    st.subheader("🗺️ Greenhouse Task Map")
    
    # Task selector dropdown
    available_tasks_list = list(st.session_state.task_config.keys())
    selected_track_task = st.selectbox("Select Task to Track & Color-Code:", options=available_tasks_list, key="map_task_selector")
    
    st.markdown("<small>💡 <i>Click any row button below to cycle its status: <b>Pending (Default)</b> ➡️ <b>Half Finished (Yellow)</b> ➡️ <b>Finished (Green)</b></i></small>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Initialize task map storage dictionary if missing
    if selected_track_task not in st.session_state.map_progress:
        st.session_state.map_progress[selected_track_task] = {}

    north_rows = list(range(3001, 3260, 2))
    south_rows = list(range(3002, 3261, 2))
    
    col_north, col_south = st.columns(2)
    
    map_updated = False
    
    with col_north:
        st.markdown("#### ⬆️ North Side (Odd Rows)")
        for r in north_rows:
            r_str = str(r)
            current_status = st.session_state.map_progress[selected_track_task].get(r_str, "Pending")
            
            # Button color styling
            if current_status == "Finished":
                btn_label = f"🟢 Row {r} (Finished)"
            elif current_status == "Half Finished":
                btn_label = f"🟡 Row {r} (Half Finished)"
            else:
                btn_label = f"⚪ Row {r} (Pending)"
                
            if st.button(btn_label, key=f"row_btn_{selected_track_task}_{r}"):
                # Cycle status: Pending -> Half Finished -> Finished -> Pending
                if current_status == "Pending":
                    new_status = "Half Finished"
                elif current_status == "Half Finished":
                    new_status = "Finished"
                else:
                    new_status = "Pending"
                
                st.session_state.map_progress[selected_track_task][r_str] = new_status
                map_updated = True
                st.rerun()
                
    with col_south:
        st.markdown("#### ⬇️ South Side (Even Rows)")
        for r in south_rows:
            r_str = str(r)
            current_status = st.session_state.map_progress[selected_track_task].get(r_str, "Pending")
            
            if current_status == "Finished":
                btn_label = f"🟢 Row {r} (Finished)"
            elif current_status == "Half Finished":
                btn_label = f"🟡 Row {r} (Half Finished)"
            else:
                btn_label = f"⚪ Row {r} (Pending)"
                
            if st.button(btn_label, key=f"row_btn_{selected_track_task}_{r}"):
                if current_status == "Pending":
                    new_status = "Half Finished"
                elif current_status == "Half Finished":
                    new_status = "Finished"
                else:
                    new_status = "Pending"
                
                st.session_state.map_progress[selected_track_task][r_str] = new_status
                map_updated = True
                st.rerun()

    if map_updated:
        save_data(MAP_FILE, st.session_state.map_progress)

    st.markdown("---")
    if st.button("🔄 Reset All Map Progress", type="primary"):
        st.session_state.map_progress = {}
        if os.path.exists(MAP_FILE):
            os.remove(MAP_FILE)
        st.success("Map progress reset successfully!")
        st.rerun()

    st.markdown('<div class="footer-watermark">Developed by Sagar</div>', unsafe_allow_html=True)
