from urls import PETLJA_URL
from auth import get_csrf_token
from problem import get_problem_name
from datetime import datetime
import re


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
        raise ValueError(
            "Alias must contain only lowercase alphanumeric characters and dashes"
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
