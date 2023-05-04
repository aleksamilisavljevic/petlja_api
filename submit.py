from urls import ARENA_URL
import time

# Weird Petlja API language IDs
LANGUAGE_IDS = {
    "c": 10,
    "cs": 1,
    "cpp": 2,
    "java": 3,
    "m": 7,
    "pas": 4,
    "py": 9,
}


def submit(session, competition_id, problem_id, source_path):
    with open(source_path) as source_file:
        source = source_file.read()

    extension = source_path.split(".")[-1]
    submit = session.post(
        f"{ARENA_URL}/api/competition/submit-competition-problem",
        json={
            "competitionId": competition_id,
            "problemId": problem_id,
            "source": source,
            "languageId": LANGUAGE_IDS[extension],
        },
    )
    submission_id = submit.json()["value"]
    time.sleep(2)  # FIXME wait until evaluation is finished
    submission_data = session.post(
        f"{ARENA_URL}/api/competition/submissions",
        json={
            "competitionId": competition_id,
            "idStamp": submission_id,
            "loadNew": "true",
        },
    )
    score = submission_data.json()["value"]["item1"][0]["score"]
    return score
