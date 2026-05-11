version 18
clear all
set more off

* Resolve project root from the location of this file.
local here "`c(filename)'"
local here = subinstr("`here'", "\\", "/", .)
global PROJECT_ROOT = subinstr("`here'", "/Program/setup.do", "", .)

global DATA_RAW     "${PROJECT_ROOT}/Data/Raw"
global DATA_INTERIM "${PROJECT_ROOT}/Data/Interim"
global DATA_FINAL   "${PROJECT_ROOT}/Data/Final"
global PROGRAM      "${PROJECT_ROOT}/Program"
global RESULTS_TAB  "${PROJECT_ROOT}/Results/tab"
global RESULTS_FIG  "${PROJECT_ROOT}/Results/fig"
global RESULTS_TEMP "${PROJECT_ROOT}/Results/temp"

display "PROJECT_ROOT = ${PROJECT_ROOT}"

