from auth import get_csrf_token
from urls import PETLJA_URL
from bs4 import BeautifulSoup


def get_problem_id(session, uniqueid):
    problems_page = session.get(f"{PETLJA_URL}/problems/{uniqueid}")
    soup = BeautifulSoup(problems_page.text, "html.parser")
    problem_id = soup.find("button", attrs={"class": "btn-solution-submit"})[
        "data-problem-id"
    ]
    return problem_id


def create_problem(session, name, uniqueid):
    create_problem_page = session.get(f"{PETLJA_URL}/cpanel/CreateTask")
    csrf_token = get_csrf_token(create_problem_page.text)
    create_task_resp = session.post(
        f"{PETLJA_URL}/cpanel/CreateTask",
        data={
            "Name": name,
            "UniqueId": uniqueid,
            "Type": "0",
            "__RequestVerificationToken": csrf_token,
        },
    )


def upload_testcases(session, problem_id, testcases_path):
    upload_testcases_page = session.get(
        f"{PETLJA_URL}/cpanel/EditProblem/{problem_id}?tab=testcases"
    )
    csrf_token = get_csrf_token(upload_testcases_page.text)
    with open(testcases_path, "rb") as zip:
        upload_testcases_resp = session.post(
            f"{PETLJA_URL}/cpanel/EditProblem/{problem_id}",
            files={"TestCases": zip},
            data={
                "PostAction": "EditTestCases",
                "__RequestVerificationToken": csrf_token,
            },
            allow_redirects=False,
        )
