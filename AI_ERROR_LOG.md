
# AI-Error Log — Day 2

## Error 1: Incorrect rounding expectation
- **What happened:** The scoring function returned 81.2% for 13/16, while the test expected 81.3%.
- **How it was found:** The automated unit test failed with an assertion error.
- **Fix:** Use decimal rounding with ROUND_HALF_UP to produce the required 81.3%.
- **Lesson learned:** Test expected values must match the assignment's rounding rules.

## Error 2: False Excel skill match
- **What happened:** A basic substring check could detect "excel" inside "excellent".
- **How it was found:** We tested a job description containing "Excellent communication skills" alongside an actual Excel requirement.
- **Fix:** Used regular-expression word boundaries to match complete skill names.
- **Lesson learned:** Simple substring matching can create false positives.

## Error 3: No job appeared in search results
- **What happened:** The app displayed zero matching saved jobs.
- **How it was found:** We inspected the search results in the browser.
- **Fix:** Added a sample job posting and used matching search and location filters.
- **Lesson learned:** A running app still needs valid test data and appropriate filters.

## Day 2 verification
- [ ] Both scoring tests pass.
- [ ] Original example returns 11/16 = 68.8% = Not fit.
- [ ] Improved Power BI example returns 13/16 = 81.3% = Fit.
- [ ] Excel does not match "excellent".
- [ ] README.md created.
- [ ] .gitignore created.
- [ ] AI_ERROR_LOG.md created.
- [ ] GitHub repository created as private.
- [ ] Confirmed .venv is excluded from Git.

## AI Error Log — 30 October 2026

**Problem identified:**
The previous job-matching system treated every requirement as Must and gave Basic skills half credit, even when the job required only Basic knowledge. This could produce misleadingly low match scores.

**Correction implemented:**
- Added Must (weight 2) and Nice (weight 1).
- Added required skill levels: Basic (1) and Strong (2).
- Added candidate skill levels: None (0), Basic (1), Strong (2).
- Updated the scoring formula to account for the level required by the job.
- Added editable requirement classifications and skill levels.
- Fixed duplicate match score display.

**Testing performed:**
- Must / Basic / Basic: Passed
- Must / Strong / Basic: Passed
- Nice / Basic / None: Passed
- Complete six-requirement example: Passed

**Expected result:** 6.5/9 = 72.2% — Fit

**Actual result:** 6.5/9 = 72.2% — Fit

**Unit test results:** 4 tests passed, 0 failures.

**Remaining limitation:**
The application uses keyword-based suggestions for requirement classification. Users must review the suggestions because they may not always correctly interpret the job description.