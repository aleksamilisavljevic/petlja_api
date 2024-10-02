import pytest
import requests
from bs4 import BeautifulSoup

import petlja_api as petlja
from petlja_api.urls import CPANEL_URL


def test_create_problem(created_prob):
    _, alias = created_prob
    res = requests.get(f"https://petlja.org/problems/{alias}")
    assert res.status_code == 200


def test_create_already_existing_prob(sess):
    with pytest.raises(ValueError):
        petlja.create_problem(sess, "Postojeci problem", "osdrz23odbijanje")


def test_upload_testcases(sess, created_prob, testcases):
    id, _ = created_prob
    petlja.upload_testcases(sess, id, testcases)


def test_upload_statement(sess, created_prob, statement):
    id, _ = created_prob
    petlja.upload_statement(sess, id, statement)


def _get_cpanel_problem_ids(sess):
    page = sess.get(f"{CPANEL_URL}/Problems")
    soup = BeautifulSoup(page.text, "html.parser")
    problems_list = soup.select(".list-group-item")
    # items are of format <li id=title-{id} class="list-group-item">
    problem_ids = [p.get("id").removeprefix("title-") for p in problems_list]
    return problem_ids


def test_delete_problem(sess, created_prob):
    pid, _ = created_prob
    petlja.delete_problem(sess, pid)
    # For some reason the problem isn't actually deleted
    # just unlisted from the problems page
    problem_ids = _get_cpanel_problem_ids(sess)
    assert pid not in problem_ids
