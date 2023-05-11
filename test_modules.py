import pytest
import auth
import submit


@pytest.fixture
def sess():
    return auth.login("testacc", "password")


@pytest.fixture
def cid():
    return "4511"


@pytest.fixture
def pid():
    return "132490"


def test_login_success():
    session = auth.login("testacc", "password")
    assert session is not None


def test_login_failed():
    with pytest.raises(PermissionError):
        auth.login("wrongusername", "wrongpass")


def _submit_src_file(sess, cid, pid, src, path):
    path.write_text(src)
    score = submit.submit(sess, cid, pid, path)
    return score


def test_submit_ok(sess, cid, pid, tmp_path):
    src = """
    #include <iostream>
    using namespace std;

    int main()
    {
        int a, b; cin >> a >> b;
        cout << 2 * (a + b) << endl;
    }
    """
    path = tmp_path / "trening_ok.cpp"
    score = _submit_src_file(sess, cid, pid, src, path)
    assert score == "10"


def test_submit_wa(sess, cid, pid, tmp_path):
    src = """
    #include <iostream>
    using namespace std;

    int main()
    {
        int a, b; cin >> a >> b;
        cout << a + b << endl;
    }
    """
    src_path = tmp_path / "trening_wa.cpp"
    score = _submit_src_file(sess, cid, pid, src, src_path)
    assert score == "0"


# Testing TLE is slow

# def test_submit_tle(sess, cid, pid, tmp_path):
#     src = """
#     #include <iostream>
#     using namespace std;

#     int main()
#     {
#         int a, b; cin >> a >> b;
#         while(true) {}
#     }
#     """
#     src_path = tmp_path / "trening_tle.cpp"
#     score = _submit_src_file(sess, cid, pid, src, src_path)
#     assert score == "0"
