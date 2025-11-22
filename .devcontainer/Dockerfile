ARG VARIANT="ubuntu-24.04"
FROM mcr.microsoft.com/devcontainers/base:${VARIANT}

# Use the non-root "vscode" user that devcontainers base images provide
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=1000

# Switch to root for package install
USER root

# Basic build tooling + Python headers + SSL, ffi etc. for PyO3/maturin builds
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y --no-install-recommends \
       build-essential \
       pkg-config \
       curl \
       git \
       ca-certificates \
       python3 \
       python3-dev \
       python3-venv \
       python3-pip \
       libssl-dev \
       libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Ensure home exists and permissions are correct
RUN mkdir -p /home/${USERNAME} \
    && chown -R ${USER_UID}:${USER_GID} /home/${USERNAME}

# Switch to vscode user for Rust + uv install
USER ${USERNAME}
ENV HOME=/home/${USERNAME}
ENV CARGO_HOME=${HOME}/.cargo
ENV RUSTUP_HOME=${HOME}/.rustup
ENV PATH=${CARGO_HOME}/bin:${PATH}

# Install Rust (minimal profile, stable) and uv
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs \
        | sh -s -- -y --profile minimal --default-toolchain stable \
    && curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Claude Code CLI
RUN curl -fsSL https://claude.ai/install.sh | bash \
    && echo 'export PATH="$HOME/.local/bin:$PATH"' >> ${HOME}/.bashrc

# Default workdir used by devcontainers
WORKDIR /workspaces/oxc-python
