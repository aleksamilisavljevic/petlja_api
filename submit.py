from auth import get_session
from urls import ARENA_URL
import time


def submit(competition_id, problem_id, source, language_id):
    session = None
    while session is None:
        try:
            session = get_session()
        except PermissionError as e:
            print(e)

    submit = session.post(
        f"{ARENA_URL}/api/competition/submit-competition-problem",
        json={
            "competitionId": competition_id,
            "problemId": problem_id,
            "source": source,
            "languageId": language_id,
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
