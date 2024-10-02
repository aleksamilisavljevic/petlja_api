import pytest

import petlja_api as petlja


def test_submit_ok(sess, comp_with_problems, src_ok):
    cid, _ = comp_with_problems
    pid = petlja.get_added_problem_ids(sess, cid)[0]
    score = petlja.submit_solution(sess, cid, pid, src_ok)
    assert int(score) > 0


def test_submit_wa(sess, comp_with_problems, src_wa):
    cid, _ = comp_with_problems
    pid = petlja.get_added_problem_ids(sess, cid)[0]
    score = petlja.submit_solution(sess, cid, pid, src_wa)
    assert score == "0"


@pytest.mark.slow
def test_submit_tle(sess, comp_with_problems, src_tle):
    cid, _ = comp_with_problems
    pid = petlja.get_added_problem_ids(sess, cid)[0]
    score = petlja.submit_solution(sess, cid, pid, src_tle)
    assert score == "0"
