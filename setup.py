from distutils.core import setup

setup(name='pysh',
      version='1.0',
      description='A bridge between the python shell and the OS shell',
      author='Ryan Abrams',
      author_email='rdabrams@gmail.com',
      url='https://github.com/caervs/pysh',
      packages=['pysh', 'pysh.interface', 'pysh.examples', 'pysh.scopes',
                'pysh.scopes.standard', 'pysh.tests'],
      scripts=['scripts/pysh'], )
