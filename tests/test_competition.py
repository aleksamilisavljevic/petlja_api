import pytest
from bs4 import BeautifulSoup

import petlja_api as petlja
from petlja_api.urls import CPANEL_URL


def test_upload_scoring(sess, comp_with_problems, scoring):
    cid, _ = comp_with_problems
    pid = petlja.get_added_problem_ids(sess, cid)[0]
    petlja.upload_scoring(sess, cid, pid, scoring)


def test_get_competition_id(sess, empty_comp):
    cid, alias = empty_comp
    assert petlja.get_competition_id(sess, alias) == cid


def test_get_competition_id_nonexistent(sess):
    with pytest.raises(ValueError):
        petlja.get_competition_id(sess, "qurvoqireouqh")


def test_submit_unallowed_lang(sess, comp_with_problems, created_prob, src_py):
    cid, _ = comp_with_problems
    pid, _ = created_prob
    with pytest.raises(Exception):
        petlja.submit_solution(sess, cid, pid, src_py)


def test_delete_competition(sess, empty_comp):
    cid, _ = empty_comp
    petlja.delete_competition(sess, cid)
    with pytest.raises(ValueError):
        petlja.get_competition_id(sess, cid)


def test_set_time_limit(sess, created_prob):
    pid, _ = created_prob
    petlja.set_time_limit(sess, pid, 42)
    page = sess.get(f"{CPANEL_URL}/EditProblem/{pid}")
    soup = BeautifulSoup(page.text, "html.parser")
    time_limit = soup.select_one("#Problem_TimeLimit").get("value")
    assert time_limit == "42"


def test_set_memory_limit(sess, created_prob):
    pid, _ = created_prob
    petlja.set_memory_limit(sess, pid, 42)
    page = sess.get(f"{CPANEL_URL}/EditProblem/{pid}")
    soup = BeautifulSoup(page.text, "html.parser")
    memory_limit = soup.select_one("#Problem_MemoryLimit").get("value")
    assert memory_limit == "42"
