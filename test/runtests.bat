@echo off

set PYTHONPATH=%PYTHONPATH%;..
set PYTHON=c:\python27\python.exe

%PYTHON% -m unittest discover
