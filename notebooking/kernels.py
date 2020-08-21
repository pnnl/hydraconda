from estcp_project.work import find_WorkDirs
from jupyter_client.kernelspec import KernelSpecManager as _KernelSpecManager, KernelSpec

from pathlib import Path

class KernelSpecManager(_KernelSpecManager):

    def __init__(self, *args, **kwargs):
        self.install_kernel_specs()
        super().__init__(*args, **kwargs)


    def find_kernel_specs(self):
        from subprocess import check_output
        import json
        env_dirs = check_output(['conda', 'env', 'list', '--json'], shell=True)
        #              stem or name?
        envs = {Path(ed).name : Path(ed) for ed in  json.loads(env_dirs)['envs']
               if Path(ed).name in  {wd.devenv_name for wd in find_WorkDirs() if wd.name != 'notebooking'}}
        r = {}
        for env_name, env_dir in envs.items():
            kps  = env_dir / 'share' / 'jupyter' / 'kernels'
            if kps.exists():
                for kp in ( env_dir / 'share' / 'jupyter' / 'kernels').iterdir():
                    if kp.is_dir():
                        with open(kp / 'kernel.json', ) as kf:
                            kernel = json.load(kf)
                        kernel_name = f"{env_name}-{kp.stem}"
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
        kernel_dirs = (Path(sys.prefix) / 'share' / 'jupyter' / 'kernels')
        if kernel_dirs.exists(): shutil.rmtree(kernel_dirs)
        #for kp in (Path(sys.prefix) / 'share' / 'jupyter' / 'kernels').iterdir():
        #    kp.unlink()
        for k_name, k_dir in self.find_kernel_specs().items():
            self.install_kernel_spec(
                str(k_dir),
                prefix=sys.prefix, user=None,
                kernel_name=k_name,
                replace=True,
                )
