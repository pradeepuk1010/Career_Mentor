import os
from datetime import date, timedelta
import pandas as pd
import plotly.express as px
import streamlit as st

from database import (
    init_db, load_profile, save_profile, list_goals, add_goal,
    update_goal_status, delete_goal, list_reflections, add_reflection
)
from mentor_engine import (
    SKILL_CATALOG, ROLE_SKILLS, LEARNING_RESOURCES, build_career_snapshot,
    recommend_actions, get_ai_coaching
)

st.set_page_config(
    page_title="Career Mentor | Student Growth OS",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Styling: restrained, professional dashboard ---
st.markdown("""
<style>
:root { --ink:#172033; --muted:#65718a; --line:#e7ebf2; --brand:#4f46e5; }
.block-container { padding-top: 1.4rem; padding-bottom: 2.6rem; max-width: 1400px; }
[data-testid="stSidebar"] { border-right: 1px solid #e7ebf2; }
.hero {
  padding: 1.35rem 1.5rem; border-radius: 18px;
  background: linear-gradient(120deg, #171d3b 0%, #3730a3 60%, #6366f1 100%);
  color: white; margin-bottom: 1rem;
}
.hero h1 { color:white; margin:0; font-size:2rem; letter-spacing:-.03em; }
.hero p { color:#e4e7ff; margin:.4rem 0 0 0; }
.eyebrow { text-transform:uppercase; letter-spacing:.12em; font-size:.72rem; font-weight:700; opacity:.8; }
.section-title { font-size:1.2rem; font-weight:750; letter-spacing:-.02em; margin:.25rem 0 .7rem 0; }
.muted { color:#65718a; font-size:.9rem; }
div[data-testid="stMetric"] { border:1px solid #e7ebf2; border-radius:14px; padding:14px 16px; background:#fff; }
div[data-testid="stForm"] { border:1px solid #e7ebf2; border-radius:14px; padding:18px; }
div.stButton > button { border-radius:10px; font-weight:600; }
.resource-card { border:1px solid #e7ebf2; padding:1rem; border-radius:14px; margin-bottom:.6rem; }
.small-pill { display:inline-block; padding:3px 9px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:.75rem; font-weight:700; }
</style>
""", unsafe_allow_html=True)

init_db()
st.session_state.setdefault("active_page", "Dashboard")
PAGES = ["Dashboard", "Learning Sources", "Profile Settings", "Personal Growth"]

def current_profile():
    return load_profile()

def hero(kicker, title, subtitle):
    st.markdown(
        f'<div class="hero"><div class="eyebrow">{kicker}</div>'
        f'<h1>{title}</h1><p>{subtitle}</p></div>',
        unsafe_allow_html=True
    )

def safe_rerun():
    # streamlit >=1.27 supports st.rerun
    st.rerun()

with st.sidebar:
    st.markdown("## 🎯 Career Mentor")
    st.caption("Student Growth OS")
    st.divider()
    selected = st.radio("Workspace", PAGES, key="nav", label_visibility="collapsed")
    st.session_state["active_page"] = selected
    st.divider()
    p = current_profile()
    st.markdown("**Your current path**")
    st.write(p.get("target_role", "Software Engineer"))
    st.caption(f"{p.get('stage', 'Undergraduate')} · {p.get('weekly_hours', 6)} hrs/week")
    st.progress(min(max(int(p.get("weekly_hours", 6)), 0), 40) / 40)
    st.caption("Set your target and skills in Profile Settings.")
    st.divider()
    st.caption("Prototype · Personal data is stored in the app's SQLite database.")

profile = current_profile()
snapshot = build_career_snapshot(profile)
actions = recommend_actions(profile)

if selected == "Dashboard":
    hero("PERSONALIZED CAREER INTELLIGENCE", f"Welcome back, {profile.get('name') or 'future professional'}",
         "Turn your career goal into a practical weekly plan—with transparent recommendations.")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Role readiness", f"{snapshot['readiness']}%", help="Heuristic coverage of the selected role's core skills; not a hiring probability.")
    col2.metric("Core skills selected", f"{len(profile.get('skills', []))}/{len(ROLE_SKILLS.get(profile.get('target_role'), []))}")
    col3.metric("Open goals", sum(g["status"] != "Completed" for g in list_goals()))
    col4.metric("Weekly learning time", f"{profile.get('weekly_hours', 6)} hrs")
    st.markdown("### Your career snapshot")
    left, right = st.columns([1.2, 1])
    with left:
        role_skills = ROLE_SKILLS.get(profile.get("target_role"), ROLE_SKILLS["Software Engineer"])
        skills = profile.get("skills", [])
        chart_df = pd.DataFrame({
            "Skill": role_skills,
            "Status": ["Selected" if s in skills else "To develop" for s in role_skills],
            "Value": [1 if s in skills else 0 for s in role_skills],
        })
        fig = px.bar(chart_df, x="Skill", y="Value", color="Status",
                     color_discrete_map={"Selected":"#4f46e5", "To develop":"#d9def5"},
                     title="Target-role skill coverage")
        fig.update_layout(height=310, showlegend=True, margin=dict(l=10,r=10,t=55,b=10),
                          yaxis=dict(range=[0,1.1], showticklabels=False, title=None),
                          xaxis_title=None, legend_title=None)
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Coverage is based on skills you selected in your profile. It is a planning aid, not a validated assessment.")
    with right:
        st.markdown("#### Recommended next actions")
        for i, item in enumerate(actions[:4], 1):
            st.markdown(f"**{i}. {item['title']}**")
            st.caption(item["reason"])
        st.info("Start small: choose one action, schedule it, and record progress in Personal Growth.")
    st.divider()
    st.markdown("### AI Career Coach")
    configured_key = os.getenv("GEMINI_API_KEY", "")
    if not configured_key:
        try:
            configured_key = st.secrets.get("GEMINI_API_KEY", "")
        except Exception:
            configured_key = ""
    ai_mode = "Gemini API" if configured_key else "Local recommendation engine"
    st.caption(f"Coach mode: {ai_mode}. If no Gemini key is configured, coaching works using the built-in rule-based engine.")
    prompt = st.text_area("Ask about your next step", placeholder="Example: I have 4 hours this week. What should I prioritize?", height=90)
    if st.button("Generate coaching plan", type="primary"):
        with st.spinner("Preparing your personalized plan…"):
            response, mode = get_ai_coaching(profile, prompt, actions)
        st.markdown(f"**Response ({mode})**")
        st.write(response)
    st.markdown("#### This week's starter plan")
    plan_cols = st.columns(3)
    weekly = actions[:3]
    for idx, c in enumerate(plan_cols):
        with c:
            if idx < len(weekly):
                st.markdown(f"**{weekly[idx]['title']}**")
                st.write(weekly[idx]["reason"])
                st.caption(f"Suggested effort: {weekly[idx]['hours']} hour(s)")

elif selected == "Learning Sources":
    hero("CURATED LEARNING", "Learning Sources", "Find credible starting points and connect each resource to a target skill.")
    role_skills = ROLE_SKILLS.get(profile.get("target_role"), ROLE_SKILLS["Software Engineer"])
    gaps = [s for s in role_skills if s not in profile.get("skills", [])]
    qcol, fcol, pcol = st.columns([1.5, 1, 1])
    with qcol:
        query = st.text_input("Search resources", placeholder="Search Python, SQL, cloud…")
    with fcol:
        free_only = st.checkbox("Free resources only", value=True)
    with pcol:
        prioritize_gaps = st.checkbox("Prioritize my skill gaps", value=True)
    resources = LEARNING_RESOURCES
    if query.strip():
        q = query.strip().lower()
        resources = [r for r in resources if q in (r["title"] + r["skill"] + r["provider"] + r["description"]).lower()]
    if free_only:
        resources = [r for r in resources if r["cost"] == "Free"]
    if prioritize_gaps:
        resources = sorted(resources, key=lambda r: (r["skill"] not in gaps, r["skill"]))
    st.caption(f"{len(resources)} resource(s) match your filters. External sites may change their content or pricing.")
    if not resources:
        st.warning("No resources match those filters. Try a broader search or turn off one filter.")
    for r in resources:
        with st.container(border=True):
            a, b = st.columns([3, 1])
            with a:
                st.markdown(f"**{r['title']}**  ·  <span class='small-pill'>{r['skill']}</span>", unsafe_allow_html=True)
                st.write(r["description"])
                st.caption(f"{r['provider']} · {r['level']} · {r['format']}")
            with b:
                st.caption(r["cost"])
                st.link_button("Open resource ↗", r["url"], use_container_width=True)

elif selected == "Profile Settings":
    hero("YOUR BASELINE", "Profile Settings", "Keep your target role, current strengths, and time budget up to date.")
    all_skills = sorted(SKILL_CATALOG)
    with st.form("profile_form"):
        name = st.text_input("Display name", value=profile.get("name", "Student"))
        role_options = list(ROLE_SKILLS.keys())
        target_role = st.selectbox("Target role", role_options,
                                   index=role_options.index(profile.get("target_role", "Software Engineer")) if profile.get("target_role", "Software Engineer") in role_options else 0)
        stages = ["1st year", "2nd year", "3rd year", "4th year", "Recent graduate", "Working professional"]
        stage = st.selectbox("Current stage", stages, index=stages.index(profile.get("stage", "4th year")) if profile.get("stage", "4th year") in stages else 3)
        weekly_hours = st.slider("Available learning hours per week", 1, 40, int(profile.get("weekly_hours", 6)))
        career_goal = st.text_area("Career goal", value=profile.get("career_goal", "Build job-ready skills and a portfolio project."), height=90)
        interests = st.text_input("Interests (comma-separated)", value=profile.get("interests", "AI, software development"))
        st.markdown("**Skills you can currently demonstrate**")
        skills = st.multiselect("Select current skills", all_skills, default=[s for s in profile.get("skills", []) if s in all_skills])
        submitted = st.form_submit_button("Save profile", type="primary", use_container_width=True)
        if submitted:
            if not name.strip():
                st.error("Please enter a display name.")
            else:
                save_profile({
                    "name": name.strip(), "target_role": target_role, "stage": stage,
                    "weekly_hours": weekly_hours, "career_goal": career_goal.strip(),
                    "interests": interests.strip(), "skills": skills,
                })
                st.success("Profile saved.")
                safe_rerun()
    st.caption("Profile settings personalize local recommendations. Avoid entering passwords, financial information, or other sensitive data.")

elif selected == "Personal Growth":
    hero("BUILD CONSISTENCY", "Personal Growth", "Set small goals, track completion, and reflect on what you learned.")
    goals = list_goals()
    completed = sum(g["status"] == "Completed" for g in goals)
    open_count = len(goals) - completed
    m1, m2, m3 = st.columns(3)
    m1.metric("Total goals", len(goals))
    m2.metric("Completed", completed)
    m3.metric("Completion rate", f"{round(100*completed/len(goals)) if goals else 0}%")
    with st.expander("＋ Create a growth goal", expanded=not bool(goals)):
        with st.form("goal_form", clear_on_submit=True):
            title = st.text_input("Goal title", placeholder="Complete SQL joins practice")
            category = st.selectbox("Category", ["Technical skill", "Project", "Career preparation", "Communication", "Wellbeing"])
            due = st.date_input("Target date", value=date.today() + timedelta(days=7), min_value=date.today())
            notes = st.text_area("Success criteria / notes", placeholder="How will you know this is complete?")
            add = st.form_submit_button("Add goal", type="primary")
            if add:
                if not title.strip():
                    st.error("A goal title is required.")
                else:
                    add_goal(title.strip(), category, due.isoformat(), notes.strip())
                    st.success("Goal added.")
                    safe_rerun()
    st.markdown("### Your goals")
    if not goals:
        st.info("No goals yet. Create one small, measurable goal above.")
    for g in goals:
        with st.container(border=True):
            c1, c2, c3 = st.columns([4, 1.3, 1])
            with c1:
                mark = "✅" if g["status"] == "Completed" else "◻️"
                st.markdown(f"**{mark} {g['title']}**")
                st.caption(f"{g['category']} · Due {g['due_date'] or 'not set'}")
                if g.get("notes"):
                    st.write(g["notes"])
            with c2:
                st.caption(g["status"])
                if g["status"] == "Completed":
                    if st.button("Reopen", key=f"reopen_{g['id']}"):
                        update_goal_status(g["id"], "Open"); safe_rerun()
                else:
                    if st.button("Mark done", key=f"done_{g['id']}"):
                        update_goal_status(g["id"], "Completed"); safe_rerun()
            with c3:
                if st.button("Delete", key=f"delete_{g['id']}"):
                    delete_goal(g["id"]); safe_rerun()
    st.divider()
    st.markdown("### Weekly reflection")
    with st.form("reflection_form", clear_on_submit=True):
        week_of = st.date_input("Week starting", value=date.today() - timedelta(days=date.today().weekday()))
        wins = st.text_area("What went well?", placeholder="One thing you completed or understood…")
        blockers = st.text_area("What was difficult?", placeholder="A blocker and how you might address it…")
        next_step = st.text_input("One next step", placeholder="The smallest useful action for next week")
        reflect = st.form_submit_button("Save reflection")
        if reflect:
            if not (wins.strip() or blockers.strip() or next_step.strip()):
                st.error("Add at least one reflection field.")
            else:
                add_reflection(week_of.isoformat(), wins.strip(), blockers.strip(), next_step.strip())
                st.success("Reflection saved.")
                safe_rerun()
    reflections = list_reflections()
    if reflections:
        with st.expander("Previous reflections"):
            for r in reflections:
                st.markdown(f"**Week of {r['week_of']}**")
                if r["wins"]: st.write(f"**Wins:** {r['wins']}")
                if r["blockers"]: st.write(f"**Blockers:** {r['blockers']}")
                if r["next_step"]: st.write(f"**Next step:** {r['next_step']}")
                st.divider()

st.markdown("---")
st.caption("Career Mentor prototype · Recommendations are educational guidance, not a guarantee of employment or placement.")
