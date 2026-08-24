import math
import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="GH3 Roster & Allocation Planner", layout="wide")

# --- INITIALIZE SESSION STATE ---
if "staff_list" not in st.session_state:
    st.session_state.staff_list = [
        # GG (5)
        {"name": "Marie", "category": "GG"},
        {"name": "Kid", "category": "GG"},
        {"name": "Ting", "category": "GG"},
        {"name": "Tommy", "category": "GG"},
        {"name": "Risa", "category": "GG"},
        
        # Leading Hand (3)
        {"name": "Rebecca", "category": "Leading Hand"},
        {"name": "Rene", "category": "Leading Hand"},
        {"name": "Tico", "category": "Leading Hand"},
        
        # TOTC (6)
        {"name": "Alfredo", "category": "TOTC"},
        {"name": "Enock", "category": "TOTC"},
        {"name": "Dick", "category": "TOTC"},
        {"name": "Dan", "category": "TOTC"},
        {"name": "Will", "category": "TOTC"},
        {"name": "Terry", "category": "TOTC"},
        
        # Urson (23)
        {"name": "Nikki", "category": "Urson"},
        {"name": "Bina", "category": "Urson"}, 
        {"name": "Tiara", "category": "Urson"},
        {"name": "Shisir", "category": "Urson"},
        {"name": "Jimmy", "category": "Urson"},
        {"name": "Chandra", "category": "Urson"},
        {"name": "Malick", "category": "Urson"},
        {"name": "Audrey", "category": "Urson"},
        {"name": "Han", "category": "Urson"},
        {"name": "Rosie", "category": "Urson"},
        {"name": "Dhia", "category": "Urson"},
        {"name": "Hui", "category": "Urson"}, 
        {"name": "Erica", "category": "Urson"},
        {"name": "Lin", "category": "Urson"},
        {"name": "Moka", "category": "Urson"},
        {"name": "Panyawat", "category": "Urson"},
        {"name": "AkashDeep", "category": "Urson"},
        {"name": "Zakia", "category": "Urson"},
        {"name": "Supakit", "category": "Urson"},
        {"name": "Camie", "category": "Urson"},
        {"name": "Fierda", "category": "Urson"},
        {"name": "Luoyan liu", "category": "Urson"},
        {"name": "Fikki", "category": "Urson"},
    ]

if "task_config" not in st.session_state:
    st.session_state.task_config = {
        "Clip/Shoot": {"target_kpi": 674, "avg_kpi": 400, "freq": 1, "active": True},
        "De-leafing": {"target_kpi": 800, "avg_kpi": 750, "freq": 1, "active": True},
        "Pollination": {"target_kpi": 2500, "avg_kpi": 2250, "freq": 3, "active": True},
        "Truss Support": {"target_kpi": 1200, "avg_kpi": 550, "freq": 1, "active": True},
        "Pruning": {"target_kpi": 1200, "avg_kpi": 900, "freq": 1, "active": True},
        "Lowering": {"target_kpi": 1333, "avg_kpi": 1400, "freq": 1, "active": True},
    }

if "assignments" not in st.session_state:
    st.session_state.assignments = {task: [] for task in st.session_state.task_config.keys()}

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
        "GG": "background: #E8F5E9; color: #2E7D32; border: 1px solid #A5D6A7;",
        "TOTC": "background: #EFEBE9; color: #4E342E; border: 1px solid #BCAAA4;",
        "Urson": "background: #E3F2FD; color: #1565C0; border: 1px solid #90CAF9;",
        "Leading Hand": "background: #FFFDE7; color: #F57F17; border: 1px solid #FFF59D;"
    }
    s = styles.get(cat, "background: #F5F5F5; color: #333;")
    return f"<span style='{s} padding: 2px 8px; border-radius: 10px; font-size: 0.85rem; font-weight: 600; display: inline-block; margin: 2px;'>{name}</span>"

st.title("🌿 GH3 Labor Allocation & Roster Planner")

with st.container():
    c_set1, c_set2, c_set3, c_set4, c_set5 = st.columns(5)
    week_date = c_set1.date_input("Week Of:", value=date.today())
    total_rows = c_set2.number_input("Total Rows", min_value=1, value=260)
    plants_per_row = c_set3.number_input("Plants per Row", min_value=1, value=480)
    target_days = c_set4.number_input("Target Days", min_value=1.0, value=5.0, step=0.5)
    hours_per_day = c_set5.number_input("Hours / Day", min_value=1.0, value=7.35, step=0.05)

total_plants = total_rows * plants_per_row
st.markdown("---")

tab_assign, tab_calc, tab_staff = st.tabs([
    "📋 Tab 1: Roster & Assignments", 
    "📊 Tab 2: KPI & Staff Requirement Calculator", 
    "👥 Add / Remove Staff Pool"
])

# Filter only active tasks for the week
active_tasks = {task: cfg for task, cfg in st.session_state.task_config.items() if cfg.get("active", True)}

# ==========================================
# TAB 1: ROSTER & ASSIGNMENTS (ANTI-DOUBLE BOOKING)
# ==========================================
with tab_assign:
    st.subheader("Interactive Assignment & Copy-Paste Roster")
    
    task_requirements_display = {}
    for task, cfg in active_tasks.items():
        total_task_plants = total_plants * cfg["freq"]
        daily_output_per_person = cfg["avg_kpi"] * hours_per_day
        total_man_days = total_task_plants / daily_output_per_person if daily_output_per_person > 0 else 0
        req_staff = math.ceil(total_man_days / target_days)
        task_requirements_display[task] = req_staff

    col_pool, col_tasks = st.columns([1.2, 2])
    
    with col_pool:
        st.markdown(f"#### 👥 Staff Pool ({len(st.session_state.staff_list)} Total)")
        for cat in ["GG", "Leading Hand", "TOTC", "Urson"]:
            members = [s["name"] for s in st.session_state.staff_list if s["category"] == cat]
            if members:
                st.markdown(f"**{get_category_color(cat)}** ({len(members)})")
                badge_block = "".join([get_badge_html(m, cat) for m in members])
                st.markdown(badge_block, unsafe_allow_html=True)
                st.markdown("")

    with col_tasks:
        st.markdown("#### 📝 Task Assignments (Active Tasks Only)")
        if not active_tasks:
            st.info("All tasks are currently unchecked in Tab 2. Check at least one task to assign staff.")
        
        all_staff_names = [s["name"] for s in st.session_state.staff_list]
        
        current_assigned_flat = []
        for t, assigned_list in st.session_state.assignments.items():
            if t in active_tasks:
                current_assigned_flat.extend(assigned_list)

        for task, req_cnt in task_requirements_display.items():
            st.markdown(f"**{task}** — <span style='color: #2D6A4F; font-weight: 600;'>Required: {req_cnt} staff</span>", unsafe_allow_html=True)
            
            currently_selected = [m for m in st.session_state.assignments.get(task, []) if m in all_staff_names]
            other_assigned = [m for m in current_assigned_flat if m not in currently_selected]
            available_options = [m for m in all_staff_names if m not in other_assigned]

            assigned = st.multiselect(
                f"Assign for {task}",
                options=available_options,
                default=currently_selected,
                key=f"assign_task_{task}",
                label_visibility="collapsed"
            )
            st.session_state.assignments[task] = assigned
            
            current_assigned_flat = []
            for t, assigned_list in st.session_state.assignments.items():
                if t in active_tasks:
                    current_assigned_flat.extend(assigned_list)
            
            diff = len(assigned) - req_cnt
            if diff == 0:
                st.markdown(f"<small style='color: green;'>✅ Exactly {len(assigned)} staff assigned</small>", unsafe_allow_html=True)
            elif diff > 0:
                st.markdown(f"<small style='color: orange;'>⚠️ {len(assigned)} assigned ({diff} over requirement)</small>", unsafe_allow_html=True)
            else:
                st.markdown(f"<small style='color: red;'>❌ {len(assigned)} assigned (Need {abs(diff)} more)</small>", unsafe_allow_html=True)
            st.markdown("---")

    st.markdown("---")
    st.markdown("### 📱 Copy-Paste Format (Grouped by Category)")
    
    category_map = {"GG": [], "Leading Hand": [], "TOTC": [], "Urson": []}
    for task, assigned_members in st.session_state.assignments.items():
        if task in active_tasks:
            for name in assigned_members:
                cat = next((s["category"] for s in st.session_state.staff_list if s["name"] == name), "Other")
                if cat not in category_map:
                    category_map[cat] = []
                category_map[cat].append({"name": name, "task": task})

    output_text = f"GH3 - WEEKLY LABOR ROSTER ({week_date.strftime('%d %b %Y')})\n"
    output_text += f"Parameters: {total_rows} rows | {plants_per_row} plants/row | Target: {target_days} days ({hours_per_day} hrs/day)\n"
    output_text += "---------------------------------------------------\n\n"

    for cat in ["GG", "Leading Hand", "TOTC", "Urson"]:
        members = category_map[cat]
        if members:
            output_text += f"*{cat.upper()} ({len(members)})*\n"
            for idx, item in enumerate(members, 1):
                output_text += f"{idx}. {item['name']} - {item['task']}\n"
            output_text += "\n"

    st.code(output_text, language="text")

# ==========================================
# TAB 2: REQUIREMENT CALCULATOR & TASK TOGGLES
# ==========================================
with tab_calc:
    st.subheader("📊 Staff Requirement Breakdown & Weekly Task Selector")
    st.markdown(f"Calculated based on **{total_rows} rows**, **{plants_per_row} plants/row** (**{total_plants:,} total plants**), **{hours_per_day} hrs/day**, and a target of **{target_days} days**.")
    st.markdown("Check or uncheck tasks below depending on whether you are running them this week:")
    st.markdown("---")
    
    col_h0, col_h1, col_h2, col_h3, col_h4, col_h5 = st.columns([0.6, 1.4, 1, 1.2, 1.2, 1])
    col_h0.markdown("**Active**")
    col_h1.markdown("**Task Name**")
    col_h2.markdown("**Frequency**")
    col_h3.markdown("**Avg KPI / Req**")
    col_h4.markdown("**Target KPI / Req**")
    col_h5.markdown("**Difference**")
    st.markdown("---")

    total_avg_staff_req = 0
    total_target_staff_req = 0

    for task, cfg in st.session_state.task_config.items():
        c0, c1, c2, c3, c4, c5 = st.columns([0.6, 1.4, 1, 1.2, 1.2, 1])
        
        # Toggle checkbox for task active status
        is_active = c0.checkbox(f"Active {task}", value=cfg.get("active", True), key=f"active_{task}", label_visibility="collapsed")
        st.session_state.task_config[task]["active"] = is_active
        
        c1.markdown(f"**{task}**" if is_active else f"~~{task}~~ <small style='color:gray;'>(Skipped)</small>", unsafe_allow_html=True)
        freq = cfg["freq"]
        c2.markdown(f"{freq}x / week" if freq > 1 else "1x / week")
        
        total_task_plants = total_plants * freq
        
        new_avg_kpi = c3.number_input(f"Avg KPI {task}", min_value=1, value=int(cfg["avg_kpi"]), step=10, key=f"edit_avg_{task}", label_visibility="collapsed")
        st.session_state.task_config[task]["avg_kpi"] = new_avg_kpi
        
        new_target_kpi = c4.number_input(f"Target KPI {task}", min_value=1, value=int(cfg["target_kpi"]), step=10, key=f"edit_target_{task}", label_visibility="collapsed")
        st.session_state.task_config[task]["target_kpi"] = new_target_kpi
        
        if is_active:
            avg_daily_output = new_avg_kpi * hours_per_day
            avg_req_staff = math.ceil((total_task_plants / avg_daily_output) / target_days) if avg_daily_output > 0 else 0
            total_avg_staff_req += avg_req_staff
            
            target_daily_output = new_target_kpi * hours_per_day
            target_req_staff = math.ceil((total_task_plants / target_daily_output) / target_days) if target_daily_output > 0 else 0
            target_req_staff = max(1, target_req_staff)
            total_target_staff_req += target_req_staff
            
            c3.markdown(f"<small>Req: **{avg_req_staff} staff**</small>", unsafe_allow_html=True)
            c4.markdown(f"<small>Req: **{target_req_staff} staff**</small>", unsafe_allow_html=True)
            
            diff = avg_req_staff - target_req_staff
            if diff > 0:
                c5.markdown(f"<span style='color: orange;'>+{diff} staff</span>", unsafe_allow_html=True)
            elif diff < 0:
                c5.markdown(f"<span style='color: green;'>{diff} staff</span>", unsafe_allow_html=True)
            else:
                c5.markdown("`Match`", unsafe_allow_html=True)
        else:
            c3.markdown("<small style='color: gray;'>Skipped</small>", unsafe_allow_html=True)
            c4.markdown("<small style='color: gray;'>Skipped</small>", unsafe_allow_html=True)
            c5.markdown("<small style='color: gray;'>N/A</small>", unsafe_allow_html=True)
            
        st.markdown("---")

    st.markdown("### 📈 Summary Total Requirements (Active Tasks Only)")
    col_sum1, col_sum2, col_sum3 = st.columns(3)
    col_sum1.metric("Total Staff Required (Avg KPI)", f"{total_avg_staff_req} staff")
    col_sum2.metric("Total Staff Required (Target KPI)", f"{total_target_staff_req} staff")
    col_sum3.metric("Total Available Staff Pool", f"{len(st.session_state.staff_list)} members")

# ==========================================
# TAB 3: ADD / REMOVE STAFF POOL
# ==========================================
with tab_staff:
    st.subheader("👥 Add New Starters or Remove Staff (Quits/Departures)")
    
    col_add, col_remove = st.columns(2)
    
    with col_add:
        st.markdown("#### ➕ Add New Starter")
        with st.form("add_staff_form_direct", clear_on_submit=True):
            new_name = st.text_input("Staff Name")
            new_cat = st.selectbox("Category", ["GG", "Leading Hand", "TOTC", "Urson"])
            submitted = st.form_submit_button("Add Member to Pool")
            
            if submitted and new_name.strip():
                if not any(s["name"].lower() == new_name.strip().lower() for s in st.session_state.staff_list):
                    st.session_state.staff_list.append({"name": new_name.strip(), "category": new_cat})
                    st.success(f"Successfully added {new_name.strip()}!")
                    st.rerun()
                else:
                    st.error("A staff member with this name already exists!")

    with col_remove:
        st.markdown("#### ❌ Remove Staff Member")
        all_current_names = [s["name"] for s in st.session_state.staff_list]
        staff_to_remove = st.selectbox("Select staff member who left:", options=[""] + all_current_names, key="remove_staff_select")
        
        if st.button("Remove Selected Staff", type="primary"):
            if staff_to_remove:
                st.session_state.staff_list = [s for s in st.session_state.staff_list if s["name"] != staff_to_remove]
                for task_key in st.session_state.assignments:
                    st.session_state.assignments[task_key] = [m for m in st.session_state.assignments[task_key] if m != staff_to_remove]
                st.success(f"Removed {staff_to_remove} from the pool.")
                st.rerun()
            else:
                st.warning("Please select a staff member first.")

    st.markdown("---")
    st.markdown("#### Current Active Pool Overview")
    df_roster = pd.DataFrame(st.session_state.staff_list)
    st.dataframe(df_roster, use_container_width=True, hide_index=True)
