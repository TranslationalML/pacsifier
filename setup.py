import os
import sys
from glob import glob
if os.path.exists('MANIFEST'): os.remove('MANIFEST')

packages=["code"]


if len(set(('develop', 'bdist_egg', 'bdist_rpm', 'bdist', 'bdist_dumb',
            'bdist_wininst', 'install_egg_info', 'egg_info', 'easy_install',
            )).intersection(sys.argv)) > 0:
    from setup_egg import extra_setuptools_args

# extra_setuptools_args can be defined from the line above, but it can
# also be defined here because setup.py has been exec'ed from
# setup_egg.py.
if not 'extra_setuptools_args' in globals():
    extra_setuptools_args = dict()

def main(**extra_args):
    
    from distutils.core import setup
    setup(name='PACSMAN',
          description='Connectome Mapper',
          long_description="""A package for retrieving dicom images from CHUV pacs sever""" + \
          """One can also anonymize the retrieved date using pacsman""" + \
          """Also, convert to bids format ...""",
          author= 'CHUV',
          author_email='',
          url='',
          scripts = glob("code/*.py"),
          license='',
          packages = packages,
        classifiers = [],
          maintainer = '',
          maintainer_email = '',
          package_data = {},
          requires=["pydicom"],
          **extra_args
         )

if __name__ == "__main__":
    main(**extra_setuptools_args)
