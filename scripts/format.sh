#!/bin/sh -e
set -x

autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place pyspring examples --exclude=__init__.py
black pyspring examples
isort pyspring examples

