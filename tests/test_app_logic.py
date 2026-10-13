import json
import pytest
import database
from mentor_engine import build_career_snapshot, recommend_actions, ROLE_SKILLS

@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    monkeypatch.setenv("CAREER_MENTOR_DB", str(tmp_path / "test.db"))
    database.init_db()

def test_profile_round_trip():
    data = database.load_profile()
    data["name"] = "Test Student"
    data["skills"] = ["Python", "Git", "Python"]
    database.save_profile(data)
    loaded = database.load_profile()
    assert loaded["name"] == "Test Student"
    assert loaded["skills"] == ["Git", "Python"]

def test_goal_lifecycle():
    goal_id = database.add_goal("Practice SQL", "Technical skill", "2030-01-01", "Joins")
    assert any(g["id"] == goal_id for g in database.list_goals())
    database.update_goal_status(goal_id, "Completed")
    assert next(g for g in database.list_goals() if g["id"] == goal_id)["status"] == "Completed"
    database.delete_goal(goal_id)
    assert not any(g["id"] == goal_id for g in database.list_goals())

def test_reflection_round_trip():
    database.add_reflection("2030-01-07", "Finished a task", "Time", "Plan earlier")
    result = database.list_reflections()
    assert result[0]["week_of"] == "2030-01-07"
    assert result[0]["next_step"] == "Plan earlier"

def test_recommendations_match_role_gaps():
    profile = {"target_role":"Data Analyst", "skills":["SQL","Python"]}
    snapshot = build_career_snapshot(profile)
    actions = recommend_actions(profile)
    assert snapshot["gaps"]
    assert actions
    assert actions[0]["skill"] == snapshot["gaps"][0]
