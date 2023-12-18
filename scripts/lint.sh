#!/usr/bin/env bash

set -x

mypy pyspring examples --explicit-package-bases --ignore-missing-imports
black pyspring examples --check
isort --check-only pyspring examples
flake8 pyspring examples --max-line-length=127
