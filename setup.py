from setuptools import setup, find_packages

setup(
    name='passpy',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    description='PassPy',
    long_description='A command line utility to securely store passwords',
    author='Sriharish Ranganathan',
    license='',
    url='https://github.com/sriseeks/passpy',
    keywords=[],
    classifiers=[],
    install_requires=[
        'Click',
        'pynacl',
        'pyperclip',
        'pandas',
        'tqdm'
    ],
    entry_points={
        'console_scripts':
            [
                'passpy=PassPy.src.passpy:cli',
            ]
    },
)
