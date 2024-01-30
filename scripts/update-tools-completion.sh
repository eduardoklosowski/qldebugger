#!/bin/bash -xe

# Dependencies
which register-python-argcomplete >/dev/null || /usr/local/bin/pip install --user argcomplete
mkdir -p ~/.local/share/bash-completion/completions

# pipx
echo 'eval "$(register-python-argcomplete pipx)"' > ~/.local/share/bash-completion/completions/pipx

# Poetry
echo 'eval "$(poetry completions bash)"' > ~/.local/share/bash-completion/completions/poetry
