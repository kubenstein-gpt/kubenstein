# Developer Guidelines

This document outlines the best practices and guidelines for developers contributing to this project.

## Table of Contents

- [Developer Guidelines](#developer-guidelines)
  - [Table of Contents](#table-of-contents)
  - [Project Structure](#project-structure)
  - [Development Setup](#development-setup)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [CLI setup](#cli-setup)
    - [Configuration](#configuration)
    - [Usage](#usage)
  - [Coding Standards](#coding-standards)
  - [Git Workflow](#git-workflow)
  - [Testing](#testing)

## Project Structure

The main application starts with `chat.py`. The prompts sent to generative AIs are located under the `prompts` folder.

As the application structure evolves, one should see more Python library folders being added to the project.

## Development Setup

### Prerequisites

- A Python 3.10 (or later) runtime environment
- Cluster credentials with administrative privileges to a Kubernetes cluster
- An API Key to ChatGPT

### Installation

### CLI setup

If you want to iterate through development using a terminal, you can consult the following reference  on creating the Python environment: [https://docs.python.org/3/library/venv.html](https://docs.python.org/3/library/venv.html)

```sh
VIRTUAL_ENV_DIR=/path/to/new/virtual/environment
python -m venv ${VIRTUAL_ENV_DIR:?}
```

### Configuration

Create a configuration file in a location in your filesystem, such as ${HOME}/etc/k8s-chat.env

```sh
cat << EOF > "${HOME}/etc/k8s-chat.env"
OPENAI_API_KEY=sk-...

K8_HOSTNAME=https://api....
K8_PASSWORD=...
K8_USERNAME=...
SKIP_TLS=true

LOGGING_LEVEL=debug
EOF
```

### Usage

Activate the virtual environment:

```sh
${VIRTUAL_ENV_DIR}/bin/activate
pip install -r requirements.txt
```

Launch the application:

```sh
python --env-file $HOME/etc/k8s-chat.env app.py
```

## Coding Standards

(under construction)

- Code formatting using Flake8
- Documentation standards: All documents written in markdown format.

## Git Workflow

- Always open an issue first, following the appropriate template for either enhancement or a bug fix.
- Code branches should follow the convention `\<issue-number\>-\<dash-separated-lower-case-name\>`, such as `12-feature-name`.
- Only one commit per pull request.
- Follow [these guidelines](https://gist.github.com/robertpainsi/b632364184e70900af4ab688decf6f53) when writing the Git commit message.

## Testing

(under construction)
