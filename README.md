# pylib-helpers

Helpers for logging, sleeping, and other common functional work done across projects

[![Release](https://github.com/samarthj/pylib-helpers/actions/workflows/release.yml/badge.svg)](https://github.com/samarthj/pylib-helpers/actions/workflows/release.yml)
[![GitHub release (latest SemVer including pre-releases)](https://img.shields.io/github/v/release/samarthj/pylib-helpers?sort=semver)](https://github.com/samarthj/pylib-helpers/releases)
[![PyPI](https://img.shields.io/pypi/v/pylib-helpers)](https://pypi.org/project/pylib-helpers/)

[![Build](https://github.com/samarthj/pylib-helpers/actions/workflows/build_matrix.yml/badge.svg)](https://github.com/samarthj/pylib-helpers/actions/workflows/build_matrix.yml)

[![Total alerts](https://img.shields.io/lgtm/alerts/g/samarthj/pylib-helpers.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/samarthj/pylib-helpers/alerts/)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/samarthj/pylib-helpers.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/samarthj/pylib-helpers/context:python)

[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://conventionalcommits.org)

## RetryHandler

Samples can be found here in the [tests](https://github.com/samarthj/pylib-helpers/blob/main/tests/test_retry_handler.py)

Example usage:

```python

from somelib import ClientError
from helpers import Logger, RetryHandler, Sleeper

LOGGER = Logger()
SLEEPER = Sleeper()

def _client_error(err_obj):
    err_msg = str(err_obj)
    if "Recoverable" not in err_msg:
        raise err_obj
    else:
        LOGGER.print_error(err_msg)
        SLEEPER.normal_sleep()

@RetryHandler(
    (ClientError),
    max_retries=10,
    wait_time=0,
    err_callbacks={"ClientError": (_client_error, {})},
).wrap
def do_the_thing(data):
    pass
```
