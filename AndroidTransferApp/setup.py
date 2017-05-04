from setuptools import setup

setup(
    name='AndroidTransferApp',
    version='0.1',
    description='An app used to transfer files from the collection application to a directory on the p.c.',
    author='trottasn',
    url='',
    license='MIT',
    packages=['main_app'],
    package_data={'main_app': ['*.txt']},
    entry_points={'console_scripts': ['android_transfer_app = main_app.main_program:main']}
)
