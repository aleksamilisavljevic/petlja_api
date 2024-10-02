import os
import uuid

import pytest
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

import petlja_api as petlja
from petlja_api.urls import CPANEL_URL

load_dotenv()


@pytest.fixture
def sess():
    return petlja.login(os.environ["PETLJA_USER"], os.environ["PETLJA_PASS"])


@pytest.fixture
def created_prob(sess):
    uid = uuid.uuid4().hex
    alias = f"testprob{uid}"
    pid = petlja.create_problem(sess, "Test zadatak", alias)
    yield pid, alias
    petlja.delete_problem(sess, pid)


@pytest.fixture
def empty_comp(sess):
    uid = uuid.uuid4().hex
    alias = f"testcomp{uid}"
    cid = petlja.create_competition(sess, "Test takmicenje", alias)
    yield cid, alias
    petlja.delete_competition(sess, cid)


@pytest.fixture
def comp_with_problems(sess, empty_comp, created_prob, scoring, testcases):
    cid, alias = empty_comp
    pid, _ = created_prob
    petlja.add_problem(sess, cid, pid)
    petlja.upload_testcases(sess, pid, testcases)
    petlja.upload_scoring(sess, cid, pid, scoring)
    return cid, alias


@pytest.fixture
def src_ok(tmp_path):
    src = r"""
    #include <iostream>
    using namespace std;

    int main()
    {
        int a, b; cin >> a >> b;
        cout << 2 * (a + b) << endl;
    }
    """
    path = tmp_path / "trening_ok.cpp"
    path.write_text(src)
    return path


@pytest.fixture
def src_wa(tmp_path):
    src = r"""
    #include <iostream>
    using namespace std;

    int main()
    {
        return 0;
    }
    """
    path = tmp_path / "trening_wa.cpp"
    path.write_text(src)
    return path


@pytest.fixture
def src_tle(tmp_path):
    src = r"""
    #include <iostream>
    using namespace std;

    int main()
    {
        int a, b; cin >> a >> b;
        while(true) {}
    }
    """
    path = tmp_path / "trening_tle.cpp"
    path.write_text(src)
    return path


@pytest.fixture
def src_py(tmp_path):
    src = r"""
    a = int(input())
    b = int(input())
    print(2 * (a + b))
    """
    path = tmp_path / "trening.py"
    path.write_text(src)
    return path


@pytest.fixture
def statement(tmp_path):
    st = r"""
    За низ ћемо рећи да је **уравнотежен** ако је збир његових елемената једнак његовој дужини (броју елемената).

    Дат је низ $a$ дужине $n$, чији су елементи једноцифрени бројеви. Одредити колико он садржи уравнотежених сегмената (поднизова са узастопним елементима).

    ## Улаз

    У првом реду стандардног улаза је број $n$ $(1 \leq n \leq 10^5)$, а у другом $n$ ненегативних једноцифрених бројева, раздвојених по једним размаком.

    ## Излаз

    На стандардни излаз исписати тражени број.

    ## Пример

    ### Улаз

    ~~~
    5
    0 3 0 0 2
    ~~~

    ### Излаз

    ~~~
    4
    ~~~

    *Објашњење*: Тражени сегменти су $[0 3 0]$, $[3 0 0]$, $[0 2]$ и $[0 3 0 0 2]$.

    """
    path = tmp_path / "tekst-st.md"
    path.write_text(st)
    return path


@pytest.fixture
def testcases():
    return "tests/data/testcases.zip"


@pytest.fixture
def scoring(tmp_path):
    yaml = r"""
    type: testcase
    score_total: 100
    score_overrides:
    - {name: 1, score: 10}
    - {name: 2, score: 10}
    - {name: 3, score: 10}
    - {name: 4, score: 10}
    - {name: 5, score: 10}
    - {name: 6, score: 10}
    - {name: 7, score: 10}
    - {name: 8, score: 10}
    - {name: 9, score: 10}
    - {name: 10, score: 10}
    public: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    """
    scoring_path = tmp_path / "scoring.yaml"
    scoring_path.write_text(yaml)
    return scoring_path


def test_login_success(sess):
    assert sess is not None


def test_login_failed():
    with pytest.raises(PermissionError):
        petlja.login("wrongusername", "wrongpass")


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


def get_cpanel_problem_ids(sess):
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
    problem_ids = get_cpanel_problem_ids(sess)
    assert pid not in problem_ids


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
