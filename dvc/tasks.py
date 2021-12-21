from invoke import task
from pathlib import Path
from project import cur_workdir, project_root


@task
def setup(ctx, dir=(cur_workdir if cur_workdir else project_root), force=False): # setup is something like this
    """
    Set sharefolder as (non- source code) DVC repository.
    """
    assert(dvc_repo.exists())
    dot_dvc = dir / '.dvc'
    with ctx.cd(dir):
        if dot_dvc.exists():
            if force:
                ctx.run(f"dvc init -f {'--subdir' if cur_workdir else ''}", echo=True)
            else: # assume exists
                pass
        else:
            ctx.run(f"dvc init {'--subdir' if cur_workdir else ''}")
        ctx.run(f"dvc remote add --local sharefolder \"{dvc_repo}\" -f", echo=True)
        # set sharfolder as default dvc repo
        ctx.run(f"dvc remote default --local sharefolder", echo=True)
    #sdvc = project_root_dir / 'data' / 'sample.dvc'
    # will not error if file in (local) cache but wrong remote
    #ctx.run(f"dvc pull \"{project_root_dir /'data'/'sample.dvc'}\"", echo=True)

