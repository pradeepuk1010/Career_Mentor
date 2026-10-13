# Career Mentor — Student Growth OS

A professional Streamlit prototype that helps a student plan role-specific skills, find learning resources, manage profile settings, and track personal growth.

## Four app sections

1. **Dashboard + AI Career Coach** — role-skill coverage, suggested next actions, weekly starter plan, and a coaching interface.
2. **Learning Sources** — searchable curated links with free-only and skill-gap filters.
3. **Profile Settings** — target role, academic stage, skills, weekly time budget, interests, and career goal.
4. **Personal Growth** — measurable goals, completion tracking, and weekly reflections.

## AI behavior — read before presenting

- The app supports **optional Gemini API coaching** when `GEMINI_API_KEY` is configured.
- Without a key, the AI Coach uses a **local rule-based fallback**. This mode requires no external API and keeps the demo runnable.
- Do not describe the fallback as a large language model. In the presentation, explain both modes accurately.

## Technology and cloud design

- **Development/evaluation:** Google Colab (hosted notebook runtime) and local Python.
- **Source control:** GitHub repository.
- **Application hosting:** Streamlit Community Cloud (managed application hosting; PaaS-like).
- **Application:** Python + Streamlit.
- **Visualization:** Plotly.
- **Database:** SQLite for prototype profile, goals, and reflections.
- **Optional AI service:** Gemini API, only if a key is configured.

This is **not an AWS deployment**. Google Colab is used for evaluation, not for hosting the continuously available Streamlit web app.

## Run locally

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL printed by Streamlit (normally `http://localhost:8501`).

## Enable Gemini coaching (optional)

Set an API key as an environment variable before starting Streamlit:

```bash
# Windows PowerShell
$env:GEMINI_API_KEY="YOUR_KEY"
streamlit run app.py

# macOS/Linux
export GEMINI_API_KEY="YOUR_KEY"
streamlit run app.py
```

For Streamlit Community Cloud, add `GEMINI_API_KEY` under **App → Settings → Secrets**. Never commit keys to GitHub. The app still runs without the key.

## Deploy on Streamlit Community Cloud

1. Create a GitHub repository, for example `career-mentor-ft3`.
2. Upload `app.py`, `database.py`, `mentor_engine.py`, `requirements.txt`, `.streamlit/config.toml`, and the README. Keep `tests/` for reproducibility.
3. Sign in to Streamlit Community Cloud and connect GitHub.
4. Create an app using the repository, branch, and main file path `app.py`.
5. Wait for the build, open the generated URL, and test all four sections.
6. If enabling Gemini, add the API key through Streamlit Secrets—not source code.
7. Capture screenshots of the actual working deployment for the FT-III presentation.

## Storage and security limitations

SQLite is suitable for a small demonstration, but a local database file on a hosted app may not persist across restarts, rebuilds, or environment replacement. This version does not provide authentication or per-user data isolation. Do not enter sensitive personal data. For durable multi-user production use, integrate a managed database, authentication, backups, and appropriate access controls.

## Evaluation

The companion Google Colab notebook (`Career_Mentor_Evaluation.ipynb`) evaluates deterministic recommendation logic using synthetic test profiles. It reports computed skill-gap coverage, recommendation validity, and basic runtime measurements. These are prototype test results, **not** evidence of employment outcomes or a production load test. Run the notebook to produce the actual output values for your report.

## Tests

From the project folder:

```bash
pytest -q
```

Tests cover profile persistence, goal lifecycle, reflection persistence, and role-specific recommendations.

## FT-III mapping

- **Problem analysis & cloud design (2 marks):** problem, requirements, architecture, cloud service model justification.
- **Implementation & technical execution (8 marks):** working Streamlit app, four sections, SQLite storage, GitHub source control, managed app deployment, and security caveats.
- **Results & technical evaluation (2 marks):** run the companion Colab notebook and include its real output; do not invent latency or cost numbers.
- **Viva (3 marks):** explain why Streamlit hosting is used, the difference between Colab and deployment, rule-based vs Gemini coaching, SQLite persistence limitations, and future production improvements.
