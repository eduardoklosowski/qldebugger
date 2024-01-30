#!/bin/bash -xe

# Project dependencies
poetry install --with=docs

# Visual Studio Code
[ -e .vscode/settings.json ] || cp .vscode/settings.json.example .vscode/settings.json
