# petlja_api

A python library for interacting with the [petlja.org](https://petlja.org/) API.

## Installation
```
git clone https://github.com/PavleSekesan/petlja_api.git
cd petlja_api
pip install -r requirements.txt
```

## Basic usage

```py
from auth import login
from competition import create_competition, add_problem
from problem import create_problem, upload_testcases, upload_statement
from submit import submit

session = login()

# Create problem
prob_id = create_problem(session, name="My Problem", alias="my-prob")
upload_testcases(session, prob_id, "my-prob/testcases.zip")
upload_statement(session, prob_id, "my-prob/statement.md")

# Create competition
comp_id = create_competition(session, name="My Competition", alias="my-comp")
add_problem(session, comp_id, prob_id)

# Upload solution
score = submit(session, prob_id, "my-prob/sol.cpp", comp_id)
```