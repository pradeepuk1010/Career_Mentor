"""Transparent role/skill recommendation logic plus optional Gemini coaching."""
import os

ROLE_SKILLS = {
    "Software Engineer": ["Python", "Problem Solving", "Data Structures", "SQL", "Git", "APIs", "Testing", "Cloud Basics"],
    "Data Analyst": ["SQL", "Python", "Statistics", "Data Visualization", "Excel", "Communication", "Power BI"],
    "AI/ML Engineer": ["Python", "Statistics", "Machine Learning", "Data Handling", "Model Evaluation", "Git", "APIs", "Cloud Basics"],
    "Cloud Engineer": ["Linux", "Networking", "Cloud Basics", "Git", "Security Basics", "Scripting", "Containers"],
    "Frontend Developer": ["HTML/CSS", "JavaScript", "Accessibility", "APIs", "Git", "Testing", "UI Design"],
}
SKILL_CATALOG = sorted({skill for values in ROLE_SKILLS.values() for skill in values} | {
    "Communication", "Teamwork", "Resume Writing", "Interview Practice", "System Design"
})
LEARNING_RESOURCES = [
    {"title":"Python Tutorial","provider":"Python Software Foundation","skill":"Python","level":"Beginner","format":"Documentation","cost":"Free","url":"https://docs.python.org/3/tutorial/","description":"Official language tutorial with examples and core concepts."},
    {"title":"SQLBolt","provider":"SQLBolt","skill":"SQL","level":"Beginner","format":"Interactive lessons","cost":"Free","url":"https://sqlbolt.com/","description":"Short interactive lessons for SQL queries and relational concepts."},
    {"title":"Git Book","provider":"Pro Git","skill":"Git","level":"Beginner–Intermediate","format":"Book / documentation","cost":"Free","url":"https://git-scm.com/book/en/v2","description":"Version control concepts, branching, collaboration, and workflows."},
    {"title":"MDN Web Docs","provider":"Mozilla","skill":"HTML/CSS","level":"Beginner–Intermediate","format":"Documentation","cost":"Free","url":"https://developer.mozilla.org/","description":"Reference and learning guides for web standards and browser development."},
    {"title":"JavaScript Guide","provider":"MDN Web Docs","skill":"JavaScript","level":"Beginner–Intermediate","format":"Documentation","cost":"Free","url":"https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide","description":"Structured introduction to JavaScript language features."},
    {"title":"Google Machine Learning Crash Course","provider":"Google","skill":"Machine Learning","level":"Beginner–Intermediate","format":"Course","cost":"Free","url":"https://developers.google.com/machine-learning/crash-course","description":"Interactive introduction to machine-learning concepts and evaluation."},
    {"title":"Kaggle Learn","provider":"Kaggle","skill":"Statistics","level":"Beginner","format":"Micro-courses","cost":"Free","url":"https://www.kaggle.com/learn","description":"Short practical courses covering data, Python, and ML fundamentals."},
    {"title":"Microsoft Learn: Power BI","provider":"Microsoft","skill":"Power BI","level":"Beginner–Intermediate","format":"Learning paths","cost":"Free","url":"https://learn.microsoft.com/en-us/training/powerplatform/power-bi/","description":"Guided learning paths for building reports and data models."},
    {"title":"CS50's Introduction to Computer Science","provider":"Harvard / edX","skill":"Problem Solving","level":"Beginner","format":"Course","cost":"Free to audit","url":"https://cs50.harvard.edu/x/","description":"Problem-solving foundations and computer-science concepts."},
    {"title":"Google Cloud Skills Boost","provider":"Google Cloud","skill":"Cloud Basics","level":"Beginner–Intermediate","format":"Learning platform","cost":"Mixed","url":"https://www.cloudskillsboost.google/","description":"Cloud learning paths; some labs or subscriptions may be paid."},
    {"title":"Linux Journey","provider":"Linux Journey","skill":"Linux","level":"Beginner","format":"Guided lessons","cost":"Free","url":"https://linuxjourney.com/","description":"Introductory Linux and command-line learning material."},
    {"title":"Postman Learning Center","provider":"Postman","skill":"APIs","level":"Beginner–Intermediate","format":"Documentation","cost":"Free","url":"https://learning.postman.com/","description":"Learn to send requests, inspect responses, and test APIs."},
    {"title":"OWASP Top 10","provider":"OWASP","skill":"Security Basics","level":"Intermediate","format":"Reference","cost":"Free","url":"https://owasp.org/www-project-top-ten/","description":"Awareness of common web application security risks."},
    {"title":"Docker Get Started","provider":"Docker","skill":"Containers","level":"Beginner","format":"Tutorial","cost":"Free","url":"https://docs.docker.com/get-started/","description":"Container fundamentals and a guided first workflow."},
    {"title":"Google SRE Workbook","provider":"Google","skill":"Networking","level":"Intermediate","format":"Book / web","cost":"Free","url":"https://sre.google/workbook/table-of-contents/","description":"Operational reliability concepts, including monitoring and networking context."},
    {"title":"Scikit-learn User Guide","provider":"scikit-learn","skill":"Model Evaluation","level":"Intermediate","format":"Documentation","cost":"Free","url":"https://scikit-learn.org/stable/user_guide.html","description":"Model selection, metrics, validation, and practical ML workflows."},
    {"title":"Test Automation University","provider":"Applitools","skill":"Testing","level":"Beginner–Intermediate","format":"Courses","cost":"Free","url":"https://testautomationu.applitools.com/","description":"Courses on software testing and automation."},
    {"title":"Nielsen Norman Group Articles","provider":"NN/g","skill":"UI Design","level":"Beginner–Intermediate","format":"Articles","cost":"Free","url":"https://www.nngroup.com/articles/","description":"Research-based usability and interaction design articles."},
    {"title":"Microsoft Learn: Azure Fundamentals","provider":"Microsoft","skill":"Cloud Basics","level":"Beginner","format":"Learning path","cost":"Free","url":"https://learn.microsoft.com/en-us/training/paths/azure-fundamentals-describe-cloud-concepts/","description":"Cloud concepts and core cloud service models."},
    {"title":"Interview Preparation Kit","provider":"HackerRank","skill":"Interview Practice","level":"Intermediate","format":"Practice challenges","cost":"Free","url":"https://www.hackerrank.com/interview/interview-preparation-kit","description":"Structured practice for common technical interview topics."},
]

ACTION_LIBRARY = {
    "Python": ("Build a small Python utility", "Write a script that reads a CSV and summarizes three useful statistics.", 2),
    "Problem Solving": ("Practice problem solving", "Solve two problems and write down the approach and complexity.", 2),
    "Data Structures": ("Revise core data structures", "Implement a stack, queue, and hash-map use case; test edge cases.", 2),
    "SQL": ("Practice SQL queries", "Write queries using filtering, joins, aggregation, and grouping.", 2),
    "Git": ("Publish a clean repository", "Add a README, requirements, meaningful commits, and setup instructions.", 1),
    "APIs": ("Build an API mini-demo", "Call a public API and handle success, empty, and error responses.", 2),
    "Testing": ("Add automated tests", "Write tests for normal, boundary, and invalid input cases.", 2),
    "Cloud Basics": ("Map a cloud deployment", "Draw the client, managed app host, application, and storage components.", 1),
    "Machine Learning": ("Train a baseline model", "Use a held-out split and report a metric appropriate to the task.", 3),
    "Statistics": ("Review statistics with examples", "Explain mean, variance, sampling, and correlation with a small dataset.", 2),
    "Data Visualization": ("Create one decision-focused chart", "Build a chart and state the decision it supports.", 2),
    "Power BI": ("Create a small Power BI report", "Load a tidy dataset and build two measures plus a filtered visual.", 2),
    "Linux": ("Practice command-line basics", "Use navigation, files, permissions, and process commands in a safe environment.", 1),
    "Networking": ("Review networking fundamentals", "Explain DNS, HTTP, TCP, ports, and a request path.", 1),
    "Security Basics": ("Run a security checklist", "Review secrets, input validation, least privilege, and data exposure.", 1),
    "Scripting": ("Automate a repeatable task", "Create a script that validates files and reports actionable errors.", 2),
    "Containers": ("Containerize a demo app", "Follow the official Docker getting-started tutorial.", 2),
    "HTML/CSS": ("Build a responsive page", "Create a semantic page with a mobile-friendly layout.", 2),
    "JavaScript": ("Add an interactive feature", "Build and test one accessible client-side interaction.", 2),
    "Accessibility": ("Audit a UI flow", "Check keyboard navigation, labels, contrast, and error messages.", 1),
    "UI Design": ("Review one interface", "Identify one usability issue and prototype an improvement.", 1),
    "Communication": ("Explain a project clearly", "Prepare a 60-second explanation of problem, approach, result, and limitation.", 1),
    "Resume Writing": ("Update one resume bullet", "Use action + technical method + measurable evidence; do not invent metrics.", 1),
    "Interview Practice": ("Run a mock interview", "Answer one technical and one behavioral question aloud.", 1),
    "System Design": ("Sketch a small system", "Describe components, data flow, bottlenecks, and trade-offs.", 2),
    "Data Handling": ("Prepare a clean dataset", "Check missing values, types, duplicates, and leakage risks.", 2),
    "Model Evaluation": ("Compare model baselines", "Choose a suitable metric and compare at least two baselines fairly.", 2),
    "Excel": ("Practice spreadsheet analysis", "Use filters, lookup, aggregation, and a pivot table on sample data.", 2),
    "Teamwork": ("Document a team hand-off", "Write clear ownership, status, and next steps for a small task.", 1),
}

def build_career_snapshot(profile):
    role = profile.get("target_role", "Software Engineer")
    required = ROLE_SKILLS.get(role, ROLE_SKILLS["Software Engineer"])
    skills = set(profile.get("skills", []))
    selected = len([s for s in required if s in skills])
    return {
        "role": role,
        "required_skills": required,
        "selected_skills": sorted(skills),
        "gaps": [s for s in required if s not in skills],
        "readiness": round(100 * selected / len(required)) if required else 0,
    }

def recommend_actions(profile, limit=8):
    snap = build_career_snapshot(profile)
    gaps = snap["gaps"]
    if not gaps:
        preferred = ["Project", "Interview Practice", "System Design"]
        gaps = [s for s in preferred if s in ACTION_LIBRARY]
    actions = []
    for skill in gaps:
        title, reason, hours = ACTION_LIBRARY.get(
            skill, (f"Practice {skill}", f"Complete a small exercise that demonstrates {skill}.", 1)
        )
        actions.append({"skill": skill, "title": title, "reason": reason, "hours": hours})
    return actions[:limit]

def get_ai_coaching(profile, user_prompt, actions):
    """Use Gemini only when an API key is configured; otherwise use transparent local rules."""
    key = os.getenv("GEMINI_API_KEY", "")
    try:
        import streamlit as st
        key = key or st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        pass
    if key:
        try:
            from google import genai
            client = genai.Client(api_key=key)
            prompt = f"""You are a careful student career coach. Use only the provided profile and actions.
Do not claim job placement or fabricate facts. Give a realistic short plan with concrete steps.
Profile: {profile}
Suggested actions: {actions[:5]}
Student question: {user_prompt or 'Give me a practical plan for this week.'}
Answer in concise bullets. Mention assumptions if needed."""
            result = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
            if getattr(result, "text", None):
                return result.text, "Gemini API"
        except Exception as exc:
            # Do not expose keys or raw provider errors to end users.
            fallback = _local_coaching(profile, user_prompt, actions)
            return fallback + "\n\nGemini could not be reached; this answer uses the local fallback.", "Local fallback"
    return _local_coaching(profile, user_prompt, actions), "Local rule-based coach"

def _local_coaching(profile, user_prompt, actions):
    name = profile.get("name") or "there"
    hours = int(profile.get("weekly_hours", 6))
    role = profile.get("target_role", "your target role")
    goal = profile.get("career_goal", "build job-ready skills")
    lines = [
        f"{name}, your current target is **{role}**.",
        f"Your stated goal: {goal}",
        f"Plan within your {hours}-hour weekly budget:",
    ]
    if actions:
        for i, item in enumerate(actions[:3], 1):
            lines.append(f"{i}. **{item['title']}** ({min(item['hours'], max(hours, 1))} hour(s)): {item['reason']}")
    else:
        lines.append("Choose one portfolio project and document what it demonstrates.")
    if user_prompt.strip():
        lines.append(f"**Your question:** {user_prompt.strip()}")
        lines.append("Prioritize one measurable outcome, then review progress before adding another task.")
    lines.append("These are heuristic suggestions; adjust them to your course requirements and actual skill level.")
    return "\n\n".join(lines)
