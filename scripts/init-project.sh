#!/bin/bash -xe

# Project dependencies
poetry install --with=docs

# Visual Studio Code
[ -e .vscode/settings.json ] || jq ".[\"python.defaultInterpreterPath\"] = \"$(poetry env info -e)\"" .vscode/settings.json.example > .vscode/settings.json
