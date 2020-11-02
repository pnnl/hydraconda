# not really used but just clears and installs associated kernels on every jupyter app
try:
    from notebooking_kernels import KernelSpecManager
    KernelSpecManager()#.install_kernel_specs()
except RecursionError:
    # some problem that shows up on env setup using conda devenv TODO
    # https://github.com/chendaniely/pyprojroot/issues/16
    pass

## The kernel spec manager class to use. Should be a subclass of
#  `jupyter_client.kernelspec.KernelSpecManager`.
#
#  The Api of KernelSpecManager is provisional and might change without warning
#  between this version of Jupyter and the next stable one.
#c.NotebookApp.kernel_spec_manager_class = 'jupyter_client.kernelspec.KernelSpecManager'
#c.NotebookApp.kernel_spec_manager_class = 'kernels.KernelSpecManager'
#c.ListKernelSpecs.kernel_spec_manager = 'kernels.KernelSpecManager'
#c.NotebookApp.kernel_spec_manager_class = 'kernels.KernelSpecManager'
#c.JupterApp.ken = 'kernels.KernelSpecManager'
#c.KernelSpecApps.kernel_spec_manager_class = 'kernels.KernelSpecManager'



#c.NotebookApp.notebook_dir = ''
## Full path of a config file.
#from project import project_root
#c.JupyterApp.config_file = project_root / 'notebooking' / jupyter_config
