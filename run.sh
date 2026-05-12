#!/bin/bash
# TikTok Bot Launcher
# Sets up the correct Python environment and runs the bot

export PYENV_ROOT="/root/.pyenv"
export PATH="$PYENV_ROOT/shims:$PATH"
eval "$(pyenv init -)"
pyenv global 3.12.13

# Run whatever is passed as arguments
python "$@"
