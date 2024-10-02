from .auth import login
from .competition import (
    add_language,
    add_problem,
    create_competition,
    delete_competition,
    get_added_problem_ids,
    get_competition_id,
    upload_scoring,
)
from .problem import (
    create_problem,
    delete_problem,
    get_problem_id,
    get_problem_name,
    set_memory_limit,
    set_time_limit,
    upload_statement,
    upload_testcases,
)
from .submit import submit_solution

__all__ = [
    "login",
    "create_competition",
    "get_competition_id",
    "get_added_problem_ids",
    "add_problem",
    "upload_scoring",
    "add_language",
    "get_problem_id",
    "get_problem_name",
    "create_problem",
    "upload_testcases",
    "upload_statement",
    "submit_solution",
    "delete_problem",
    "delete_competition",
    "set_time_limit",
    "set_memory_limit",
]
