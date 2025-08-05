rem
rem
rem
@echo off

IF NOT DEFINED PYTHONPATH (
    set PYTHONPATH=%~dp0\..;%PYTHONPATH%
)
if not DEFINED OUTPUT_DIR (
set OUTPUT_DIR=C:\temp
)
if not DEFINED TEST_DATA__DIR (
    set TEST_DATA__DIR=..\UHRdatascraper\test
)

IF "%1" == "" (
    set F=runme.py
) ELSE (
    set F=%1
)
py -i %F%