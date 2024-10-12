FROM python:3.13-alpine3.20

RUN apk add curl gcc bash git musl-dev vim tmux ripgrep fzf htop bat jq tree && \
    curl -sS https://starship.rs/install.sh | sh -s - -y && \
    echo 'eval "$(starship init bash)"' >> $HOME/.bashrc && \
    curl -proto '=https' -tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y && \
    echo 'source $HOME/.cargo/env' >> $HOME/.bashrc && \
    pip3 install pipx && \
    python3 -m pipx ensurepath && \
    pipx install pdm pre-commit && \
    git config --global --add safe.directory '*'

ENV SHELL=bash
CMD ["/bin/bash"]
