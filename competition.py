from urls import PETLJA_URL, ARENA_URL
from auth import get_csrf_token
from problem import get_problem_name
from datetime import datetime
import re
from bs4 import BeautifulSoup


def get_competition_id(session, alias):
    page = session.get(f"{ARENA_URL}/competition/{alias}")
    if page.status_code == 404:
        raise ValueError(f"Competition with alias {alias} does not exist")

    soup = BeautifulSoup(page.text, "html.parser")
    competition_id = soup.find("button", attrs={"id": "ciRun"})["data-competition-id"]
    return competition_id


def get_added_problem_ids(session, competition_id):
    page = session.get(f"{PETLJA_URL}/cpanel/CompetitionTasks/{competition_id}")
    soup = BeautifulSoup(page.text, "html.parser")
    options = soup.find("select", {"id": "selectTask"}).find_all("option")
    return [o["value"] for o in options]


def create_competition(
    session, name, alias=None, description=None, start_date=None, end_date=None
):
    if alias is None:
        alias = ""
    if description is None:
        description = ""
    if start_date is None:
        start_date = datetime.now()
    if end_date is None:
        end_date = ""

    regex = re.compile(r"^[a-z0-9-]+$")
    if not regex.match(alias):
        raise NameError(
            f"Invalid alias {alias}: must contain only lowercase alphanumeric characters and dashes"
        )

    url = f"{PETLJA_URL}/cpanel/CreateCompetition"
    page = session.get(url)
    csrf_token = get_csrf_token(page.text)
    resp = session.post(
        url,
        data={
            "Name": name,
            "Alias": alias,
            "Description": description,
            "StartDate": start_date,
            "EndDate": end_date,
            "HasNotEndDate": [True, False],  # Not sure what this field does
            "__RequestVerificationToken": csrf_token,
        },
        allow_redirects=False,
    )

    if resp.status_code == 302:
        header_loc = resp.headers["Location"]  # /cpanel/CompetitionSettings/:comp_id
        comp_id = header_loc.split("/")[-1]
        return comp_id
    elif resp.status_code == 200:
        raise ValueError("Competition alias already exists")
    else:
        raise Exception(f"Unknown error, status code {resp.status_code}")


def add_problem(session, competition_id, problem_id, scoring=None):
    already_added = get_added_problem_ids(session, competition_id)
    if problem_id in already_added:
        return

    url = f"{PETLJA_URL}/api/dashboard/competitions/problems/add"
    problem_name = get_problem_name(session, problem_id)
    resp = session.post(
        url,
        json={
            "competitionId": competition_id,
            "problemId": problem_id,
            "name": problem_name,
            # "sortOrder": 0, # Seems to be optional
        },
    )

    # TODO: Check for errors
