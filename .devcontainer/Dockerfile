FROM python:3.13-bookworm

RUN apt-get update && \
    apt-get install -y curl gcc bash git build-essential vim tmux ripgrep fzf htop bat jq tree locales && \
    ln -s /usr/bin/batcat /usr/local/bin/bat && \
    curl -sS https://starship.rs/install.sh | sh -s - -y && \
    echo 'eval "$(starship init bash)"' >> $HOME/.bashrc && \
    curl -proto '=https' -tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y && \
    echo 'source $HOME/.cargo/env' >> $HOME/.bashrc && \
    pip3 install pipx && \
    python3 -m pipx ensurepath && \
    pipx install pdm pre-commit && \
    git config --global --add safe.directory '*'

RUN sed -i '/en_GB.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen en_GB.UTF-8 && \
    update-locale LANG=en_GB.UTF-8
ENV LANG en_GB.UTF-8
ENV LANGUAGE en_GB.UTF-8
ENV LC_ALL en_GB.UTF-8

ENV SHELL=bash
CMD ["/bin/bash"]
