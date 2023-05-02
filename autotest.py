from pathlib import Path
import argparse
import json

cwd = Path.cwd()
autotest_dir = cwd.joinpath('.autotest')
autotest_dir.mkdir(exist_ok=True)
solutions_path = autotest_dir.joinpath('solutions.json')

def status(args):
    with solutions_path.open() as sols_file:
        for sol_name in json.load(sols_file)['solutions']:
            print(sol_name)

def add(args):
    matches = cwd.glob(args.source_paths)

    if not solutions_path.is_file():
        with solutions_path.open('w') as f:
            f.write(json.dumps({ 'solutions': [] }))
    
    with solutions_path.open() as f:
        json_obj = json.load(f)

    sols = json_obj['solutions']
    for src in matches:
        if src.name not in sols:
            sols.append(src.name)
    json_obj['solutions'] = sols
    
    with solutions_path.open('w') as sols_file:
        json.dump(json_obj, sols_file)
    
def test(args):
    raise NotImplementedError

parser = argparse.ArgumentParser(
    'petlja-autotest',
    description='Test solutions automatically on petlja.org judge'
)
subp = parser.add_subparsers(required=True)
status_parser = subp.add_parser('status')
status_parser.set_defaults(func=status)

add_parser = subp.add_parser('add')
add_parser.add_argument('source_paths')
add_parser.set_defaults(func=add)

test_parser = subp.add_parser('test')
test_parser.set_defaults(func=test)

args = parser.parse_args('add 1.cpp'.split())
args.func(args)