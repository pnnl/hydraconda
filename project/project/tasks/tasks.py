from invoke import task, Collection
from .. import project_root_dir, project_name
import yaml
from .. import work
from pathlib import Path

# need a var called ns!!!
ns = coll = collection = Collection()
# PROJECT
coll.add_collection(Collection('project'))
coll.collections['project'].add_collection(Collection('setup'))
coll.collections['project'].add_collection(Collection('action'))
coll.collections['project'].add_collection(Collection('info'))


# WORK DIR
coll.add_collection(Collection('work-dir'))
coll.collections['work-dir'].add_collection(Collection('setup'))
coll.collections['work-dir'].add_collection(Collection('action'))
coll.collections['work-dir'].add_collection(Collection('info'))


config = yaml.safe_load((project_root_dir / 'project' / 'config.yml').open())

@task
def set_dvc_repo(ctx):
    """
    Set sharefolder as (non- source code) DVC repository.
    """
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
coll.collections['project'].collections['setup'].add_task(set_dvc_repo)


@task
def create_project_wrappers(ctx, ):
    """
    Create wrappers around project tool executables.
    """
    for exe in ['dvc', ]+['git', 'bash', 'pre-commit',]:
        create_exec_wrapper(ctx, exe, work_dir='project')
coll.collections['project'].collections['setup'].add_task(create_project_wrappers)

@task
def set_git_hooks(ctx):
    """
    install git hooks using pre-commit tool
    """
    def inform_hookfile(hf):
        #https://github.com/pre-commit/pre-commit/issues/1329
        get_exe_py = f"from shutil import which; print(which(\'project-python\'))"
        exe_pth = ctx.run(f"{work.WorkDir('project').dir/'wbin'/'run-in'} python -c \"{get_exe_py}\"", hide='out').stdout.replace('\n', '')
        if exe_pth=='None': raise Exception(f'{exe_name} exe not found')
        uninformed_line = "INSTALL_PYTHON ="
        informed_line = f"INSTALL_PYTHON = \"{Path(exe_pth)}\""
        informed_line = informed_line.encode('unicode-escape').decode() + "\n"
        _ = open(hf).readlines()
        assert(''.join(_).count(uninformed_line) == 1)
        lines = []
        for al in _:
            if uninformed_line in al:
                al = informed_line
            lines.append(al)
        open(hf, 'w').writelines(lines)

    if config['git']:
        ctx.run(f"pre-commit install", echo=True)
        # make the stupid pre-commit exec invocation see the pre-commit exec instead of a python
        inform_hookfile(project_root_dir / '.git' / 'hooks' / 'pre-commit', )
        ctx.run(f"pre-commit install    --hook-type     prepare-commit-msg", echo=True)
        inform_hookfile(project_root_dir / '.git' / 'hooks' / 'prepare-commit-msg')
    else:
        ctx.run(f"pre-commit uninstall", echo=True)
        ctx.run(f"pre-commit uninstall    --hook-type     prepare-commit-msg", echo=True)
coll.collections['project'].collections['setup'].add_task(set_git_hooks)

@task(default=True)
def setup(ctx,):
    """All setup tasks"""
    if ' ' in str(project_root_dir):
        raise ValueError(f"Project directory: {project_root_dir} has spaces. Move to location w/o spaces.")
    print('creating project wrappers')
    create_project_wrappers(ctx)
    print('creating scripts wrappers')
    create_scripts_wrappers(ctx, work_dir='project')
    print('setting git hooks')
    set_git_hooks(ctx)
    #print('setting dvc repo')
    #set_dvc_repo(ctx)
    #run_setup_tasks(ctx, work_dir='project') inf loop
    #make_devenv(ctx, work_dir='project') # doesn't make sense
coll.collections['project'].collections['setup'].add_task(setup)


def get_current_conda_env():
    import os
    dir = Path(os.getenv('CONDA_PREFIX')) # can't rely conda info active env
    if not dir:
        return
    else:
        return dir.parts[-1]


def _get_current_work_dir():
    import os
    _ = Path(os.curdir).absolute()
    _ = _.relative_to(project_root_dir)
    if len(_.parts) == 0:
        return
    else:
        if _.parts[0] in (wd.name for wd in work.find_WorkDirs()):
            return _.parts[0]
        else:
            return


@task
def project_root(ctx):
    print(project_root_dir)
coll.collections['project'].collections['info'].add_task(project_root)



@task
def work_dir_list(ctx):
    """Lists work directories"""
    for wd in work.find_WorkDirs():
        print(wd.name)
coll.collections['project'].collections['info'].add_task(work_dir_list)


@task
def current_work_dir(ctx):
    cd = _get_current_work_dir()
    if cd: print(cd)
    else: exit(1)
coll.collections['work-dir'].collections['info'].add_task(current_work_dir)



def get_current_WorkDir():
    wd = _get_current_work_dir()
    if wd:
        return work.WorkDir(wd)
    return


def _create_WorkDir(ctx, dir):
    """
    Initializes a work dir with special files.
    """
    dir = Path(dir)
    if len(dir.parts) > 1:
        print('keep work directories flat')
    wd = work.WorkDir(dir)
    return wd


cur_work_dir = _get_current_work_dir()
def get_cur_work_dir_help():
    cd = ''
    if cur_work_dir:
        cd += f" Default: {cur_work_dir}"
    return f"Work directory."+cd


def _get_workdir_deps(ctx, WD):
    return [wdn for wdn in ctx.run(f"deps -p {WD.dir}", hide='out').stdout.split('\n') if wdn]


@task(help={'work-dir':get_cur_work_dir_help()})
def work_dir_deps(ctx, work_dir=cur_work_dir):
    """
    lists dependencies of work dir
    """
    if work_dir not in (wd.name for wd in work.find_WorkDirs()):
        print('work dir not found')
        exit(1)
    for wdn in _get_workdir_deps(ctx, work.WorkDir(work_dir)):
        print(wdn)
coll.collections['work-dir'].collections['info'].add_task(work_dir_deps)


@task(help={'work-dir': get_cur_work_dir_help()})
def work_dir_deps_tree(ctx, work_dir=cur_work_dir, all_dirs=False):
    """
    print dependency tree of work dir
    """
    cache = {}
    def __get_workdir_deps(ctx, parent):
        if parent.name in cache:
            ds = cache[parent.name]
            return ds
        else:
            cache[parent.name] = _get_workdir_deps(ctx, parent)
            return __get_workdir_deps(ctx, parent)

    def r(parent, t=''):
        print(t+parent.name)
        t += '   |'
        for child in __get_workdir_deps(ctx, parent):
            if child == parent.name: continue
            r(work.WorkDir(child), t=t)

    if all_dirs:
        work_dirs = (wd for wd in work.find_WorkDirs())
    else:
        if work_dir not in (wd.name for wd in work.find_WorkDirs()):
            print('work dir not found')
            exit(1)
        work_dirs = (work.WorkDir(work_dir), )
    for wd in work_dirs:
        r(wd)
coll.collections['project'].collections['info'].add_task(work_dir_deps_tree)



@task(help={
    'exe': "name or path of executable",
    'test': "test if executable can be seen before making a wrapper around it"
    })
def create_exec_wrapper(ctx, exe='_stub',  work_dir=cur_work_dir, test=True): #TODO: create script arg?
    """
    Create wrapper around executable in work dir env.
    """
    exe_pth = Path(exe)
    if work_dir not in (wd.name for wd in work.find_WorkDirs()):
        print('work dir not found')
        exit(1)
    wd = work.WorkDir(project_root_dir / work_dir)
    env_pth = wd.get_env_path()
    if not env_pth:
        raise Exception('no associated environment')

    exe_name = exe_pth.stem

    def create_wrapper(exe_pth, test=True): # TODO rename exp_pth > exe_pth_or_name
        exe_pth = Path(exe_pth)
        exe_name = exe_pth.stem
        exe_prefix_switch = f"-b {exe_pth.parent}" if exe_pth.parent.parts else ''
        from shutil import which
        if not test:
            # overwrites
            ctx.run(f"create-wrappers -t conda {exe_prefix_switch} -f {exe_name} -d {wd.dir/'wbin'} --conda-env-dir {env_pth}", echo=True)
            return Path(which(exe_name, path=str(wd.dir/'wbin')))  # Path doesn't work until py3.8

        if not exe_pth.parent.parts:
            get_exe_py = f"from shutil import which; print(which(\'{exe_name}\'))"
            exe_pth = ctx.run(f"{wd.dir/'wbin'/'run-in'} python -c \"{get_exe_py}\"", hide='out').stdout.replace('\n', '')
            if exe_pth=='None': raise Exception(f'{exe_name} exe not found')
        else:
            exe_pth = Path(exe_pth).absolute()
            if not exe_pth.exists():
                raise Exception(f'{exe_pth} does not exist')
        return create_wrapper(exe_pth, test=False)

    if exe_name == '_stub':
        wpth = create_wrapper(exe_name, test=False)
        wpth.unlink()
        wpth, env_exec_pth = create_exec_wrapper(ctx, '_prefixed-stub', work_dir=work_dir, test=False)
        wpth.unlink()
        env_exec_pth.unlink()
        return wpth, env_exec_pth
    # so now the following doesn't pick up the wrapped exe. breaks out of recursion issues.
    create_wrapper(exe_pth, test=False).unlink()
    wpth = create_wrapper(exe_pth, test=test)
    from shutil import copy2 as copyexe # attempt to copy all metadata (mainly keeping +x attrib)
    from shutil import which
    assert(wpth.stem == exe_name)
    env_exec_pth = wpth.parent / f"{wd.name}-{exe_name}{wpth.suffix}"
    copyexe(wpth, env_exec_pth)
    run_in_pth = which('run-in', path=str(wpth.parent))
    assert(run_in_pth)
    run_in_pth = Path(run_in_pth)
    assert(run_in_pth.exists())
    # creating {name prefix}-run-in
    copyexe(run_in_pth, run_in_pth.parent / f"{wd.name}-{run_in_pth.stem}{run_in_pth.suffix}")
    print(f"created wrapper {wpth} for {exe_name}")
    print(f"created wrapper {env_exec_pth} for {exe_name}")
    return wpth, env_exec_pth
coll.collections['work-dir'].collections['action'].add_task(create_exec_wrapper)


@task
def create_scripts_wrappers(ctx, work_dir=cur_work_dir):
    if work_dir not in (wd.name for wd in work.find_WorkDirs()):
        print('work dir not found')
        exit(1)
    wd = work.WorkDir(project_root_dir / work_dir)
    sdir = wd.dir / 'scripts'
    assert(sdir.exists())
    (sdir / 'bin').mkdir(exist_ok=True)

    def make_cmd_script(cmds):
        # assuming simple case: just lines of cmds
        if isinstance(cmds, str):
            cmds = [cmds]
        cmds = [cmd.strip() for cmd in cmds]
        lines = []
        al = lambda ln: lines.append(ln)
        #https://stackoverflow.com/questions/17510688/single-script-to-run-in-both-windows-batch-and-linux-bash/17623721#17623721
        al('echo >/dev/null # >nul & GOTO WINDOWS & rem ^')
        # ***********************************************************
        # * NOTE: If you modify this content, be sure to remove carriage returns (\r)
        # *       from the Linux part and leave them in together with the line feeds
        # *       (\n) for the Windows part. In summary:
        # *           New lines in Linux: \n
        # *           New lines in Windows: \r\n
        # ***********************************************************
        # Do Linux Bash commands here... for example:
        #StartDir="$(pwd)"
        # Then, when all Linux commands are complete, end the script with 'exit'...
        al('set -e')
        for i, cmd in enumerate(cmds):
            if not cmd.replace(' ', ''): continue
            if i == 0:
                # pass args to 1st cmd
                al(f"{cmd} \"$@\"")
            else:
                al(cmd)
        al('exit 0')
        al('- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -')
        al(':WINDOWS')
        #'REM Do Windows CMD commands here... for example:
        #SET StartDir=%cd%
        cmds_line = ""
        for i, cmd in enumerate(cmds):
            if not cmd.replace(' ', ''): continue
            if i == 0:
                # pass args to 1st cmd
                cmds_line += f"{cmd} %* && "
            else:
                cmds_line += f"{cmd} && "
        al(cmds_line.strip('&&').strip('&& ')) # rem trailing &&
        #REM Then, when all Windows commands are complete... the script is done.
        return tuple(lines)

    def chmod_px(pth):
        import stat
        return pth.chmod(pth.stat().st_mode | stat.S_IEXEC)

    def write_sbin(sbin, lines):
        lines = make_cmd_script(lines)
        lines = [ln.strip()+'\n' for  ln in lines]
        if sbin.suffix == '.sh':
            open(sbin, 'w', newline='\n').writelines(lines)
        else:
            open(sbin, 'w', ).writelines(lines)
        chmod_px(sbin)

    # .r, .sh, .py, .bat., .
    for script_pth in sdir.glob('*'):
        if script_pth.is_dir(): continue
        name = script_pth.stem
        ext = script_pth.suffix[1:] if script_pth.suffix else None
        sbin_bat = sdir / 'bin' / f"{name}.bat"
        sbin_sh =  sdir / 'bin' / f"{name}.sh"
        sbin_cmd =  sdir / 'bin' / f"{name}.cmd"
        sbin_name = sdir / 'bin' / name
        sbins = (sbin_bat, sbin_name) # (win, linux)

        lines = open(script_pth).readlines()
        if ext == 'cmdlines':
            for sbin in sbins: write_sbin(
                sbin,
                # TODO:     get these from workdir env os.getenv. defined in environment.devenv.template.yml
                #[f"cd {wd.dir}"]+
                [
                     ln.replace("${WORK_DIR}",      str(wd.name))
                       .replace("${WORKDIR}",       str(wd.name))
                       .replace("${WORK_DIR_PATH}", str(wd.dir ))
                       .replace("${WORKDIR_PATH}",  str(wd.dir ))
                       .replace("${PROJECT_ROOT}",  str(project_root_dir   ))
                       .replace("${PROJECTROOT}",   str(project_root_dir   ))
                for ln in lines
                if not ln.startswith('#')
                ]
                )
            wpths = create_exec_wrapper(ctx, sbin_name,  work_dir=work_dir, test=True)

        elif ext == 'py':
            # prep
            lines = [f"python {script_pth.absolute()}"]
            for sbin in sbins: write_sbin(sbin, lines)
            wpths = create_exec_wrapper(ctx, sbin_name, work_dir=work_dir, test=True)

        elif ext == 'bat':
            write_sbin(sbin_bat, lines)
            wpths = create_exec_wrapper(ctx, sbin_bat, work_dir=work_dir, test=True)
            print('not recommended to create just .bat script. include corresponding .sh script.')
        elif ext == 'sh':
            write_sbin(sbin_name, lines)
            wpths = create_exec_wrapper(ctx, sbin_name, work_dir=work_dir, test=True)
            print('not recommended to create just .sh script. include corresponding .bat script.')
        else:
            print(f'{script_pth} not processed.')
coll.collections['work-dir'].collections['action'].add_task(create_scripts_wrappers)


@task
def make_devenv(ctx, work_dir=cur_work_dir):
    """
    Create conda development environment.
    """
    assert(work_dir)
    wd = work.WorkDir(work_dir)
    # asserts maybe aren't necessary b/c warn=False default
    # idk why this failure didnt exit nonzero!!
    with ctx.cd(str(wd.dir)):
        ctx.run("conda devenv", echo=True)
    #assert(ctx.run(f"conda run --cwd {wd.dir} -n base conda devenv", echo=True).stdout) # pyt=True does't work on windows
    #assert('command failed' not in ctx.run(f"conda run --cwd {wd.dir} -n base conda devenv", echo=True).stdout) # pyt=True does't work on windows
coll.collections['work-dir'].collections['setup'].add_task(make_devenv)


def _get_setup_names(wd):
    return list(sorted({p.stem for p in (wd.dir/'scripts').glob('setup*') }))

@task(
    help={
        #'setup_list': 'the name of the setup script  (can be used multiple times to list)',
        'prompt': 'prompt setup tasks',
        },
    #iterable = ['setup_list']
)
def run_setup_tasks(ctx, work_dir=cur_work_dir, prompt=False):
    """
    execute setup tasks for the workdir
    """
    assert(work_dir)
    wd = work.WorkDir(work_dir)
    import os
    # have to render the devenv first
    dep_work_dirs = _get_workdir_deps(ctx, wd)
    assert(dep_work_dirs) # should have at least project
    done = []
    for dwd in dep_work_dirs:
        if dwd in done: continue # possibly deduping
        # 1. make the dev env
        if prompt:
            if input(f"create ({dwd}) env? [enter y for yes] ").lower().strip() == 'y':
                make_devenv(ctx, work_dir=dwd)
        else:
            make_devenv(    ctx, work_dir=dwd)

        # 2. make script wrappers
        create_exec_wrapper(    ctx, '_stub', work_dir=dwd)
        def make_wrappers():
            create_scripts_wrappers(ctx,          work_dir=dwd)
        if prompt:
            if input(f"make scripts wrappers for ({dwd})? [enter y for yes]").lower().strip() == 'y':
                make_wrappers()
        else:
            make_wrappers()

        # 3. exec setups
        dWD = work.WorkDir(dwd)
        for asetup in  _get_setup_names(dWD):
            with ctx.cd(str(dWD.dir)):
                if prompt:
                    if input(f"execute {asetup} for ({dWD.name})? [enter y for yes] ").lower().strip() == 'y':
                        assert(ctx.run(f"{dWD.dir/'wbin'/'run-in'} {dWD.name}-{asetup}", echo=True).ok)
                else:
                    # asserts may not be needed b/c warn=False
                    assert(    ctx.run(f"{dWD.dir/'wbin'/'run-in'} {dWD.name}-{asetup}", echo=True).ok)
        done.append(dWD.name)
    #ctx.run(f"conda run --cwd {wd.dir} -n {wd.env name} conda devenv", echo=True) # pyt=True does't work on windows
coll.collections['work-dir'].collections['setup'].add_task(run_setup_tasks)


def _change_dir(wd):
    if wd.dir.resolve() != Path('.').resolve():
        print(f"Change directory to {wd.dir}.")
        print(f"> cd {wd.dir}")
        return True
    else:
        return None

# TODO create recreate env task


@task(
    help={
    'work-dir': "directory to work in a workdir",
    'prompt-setup': 'prompt setup tasks',
    }
)
def work_on(ctx, work_dir, prompt_setup=False): # TODO rename work_on_check ?
    """
    Sets up an existing or new work dir.
    """
    cur_branch = ctx.run('git rev-parse --abbrev-ref HEAD', hide='out').stdout.replace('\n','')
    cur_env_name = get_current_conda_env()

    def init_commit(wd):
        ctx.run(f"conda run -n {work.WorkDir('project').devenv_name} git add {wd.dir}", echo=True)
        ctx.run(f"conda run -n {work.WorkDir('project').devenv_name} git commit -m  \"initial placeholder commit\"", echo=True)

    # best programmed with a state diagram. TODO

    # 1. check work dir creation
    if ' ' in work_dir:
        raise ValueError(f"Work directory, {work_dir}, has spaces. Create work directory w/o spaces.")
    wd = work_dir
    if wd not in (wd.name for wd in work.find_WorkDirs()):
        new_work_dir = True
        # best to do this from the project env
        project_env = work.WorkDir(project_root_dir/'project').devenv_name
        if cur_env_name !=  project_env:
            print("Change to project environment before creating a new workdir.")
            print(f"> conda activate {work.WorkDir(project_root_dir/'project').devenv_name}")
            exit(1)
        # state of just creating a workdir
        # if cur_branch != 'master':
        #     if input(f"Current git branch is not 'master'. Enter 'Y' if  you're sure that you want to initialize the work dir in the '{cur_branch}' branch.").lower() == 'y':
        #         wd = _create_WorkDir(ctx, wd)
        #         init_commit(wd)
        #     else:
        #         print('Switch to master.')
        #         print('> git checkout master')
        #         exit(1)
        #else:
        wd = _create_WorkDir(ctx, wd)
        #init_commit(wd)

    else:
        new_work_dir = False
        wd = work.WorkDir(wd)

    # 2. env creation
    minDevenv = \
       (open(wd.dir/'environment.devenv.yml')).read() \
       == wd.make_devenv()
    if minDevenv:
       print('Minimal env detected. Make sure that this is intended.')

    # 5. run setup tasks
    run_setup_tasks(ctx, work_dir=work_dir, prompt=prompt_setup)

    # check if devenv in run env includes. TODO

    # 6. check if in env
    if wd.devenv_name != cur_env_name:
        print(f'Activate environment:')
        print(f'> conda activate {wd.devenv_name}')
        exit(1)

    # 7. check if in dir
    #if _change_dir(wd):
    #    exit(1)

    # 8. check if in a branch
    if cur_branch in {'master', 'main'}:
        print('Note: You many want to create a branch for your work.')

    print('Ready to work!')
    print(f'Activate environment:')
    print(f'> conda activate {wd.devenv_name}')
coll.collections['work-dir'].collections['action'].add_task(work_on)
coll.add_task(work_on)




# TODO: recreate is this followed by a workon
@task(help={
    'work-dir': get_cur_work_dir_help(),
    'hard': 'deletes env dirs (instead of asking conda to (nicely) remove them'})
def reset(ctx, work_dir=cur_work_dir, hard=False):
    """
    Recrecreates enviroments associated with the work dir by 'removing' environments.
    """ #                  hah this wouldn't be possible with a container like docker.
    wd = work_dir
    if wd not in (wd.name for wd in work.find_WorkDirs()):
        print('Work dir not found.')
        exit(1)
    wd = work.WorkDir(wd)
    #                                           sometimes nonzero exit returned :/
    
    def onerror(func, path, exc_info):
        """
        Error handler for ``shutil.rmtree``.

        If the error is due to an access error (read only file)
        it attempts to add write permission and then retries.

        If the error is for another reason it re-raises the error.

        Usage : ``shutil.rmtree(path, onerror=onerror)``
        """
        import stat
        import os
        if not os.access(path, os.W_OK):
            # Is the error an access error ?
            os.chmod(path, stat.S_IWUSR)
            func(path)
        else:
            raise
        
    import json
    all_env_dirs = json.loads(ctx.run('conda info --json', hide='out', warn=True).stdout)['envs_dirs']
    from itertools import chain
    all_env_dirs = (Path(dr) for dr in all_env_dirs)
    all_env_dirs = (dr for dr in all_env_dirs if dr.exists())
    all_env_dirs = (dr.iterdir() for dr in all_env_dirs)
    from itertools import chain
    all_env_dirs = chain.from_iterable(all_env_dirs)
    all_env_dirs = (pth for pth in  all_env_dirs if pth.is_dir())
    all_envs = {Path(ed).stem: ed for ed in all_env_dirs}
    deps = _get_workdir_deps(ctx, wd)
    dep_envs = {work.WorkDir(dwd).devenv_name for dwd in deps}
    rem_envs = set(all_envs).intersection(dep_envs)
    assert(rem_envs)
    project_env_name = work.WorkDir(project_root_dir/'project').devenv_name
    for wdenv in rem_envs:
        if wdenv == project_env_name: continue 
        if hard:
            from shutil import rmtree
            print(f'deleting env dir {all_envs[wdenv]}')
            rmtree(all_envs[wdenv], onerror=onerror)
        else: # 
            ctx.run(f"conda env remove -n {wdenv} --yes", echo=True)
            
    for dep in deps:
        del_wrappers(dep)
        del_envfile(dep)
    work_on(ctx, wd.name)
    print('Deactivate then reactivate your environment.')
coll.collections['work-dir'].collections['action'].add_task(reset)
coll.add_task(reset)


def del_wrappers(wd):
    # and rem wrappers
    from shutil import rmtree
    wdir = work.WorkDir(wd).dir
    if        (wdir / 'wbin').exists():
        rmtree(wdir / 'wbin')
    if       ( wdir / 'scripts' / 'bin').exists():
        rmtree(wdir / 'scripts' / 'bin')

def del_envfile(wd):
    wdir = work.WorkDir(wd).dir
    # remove generated env file
    if ( wdir / 'environment.yml').exists():
        (wdir / 'environment.yml').unlink()


# TODO: reset work dir
#@task TODO
def dvc_run(ctx,  work_dir=cur_work_dir):
    """
    Executes .dvc files.
    """
    ...
    wd = work_dir
    if wd not in (wd.name for wd in work.find_WorkDirs()):
        print('Work dir not found.')
        exit(1)
    wd = work.WorkDir(wd)
    work_on(ctx, wd.dir)
#ns.add_task(dvc_run)

# run dvc conda run
# task: reset/clean env
# clean env
# TODO feature: optionally print out shell cmds.

# ok just do setup.py programmatically

#
coll.collections['project'].add_collection(Collection('_git'))

@task
def prepare_commit_msg_hook(ctx,  COMMIT_MSG_FILE): # could not use work_dir
    """
    (ignore. internal task.) git commit hook for workdir tag
    Uses takes the first dir part to prepend
    """
    from re import match
    import git
    repo = git.Repo(project_root_dir)
    work_dirs = []
    for pth in repo.index.diff("HEAD"):
        pth = Path(pth.a_path) # a_path or b_path idk
        if len(pth.parts) == 1: # assume project
            work_dirs.append('project')
        else:
            work_dir = pth.parts[0]
            if work_dir == 'notebooking' and (project_root_dir / pth).exists():
                try:
                    m = match(f"display_name: {project_name}-(.*)-(.*)", open(project_root_dir / pth).read())
                except UnicodeDecodeError:
                    continue
                if m:
                    work_dir = m.groups()[0]
            work_dirs.append(work_dir)
    work_dirs = frozenset(work_dirs)

    def find_tags(txt):
        from re import findall
        return findall("\[([^\[\]]{1,})\]", txt)

    if work_dirs:
        tags = ""
        message = open(COMMIT_MSG_FILE, 'r').read()
        existing_tags = find_tags(message)
        for wd in work_dirs:
            if wd not in existing_tags:
                tags += f"[{wd}]"
        message = f"{tags} " + message
        cmf = open(COMMIT_MSG_FILE, 'w')
        cmf.write(message)
        cmf.close()
coll.collections['project'].collections['_git'].add_task(prepare_commit_msg_hook)