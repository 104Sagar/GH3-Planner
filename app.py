import math
import json
import os
import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="GH Labor Planner", layout="wide")

# --- COMPACT CSS ---
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
        h1 {
            font-size: 1.6rem !important;
            margin-bottom: 0.2rem !important;
        }
        h2, h3, h5 {
            font-size: 1.1rem !important;
            margin-top: 0.2rem !important;
            margin-bottom: 0.2rem !important;
        }
        p, label, span, div {
            font-size: 0.85rem !important;
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

# Added Tab 5 for your new Tap-to-Assign concept
tab_assign, tab_calc, tab_staff, tab_map, tab_tap = st.tabs([
    "📋 Roster", 
    "📊 Calculator", 
    "👥 Staff Pool",
    "🗺️ Greenhouse Map",
    "⚡ Tap-to-Assign"
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
# TAB 1: ROSTER & ASSIGNMENTS + COPY-PASTE LISTS
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

    st.markdown("---")
    st.markdown("### 📱 Copy-Paste Ready Roster Lists")

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
# TAB 2: CALCULATOR
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
    st.markdown('<div class="footer-watermark">Developed by Sagar</div>', unsafe_allow_html=True)

# ==========================================
# TAB 3: STAFF POOL
# ==========================================
with tab_staff:
    st.subheader("👥 Manage Staff Pool")
    df_roster = pd.DataFrame(st.session_state.staff_list)
    st.dataframe(df_roster, use_container_width=True, hide_index=True)
    st.markdown('<div class="footer-watermark">Developed by Sagar</div>', unsafe_allow_html=True)

# ==========================================
# TAB 4: GREENHOUSE MAP
# ==========================================
with tab_map:
    st.subheader("🗺️ Greenhouse Task Map")
    st.markdown("Use this tab for tracking row completion.")
    st.markdown('<div class="footer-watermark">Developed by Sagar</div>', unsafe_allow_html=True)

# ==========================================
# TAB 5: TAP-TO-ASSIGN CONTROL BOARD
# ==========================================
with tab_tap:
    st.subheader("⚡ Tap-to-Assign Control Board")
    st.markdown("<small>💡 <i>Select a task first, then simply tap staff names from the pool below to assign or unassign them instantly!</i></small>", unsafe_allow_html=True)
    st.markdown("---")

    # Task selector dropdown
    selected_target_task = st.selectbox("Select Task to Assign Workers To:", options=list(active_tasks.keys()), key="tap_task_select")
    
    current_task_assigned = st.session_state.assignments.get(selected_target_task, [])
    
    # Calculate required staff for context
    cfg = active_tasks[selected_target_task]
    if cfg.get("is_manual", False):
        req_cnt = cfg.get("manual_req", 1)
    else:
        tot_p = total_plants * cfg["freq"]
        out_p = cfg["avg_kpi"] * gp["hours_per_day"]
        mand = tot_p / out_p if out_p > 0 else 0
        req_cnt = math.ceil(mand / gp["target_days"])

    st.markdown(f"**Currently assigned to {selected_target_task}:** {len(current_task_assigned)} workers (Target Needed: **{req_cnt}**)")
    st.markdown("---")

    tap_updated = False

    # Display staff grouped by category with interactive toggle buttons
    for cat in ["GG", "Leading Hand", "TOTC", "Urson"]:
        cat_staff = [s for s in st.session_state.staff_list if s["category"] == cat]
        if cat_staff:
            st.markdown(f"**{get_category_color(cat)}**")
            cols = st.columns(3)
            for idx, staff in enumerate(cat_staff):
                name = staff["name"]
                c_target = cols[idx % 3]
                
                # Check status
                is_in_task = name in current_task_assigned
                # Check if assigned to another task
                assigned_elsewhere = ""
                for t, members in st.session_state.assignments.items():
                    if name in members and t != selected_target_task:
                        assigned_elsewhere = f" (in {t})"
                        break

                # Button label with status icon
                if is_in_task:
                    btn_label = f"✅ {name}"
                elif assigned_elsewhere:
                    btn_label = f"📌 {name}{assigned_elsewhere}"
                else:
                    btn_label = f"➕ {name}"

                if c_target.button(btn_label, key=f"tap_btn_{selected_target_task}_{name}", use_container_width=True):
                    if is_in_task:
                        # Remove from task
                        current_task_assigned.remove(name)
                    else:
                        # Add to task (and remove from any other task to avoid duplicates)
                        for t in st.session_state.assignments:
                            if name in st.session_state.assignments[t]:
                                st.session_state.assignments[t].remove(name)
                        current_task_assigned.append(name)
                    
                    st.session_state.assignments[selected_target_task] = current_task_assigned
                    tap_updated = True

            st.markdown("---")

    if tap_updated:
        save_data(ASSIGNMENT_FILE, st.session_state.assignments)
        st.rerun()

    st.markdown('<div class="footer-watermark">Developed by Sagar</div>', unsafe_allow_html=True)
