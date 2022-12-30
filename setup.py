from setuptools import setup

setup(
    name='simplefilemirror',
    version='1.0.0',
    description='Simple file mirror',
    long_description=(
        "Updates files from the source folder to the destination folder. 'Update' means:"
        "Source present, destination missing, not tagged -> Copy."
        "Source present, destination missing, tagged -> [No action]."
        "Source present, destination present-> [No action]."
        "Source missing, destination present-> [No action]"
        "'Tagging' is done via json-file, storing files already been copied."),
    url='https://github.com/HenningUe/simple-file-sync',
    author='Henning Uekötter',
    author_email='ue.henning@gmail.com',
    license='MIT License',
    packages=['simplefilemirror'],
    install_requires=['python-utils >= 3.4.5',
                      'progressbar2 >= 4.2.0',
                      ],

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Topic :: System :: Filesystems ',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3',
    ],
)
