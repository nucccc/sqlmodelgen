# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/nucccc/sqlmodelgen/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                                            |    Stmts |     Miss |   Cover |   Missing |
|---------------------------------------------------------------- | -------: | -------: | ------: | --------: |
| src/sqlmodelgen/\_\_init\_\_.py                                 |        4 |        0 |    100% |           |
| src/sqlmodelgen/codegen/cir\_to\_full\_ast/code\_ir\_to\_ast.py |       27 |        0 |    100% |           |
| src/sqlmodelgen/codegen/cir\_to\_full\_ast/to\_ast\_imports.py  |       36 |        0 |    100% |           |
| src/sqlmodelgen/codegen/code\_ir/build\_cir.py                  |       23 |        0 |    100% |           |
| src/sqlmodelgen/codegen/code\_ir/build\_col\_attrs.py           |       31 |        0 |    100% |           |
| src/sqlmodelgen/codegen/code\_ir/build\_common.py               |        3 |        0 |    100% |           |
| src/sqlmodelgen/codegen/code\_ir/build\_rels.py                 |       55 |        0 |    100% |           |
| src/sqlmodelgen/codegen/code\_ir/build\_table\_args.py          |        5 |        0 |    100% |           |
| src/sqlmodelgen/codegen/code\_ir/code\_ir.py                    |       41 |        1 |     98% |        32 |
| src/sqlmodelgen/codegen/codegen.py                              |        9 |        0 |    100% |           |
| src/sqlmodelgen/codegen/convert\_data\_type.py                  |       28 |        0 |    100% |           |
| src/sqlmodelgen/ir/ir.py                                        |       24 |        6 |     75% | 37, 49-53 |
| src/sqlmodelgen/ir/parse/ir\_parse.py                           |       61 |        2 |     97% |   60, 124 |
| src/sqlmodelgen/ir/parse/org\_parse.py                          |       40 |        0 |    100% |           |
| src/sqlmodelgen/ir/postgres/postgres\_collect.py                |       66 |        0 |    100% |           |
| src/sqlmodelgen/ir/sqlite/sqlite\_parse.py                      |       43 |        0 |    100% |           |
| src/sqlmodelgen/sqlmodelgen.py                                  |       13 |        0 |    100% |           |
| src/sqlmodelgen/utils/dependency\_checker.py                    |        6 |        2 |     67% |       4-5 |
|                                                       **TOTAL** |  **515** |   **11** | **98%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/nucccc/sqlmodelgen/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/nucccc/sqlmodelgen/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/nucccc/sqlmodelgen/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/nucccc/sqlmodelgen/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2Fnucccc%2Fsqlmodelgen%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/nucccc/sqlmodelgen/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.