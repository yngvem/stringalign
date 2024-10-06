FROM python:3.12.7-alpine3.20

RUN apk add curl gcc bash git musl-dev  && \
    curl -proto '=https' -tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y && \
    echo 'source $HOME/.cargo/env' >> $HOME/.bashrc && \
    pip3 install pipx && \
    python3 -m pipx ensurepath && \
    python3 -m pipx completions && \
    echo "eval \"\$(register-python-argcomplete pipx)\"" >> ~/.bashrc && \
    pipx install pdm pre-commit

CMD ["/bin/bash"]
