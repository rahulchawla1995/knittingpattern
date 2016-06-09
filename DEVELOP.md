Upload
------

First ensure all tests are running:

    setup.py pep8

From [docs.python.org](https://docs.python.org/3.1/distutils/uploading.html):

    setup.py sdist bdist_wininst upload

For first upload use

    setup.py register

Install
-------

Install it with a specific python verison under windows:

    py -3.5 -m pip --no-cache-dir install --upgrade knittingpattern

Test the installed version. You might have forgotten some includes:

    cd C:\Python35-32\Lib\site-packages
    py -3.5 -m pytest knittingpattern

Classifiers
-----------

You can find all Pypi classifiers 
[here](http://pypi.python.org/pypi?%3Aaction=list_classifiers).