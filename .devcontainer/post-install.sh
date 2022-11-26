#!/usr/bin/env bash
echo "export GPG_TTY=\$(tty)" >> /home/vscode/.zshrc
cd /workspaces/fastgraphql
poetry config virtualenvs.in-project true && poetry install --with docs --with dev --all-extras
