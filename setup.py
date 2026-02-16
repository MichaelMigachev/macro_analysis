from setuptools import setup, find_packages

setup(
    name='macro_analysis',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'tabulate',
        'pytest',
        'pytest-cov',
        'pandas',
        'numpy'
    ],
    entry_points={
        'console_scripts': [
            'macro-analysis=macro_analysis.cli:main'
        ]
    },
    author='Your Name',
    author_email='your.email@example.com',
    description='Макроэкономический анализ данных',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/your-repo/macro-analysis',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
