# Autotests for HdRPR


## USD location
    USD is bound to the paths where it was built.
    Built USD from Jenkins must be placed in the `C:\JN\WS\HdRPR_Build\USD\build` folder.


## Install
 1. Clone this repo

 2. Get `jobs_launcher` as git submodule, using next commands
 `git submodule init`
 `git submodule update`

 4. Put folders with scenes in `C:/TestResources/hdrpr_autotests_assets` and baselines in `C:/TestResources/hdrpr_autotests_baselines`.
 
    ***You should use the specific scenes which defined in `test_cases.json` files in `jobs/Tests/` folders.***

 4. Install Python 3.7.x

 5. Set the `PYTHONPATH` environment variable with path to USD `lib/python` folder (e.g. <built_usd_path>/lib/python)

 5. Add `bin` and `lib` folders in the `PATH` environment variable (e.g. <built_usd_path>/bin and <built_usd_path>/lib)

 6. Run `run.bat` from the `scripts` folder with customised arguments with space separator:

    | NUMBER | NAME            | DEFINES                                                                              | DEFAULT                                                                |
    |--------|-----------------|--------------------------------------------------------------------------------------|------------------------------------------------------------------------|
    | 1      | FILE_FILTER     | Path to json-file with groups of test to execute                                     | There is no default value                                              |
    | 2      | TESTS_FILTER    | Paths to certain tests from `..\Tests`. If `FILE_FILTER` is set, you can write `""`. | There is no default value                                              |
    | 3      | ENGINE          | Necessary render engine (Northstar/HybridPro).                                       | There is no default value                                              |
    | 4      | RETRIES         | Number of retries for each test case.                                                | 2                                                                      |
    | 5      | UPDATE_REFS     | Should script update references images on each iteration.                            | "No"                                                                   |
    | 6      | TOOL            | Path to `usdview`                                                                    | "..\USD\build\bin\usdview"                                             |
    | 7      | PYTHON          | Path to Python 3.7.x                                                                 | "C:\Python37\python.exe"                                               |

    Example:
    > run.bat none MaterialX_Nodes Northstar

    ***ATTENTION!***

    **The order of the arguments is important. You cannot skip arguments.**
