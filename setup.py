from setuptools import setup, find_packages

setup(name='clinvoc',
      version='0.1',
      author='Jason Rudy',
      author_email='jcrudy@gmail.com',
      url='https://github.com/jcrudy/clinvoc',
      package_data={'clinvoc': ['resources/*']},
      packages=find_packages(),
      requires=[]
     )