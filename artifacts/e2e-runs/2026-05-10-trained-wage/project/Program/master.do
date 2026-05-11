version 18
clear all
set more off

do "setup.do"

display "=== STEP 1: CLEAN ==="
capture noisily do "${PROGRAM}/Clean/00_build_final_data.do"

display "=== STEP 2: ANALYSIS ==="
capture noisily do "${PROGRAM}/Analysis/00_main_results.do"

display "=== STEP 3: ROBUSTNESS ==="
capture noisily do "${PROGRAM}/Analysis/10_robustness_checks.do"

display "Master pipeline finished."

