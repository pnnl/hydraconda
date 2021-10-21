from project.work import find_WorkDirs
from project import project_root
from jupyter_client.kernelspec import KernelSpecManager as _KernelSpecManager
from pathlib import Path


def check_ifnbenv():
    import sys
    # space for kernels to be installed in 'notebooking'
    from project import activated_workdir
    if 'notebooking' != activated_workdir.stem:
        raise Exception("this only intended to be run within the 'notebooking' jupyter")

check_ifnbenv()

class KernelSpecManager(_KernelSpecManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.install_kernel_specs()


    def find_kernel_specs(self):
        from shutil import which
        exe_ext = "self-setup" # 'run-in'
        exe_ext = which(exe_ext)
        assert(exe_ext)
        exe_ext = Path(exe_ext).suffix

        from subprocess import check_output
        import json
        work_dirs = {wd for wd in find_WorkDirs() if wd.name != 'notebooking'}
        work_dirs_by_name = {wd.name: wd for wd in work_dirs}
        work_dirs_by_env = {wd.devenv_name: wd for wd in work_dirs}
        env_dirs = check_output('conda env list --json', shell=True)
        env_dirs = json.loads(env_dirs)['envs']
        #           stem or name?                 stem or name?
        env_dirs = {Path(ed).name: Path(ed) for ed in env_dirs
                    if Path(ed).name in work_dirs_by_env}
        r = {}
        for env_name, env_dir in env_dirs.items():
            wd = work_dirs_by_env[env_name]
            kps  =          env_dir / 'share' / 'jupyter' / 'kernels'
            if kps.exists():
                for kp in ( env_dir / 'share' / 'jupyter' / 'kernels').iterdir():
                    if kp.is_dir():
                        if not (kp / '_kernel.json').exists():
                            with open(kp / '_kernel.json', 'w') as kfo:
                                kfo.write(open(kp/'kernel.json').read())
                        with open(kp / '_kernel.json',) as kf:
                            kernel = json.load(kf)
                        kernel_name = f"{wd.devenv_name}-{kp.stem}"
                        exe_prefix = f"{project_root / wd.name / 'wbin' / wd.name }-run-in"+exe_ext #* either runin or pth to wrapper
                        # maybe it doesnt exist, so wouldnt want to error
                        # exe_prefix = which(exe_prefix)
                        # assert(exe_prefix)
                        kernel['argv'] = [exe_prefix] + kernel['argv']
                        kernel['display_name'] = kernel_name
                        with open(kp / 'kernel.json', 'w') as kf:
                            kf.write(json.dumps(kernel))
                        r[kernel_name] = kp
                        #{0} [conda env:{1}]
        return r

    # def get_all_specs(self):
    #     import json
    #     r = {}
    #     for name, rdir in self.find_kernel_specs().items():
    #         r[name] = {}
    #         r[name]['resource_dir'] = rdir
    #         r[name]['spec'] = json.load(open(rdir / 'kernel.json'))
    #     return r

    # def get_kernel_spec(self, name):


    def install_kernel_specs(self):
        import sys
        import shutil
        # space for kernels to be installed in 'notebooking'
        kernel_dirs = (Path(sys.prefix) / 'share' / 'jupyter' / 'kernels')
        if kernel_dirs.exists(): shutil.rmtree(kernel_dirs)
        #for kp in (Path(sys.prefix) / 'share' / 'jupyter' / 'kernels').iterdir():
        #    kp.unlink()
        for k_name, k_dir in self.find_kernel_specs().items():
            k_dir = Path(k_dir)
            assert(k_dir.exists())
            self.install_kernel_spec(
                str(k_dir),
                prefix=sys.prefix, user=None,
                kernel_name=k_name,
                replace=True,
                )

