from invoke import task

@task
def setup(ctx): # setup is something like this
    """
    Set sharefolder as (non- source code) DVC repository.
    """
    print('TODO: set up dvc')
    return
    # import json
    # dir_from_config = (
    #     ctx.run(f"dvc config --local core.remote sharefolder")
    #     .stdout
    #     .strip()
    # )
    # dir = json.loads(dir_from_config)['url'] if dir_from_config else dir
    dir = Path(config['dvc']['dir'])
    if not dir.is_dir():
        raise FileNotFoundError('not a directory or directory not found')
    ctx.run(f"dvc remote add --local sharefolder \"{dir}\" -f", echo=True)
    # set sharfolder as default dvc repo
    ctx.run(f"dvc remote default --local sharefolder", echo=True)
    sdvc = project_root_dir / 'data' / 'sample.dvc'
    # will not error if file in (local) cache but wrong remote
    ctx.run(f"dvc pull \"{project_root_dir /'data'/'sample.dvc'}\"", echo=True)



# #@task TODO
# def dvc_run(ctx,  work_dir=cur_work_dir):
#     """
#     Executes .dvc files.
#     """
#     ...
#     wd = work_dir
#     if wd not in (wd.name for wd in work.find_WorkDirs()):
#         print('Work dir not found.')
#         exit(1)
#     wd = work.WorkDir(wd)
#     work_on(ctx, wd.dir)
# #ns.add_task(dvc_run)

# # run dvc conda run
# # task: reset/clean env
# # clean env
# # TODO feature: optionally print out shell cmds.

# # ok just do setup.py programmatically