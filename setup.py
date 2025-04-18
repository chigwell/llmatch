import os
import setuptools
from setuptools import find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname), 'r', encoding='utf-8').read()


install_requires = [
    'langchain-llm7==2025.4.101205',
    'langchain-core==0.3.51',
]

setuptools.setup(
    name='llmatch',
    version='2025.4.181147',
    author='Eugene Evstafev',
    author_email='chigwel@gmail.com',
    description='Reliable LLM interaction with pattern matching and retries.',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/chigwell/llmatch',
    packages=find_packages(),
    install_requires=install_requires,
    # Reference: https://pypi.org/classifiers/
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
    license='Apache-2.0',
    tests_require=['pytest'],
)