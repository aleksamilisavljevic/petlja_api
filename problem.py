from auth import get_csrf_token
from urls import PETLJA_URL
from bs4 import BeautifulSoup


def get_problem_id(session, alias):
    page = session.get(f"{PETLJA_URL}/problems/{alias}")
    soup = BeautifulSoup(page.text, "html.parser")
    problem_id = soup.find("button", attrs={"class": "btn-solution-submit"})[
        "data-problem-id"
    ]
    return problem_id


def get_problem_name(session, problem_id):
    page = session.get(f"{PETLJA_URL}/cpanel/EditProblem/{problem_id}")
    soup = BeautifulSoup(page.text, "html.parser")
    problem_name = soup.find("input", attrs={"id": "Problem_Name"})["value"]
    return problem_name


def create_problem(session, name, alias):
    create_problem_page = session.get(f"{PETLJA_URL}/cpanel/CreateTask")
    csrf_token = get_csrf_token(create_problem_page.text)
    resp = session.post(
        f"{PETLJA_URL}/cpanel/CreateTask",
        data={
            "Name": name,
            "UniqueId": alias,
            "Type": "0",
            "__RequestVerificationToken": csrf_token,
        },
    )
    return get_problem_id(session, alias)


def upload_testcases(session, problem_id, testcases_path):
    page = session.get(f"{PETLJA_URL}/cpanel/EditProblem/{problem_id}?tab=testcases")
    csrf_token = get_csrf_token(page.text)
    with open(testcases_path, "rb") as zip:
        resp = session.post(
            f"{PETLJA_URL}/cpanel/EditProblem/{problem_id}",
            files={"TestCases": zip},
            data={
                "PostAction": "EditTestCases",
                "__RequestVerificationToken": csrf_token,
            },
            allow_redirects=False,
        )
