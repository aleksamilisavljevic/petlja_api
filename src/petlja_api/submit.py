from .urls import ARENA_URL
import time

# Weird Petlja API language IDs
LANGUAGE_IDS = {
    ".c": 10,
    ".cs": 1,
    ".cpp": 2,
    ".java": 3,
    ".m": 7,
    ".pas": 4,
    ".py": 9,
}

TIMEOUT = 30


def submit_solution(session, competition_id, problem_id, source_path):
    with open(source_path) as source_file:
        source = source_file.read()

    extension = source_path.suffix
    submit_res = session.post(
        f"{ARENA_URL}/api/competition/submit-competition-problem",
        json={
            "competitionId": competition_id,
            "problemId": problem_id,
            "source": source,
            "languageId": LANGUAGE_IDS[extension],
        },
    )
    success = submit_res.json()["succeeded"]
    if not success:
        error = submit_res.json()["errors"][0]["description"]
        raise Exception(error)
    submission_id = submit_res.json()["value"]
    # Polling the server every x seconds
    # Better solution may exist
    tries = 0
    while tries < TIMEOUT:
        submission_data = session.post(
            f"{ARENA_URL}/api/competition/submissions",
            json={
                "competitionId": competition_id,
                "idStamp": submission_id,
                "loadNew": True,
            },
        )
        score = submission_data.json()["value"]["item1"][0]["score"]
        if score != '-':
            return score
        time.sleep(1)

    raise TimeoutError
