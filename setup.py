from setuptools import setup, find_packages

setup(
    name='WCVPHomonyms',
    url='https://github.com/alrichardbollans/WCVPHomonyms',
    author='Adam Richard-Bollans',
    author_email='38588335+alrichardbollans@users.noreply.github.com',
    # Needed to actually package something
    packages=find_packages(),

    install_requires=[
        "wcvpy >= 1.3",
    ],
    # *strongly* suggested for sharing
    version='1.0',
    description='A brief analysis of the use of ambiguous species homonyms',
    long_description=open('README.md').read(),
)
