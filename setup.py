
from setuptools import setup, find_packages

def get_version():
    try:
        import subprocess
        p = subprocess.Popen('hg id -t', shell=True, stdout=subprocess.PIPE)
        tag = p.stdout.read()[1:].strip()
        return tag
    except:
        return 'dev'

setup(
    name = "dream-gadget-mail",
    version = get_version(),
    license = 'Modified BSD',
    description = "Dream platfrom mail gadget",
    author = 'Haltu',
    packages = find_packages(),
    include_package_data = True,
    zip_safe = False,
    setup_requires = [],
    install_requires = ['requests',],
)

