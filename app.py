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
        "Clip/Shoot": {"target_kpi": 674, "avg_kpi": 400, "freq": 1},
        "De-leafing": {"target_kpi": 800, "avg_kpi": 750, "freq": 1},
        "Pollination": {"target_kpi": 2500, "avg_kpi": 2250, "freq": 3},
        "Truss Support": {"target_kpi": 1200, "avg_kpi": 550, "freq": 1},
        "Pruning": {"target_kpi": 1200, "avg_kpi": 900, "freq": 1},
        "Lowering": {"target_kpi": 1333, "avg_kpi": 1400, "freq": 1},
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
    c_set1, c_set2, c_set3, c_set4 = st.columns(4)
    week_date = c_set1.date_input("Week Of:", value=date.today())
    total_rows = c_set2.number_input("Total Rows", min_value=1, value=260)
    plants_per_row = c_set3.number_input("Plants per Row", min_value=1, value=480)
    target_days = c_set4.number_input("Target Days to Finish", min_value=1.0, value=5.0, step=0.5)

total_plants = total_rows * plants_per_row
st.markdown("---")

tab_assign, tab_calc, tab_staff = st.tabs([
    "📋 Tab 1: Roster & Assignments", 
    "📊 Tab 2: KPI & Staff Requirement Calculator", 
    "👥 Manage Staff Roster"
])

# ==========================================
# TAB 1: ROSTER & ASSIGNMENTS
# ==========================================
with tab_assign:
    st.subheader("Interactive Assignment & Copy-Paste Roster")
    
    task_requirements_display = {}
    for task, cfg in st.session_state.task_config.items():
        total_task_plants = total_plants * cfg["freq"]
        avg_kpi = cfg["avg_kpi"]
        man_days = total_task_plants / avg_kpi if avg_kpi > 0 else 0
        req_staff = math.ceil(man_days / target_days)
        task_requirements_display[task] = req_staff

    col_pool, col_tasks = st.columns([1.2, 2])
    
    with col_pool:
        st.markdown("#### 👥 Staff Pool")
        for cat in ["GG", "Leading Hand", "TOTC", "Urson"]:
            members = [s["name"] for s in st.session_state.staff_list if s["category"] == cat]
            if members:
                st.markdown(f"**{get_category_color(cat)}** ({len(members)})")
                badge_block = "".join([get_badge_html(m, cat) for m in members])
                st.markdown(badge_block, unsafe_allow_html=True)
                st.markdown("")

    with col_tasks:
        st.markdown("#### 📝 Task Assignments")
        all_staff_names = [s["name"] for s in st.session_state.staff_list]
        assigned_flat = []

        for task, req_cnt in task_requirements_display.items():
            st.markdown(f"**{task}** — <span style='color: #2D6A4F; font-weight: 600;'>Required: {req_cnt} staff</span>", unsafe_allow_html=True)
            
            assigned = st.multiselect(
                f"Assign for {task}",
                options=all_staff_names,
                default=st.session_state.assignments.get(task, []),
                key=f"assign_task_{task}",
                label_visibility="collapsed"
            )
            st.session_state.assignments[task] = assigned
            assigned_flat.extend(assigned)
            
            diff = len(assigned) - req_cnt
            if diff == 0:
                st.markdown(f"<small style='color: green;'>✅ Exactly {len(assigned)} staff assigned</small>", unsafe_allow_html=True)
            elif diff > 0:
                st.markdown(f"<small style='color: orange;'>⚠️ {len(assigned)} assigned ({diff} over requirement)</small>", unsafe_allow_html=True)
            else:
                st.markdown(f"<small style='color: red;'>❌ {len(assigned)} assigned (Need {abs(diff)} more)</small>", unsafe_allow_html=True)
            st.markdown("---")

        duplicates = set([x for x in assigned_flat if assigned_flat.count(x) > 1])
        if duplicates:
            st.error(f"⚠️ **Double Booking Warning:** {', '.join(duplicates)} are assigned to multiple tasks!")

    st.markdown("---")
    st.markdown("### 📱 Copy-Paste Format (Grouped by Category)")
    
    category_map = {"GG": [], "Leading Hand": [], "TOTC": [], "Urson": []}
    for task, assigned_members in st.session_state.assignments.items():
        for name in assigned_members:
            cat = next((s["category"] for s in st.session_state.staff_list if s["name"] == name), "Other")
            if cat not in category_map:
                category_map[cat] = []
            category_map[cat].append({"name": name, "task": task})

    output_text = f"GH3 - WEEKLY LABOR ROSTER ({week_date.strftime('%d %b %Y')})\n"
    output_text += f"Parameters: {total_rows} rows | {plants_per_row} plants/row | Target: {target_days} days\n"
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
# TAB 2: REQUIREMENT CALCULATOR
# ==========================================
with tab_calc:
    st.subheader("📊 Staff Requirement Breakdown (Average KPI vs. Target KPI)")
    st.markdown(f"Calculated based on **{total_rows} rows**, **{plants_per_row} plants/row** (**{total_plants:,} total plants**), and a target of **{target_days} days**.")
    st.markdown("---")
    
    col_h1, col_h2, col_h3, col_h4, col_h5 = st.columns([1.5, 1, 1, 1, 1])
    col_h1.markdown("**Task Name**")
    col_h2.markdown("**Frequency**")
    col_h3.markdown("**Avg KPI / Req Staff**")
    col_h4.markdown("**Target KPI / Req Staff**")
    col_h5.markdown("**Difference**")
    st.markdown("---")

    for task, cfg in st.session_state.task_config.items():
        c1, c2, c3, c4, c5 = st.columns([1.5, 1, 1, 1, 1])
        c1.markdown(f"**{task}**")
        freq = cfg["freq"]
        c2.markdown(f"{freq}x / week" if freq > 1 else "1x / week")
        
        total_task_plants = total_plants * freq
        
        # Corrected calculation dividing by target_days
        avg_kpi = cfg["avg_kpi"]
        avg_man_days = total_task_plants / avg_kpi if avg_kpi > 0 else 0
        avg_req_staff = math.ceil(avg_man_days / target_days)
        c3.markdown(f"**{avg_req_staff} staff**<br><small style='color:gray;'>({avg_kpi} KPI)</small>", unsafe_allow_html=True)
        
        target_kpi = cfg["target_kpi"]
        target_man_days = total_task_plants / target_kpi if target_kpi > 0 else 0
        target_req_staff = math.ceil(target_man_days / target_days)
        c4.markdown(f"**{target_req_staff} staff**<br><small style='color:gray;'>({target_kpi} KPI)</small>", unsafe_allow_html=True)
        
        diff = avg_req_staff - target_req_staff
        if diff > 0:
            c5.markdown(f"<span style='color: orange;'>+{diff} staff needed (Avg)</span>", unsafe_allow_html=True)
        elif diff < 0:
            c5.markdown(f"<span style='color: green;'>{diff} staff (Target met)</span>", unsafe_allow_html=True)
        else:
            c5.markdown("`Exact Match`", unsafe_allow_html=True)
            st.markdown("---")

# ==========================================
# TAB 3: MANAGE STAFF
# ==========================================
with tab_staff:
    st.subheader("Manage Team Roster")
    with st.form("add_staff_form_new", clear_on_submit=True):
        c_n, c_c, c_b = st.columns([2, 2, 1])
        new_name = c_n.text_input("Staff Name")
        new_cat = c_c.selectbox("Category", ["GG", "Leading Hand", "TOTC", "Urson"])
        submitted = c_b.form_submit_button("➕ Add")
        
        if submitted and new_name.strip():
            st.session_state.staff_list.append({"name": new_name.strip(), "category": new_cat})
            st.success(f"Added {new_name.strip()}!")
            st.rerun()

    st.markdown("#### Current Roster Overview")
    df_roster = pd.DataFrame(st.session_state.staff_list)
    st.dataframe(df_roster, use_container_width=True, hide_index=True)
