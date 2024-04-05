from bs4 import BeautifulSoup

from .auth import get_csrf_token
from .urls import CPANEL_URL, PROBLEMS_URL


def get_problem_id(session, alias):
    page = session.get(f"{PROBLEMS_URL}/{alias}")
    if page.status_code == 404:
        raise ValueError(f"Problem with alias {alias} does not exist")

    soup = BeautifulSoup(page.text, "html.parser")
    problem_id = soup.find("button", attrs={"class": "btn-solution-submit"})[
        "data-problem-id"
    ]
    return problem_id


def get_problem_name(session, problem_id):
    page = session.get(f"{CPANEL_URL}/EditProblem/{problem_id}")
    if page.status_code == 404:
        raise ValueError(f"Problem with id {problem_id} does not exist")

    soup = BeautifulSoup(page.text, "html.parser")
    problem_name = soup.find("input", attrs={"id": "Problem_Name"})["value"]
    return problem_name


def create_problem(session, name, alias):
    if not alias or not alias.isalnum() or not alias.islower():
        raise NameError(
            f"Invalid problem alias {alias}: must be alphanumeric and lowercase"
        )

    create_problem_page = session.get(f"{CPANEL_URL}/CreateTask")
    csrf_token = get_csrf_token(create_problem_page.text)
    resp = session.post(
        f"{CPANEL_URL}/CreateTask",
        data={
            "Name": name,
            "UniqueId": alias,
            "Type": "0",
            "__RequestVerificationToken": csrf_token,
        },
        allow_redirects=False
    )
    if resp.status_code == 302:
        return get_problem_id(session, alias)
    elif resp.status_code == 200:
        raise ValueError("Problem alias already exists")
    else:
        raise RuntimeError(
            "Unknown error while creating problem (status code {resp.status_code})"
        )


def check_testcase_upload(page):
    soup = BeautifulSoup(page.text, "html.parser")
    error = soup.find("div", attrs={"class": "validation-summary-errors"})
    if error:
        errmsg = f"Testcase upload failed: {error.text.strip()}"
        if error.text.strip() == "UserIdNotFound":
            errmsg += " (Is the zip file in the correct format?)"
        raise ValueError(errmsg)


def upload_testcases(session, problem_id, testcases_path):
    page = session.get(f"{CPANEL_URL}/EditProblem/{problem_id}?tab=testcases")
    csrf_token = get_csrf_token(page.text)
    with open(testcases_path, "rb") as zipfile:
        resp = session.post(
            f"{CPANEL_URL}/EditProblem/{problem_id}",
            files={"TestCases": zipfile},
            data={
                "PostAction": "EditTestCases",
                "__RequestVerificationToken": csrf_token,
            },
        )
    # Have to scrape the response page to check for errors
    # because the response is 302 even if there is an error
    check_testcase_upload(resp)


def upload_statement(session, problem_id, statement_path):
    page = session.get(f"{CPANEL_URL}/EditProblem/{problem_id}?tab=statement")
    csrf_token = get_csrf_token(page.text)
    with open(statement_path, encoding="utf-8") as statement:
        resp = session.post(
            f"{CPANEL_URL}/EditProblem/{problem_id}",
            data={
                "Problem.ProblemStatementMD": statement.read(),
                "PostAction": "EditStatement",
                "Problem.MDSupported": "true",
                "__RequestVerificationToken": csrf_token,
            },
            allow_redirects=False,
        )
    # TODO: check for errors
