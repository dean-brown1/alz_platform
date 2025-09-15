import json, asyncio, click
from project_stack.pipelines import steps
from validators.registry import load_all_validators
from validators.runners import run_all
@click.group()
def cli(): pass
@cli.command()
@click.argument("case_json", type=click.Path(exists=True))
def run_case(case_json):
    raw = json.load(open(case_json))
    cb = steps.normalize(steps.ingest(raw))
    vals = load_all_validators()
    results = asyncio.run(run_all(vals, cb))
    print("Validation results:", [r.__dict__ for r in results])
if __name__ == "__main__": cli()
