from setuptools import setup, find_packages
import versioneer
setup(name='clinvoc',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      author='Jason Rudy',
      author_email='jcrudy@gmail.com',
      url='https://github.com/jcrudy/clinvoc',
      package_data={'clinvoc': ['resources/*']},
      packages=find_packages(),
      requires=[]
     )