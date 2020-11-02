from re import match

#re = r"^\s?{\s?\%\s?set\s+project_name\s?=\s?[\'\"]{1}([a-z0-9\-\_]+)[\'\"]{1}\s+\%\s?}"
from pathlib import Path
# pth  = Path(__file__).absolute().parent / 'project' / 'name.devenv.yml'


# name = match(re, open(pth).readline())
# if not name:
#     raise ValueError('invalid project name')
# else:
#     if not name[1]:
#         raise ValueError('invalid project name')
#     print(name[1])

pth  = Path(__file__).absolute().parent
print(pth.name)
