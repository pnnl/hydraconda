import pathlib as pl
from subprocess import run
from project_name import pth
project_name = pth.name
import json

envs = run('conda info  --json', shell=True, text=True, capture_output=True)
envs = json.loads(envs.stdout)['envs_dirs']
from itertools import chain
envs = (pl.Path(ep) for ep in envs)
envs = chain.from_iterable(ep.glob('*') for ep in envs)
import json
for ep in envs:
    if project_name in ep.name:
        from shutil import rmtree
        print(f'deleting {ep.name}')
        rmtree(ep)
        run(f'conda env remove -n {ep.name}')
