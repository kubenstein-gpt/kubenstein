# Kubenstein

## Concept

The name "Kubenstein" is a play of words on Kubernetes and Frankenstein.

The goal is to explore the effectiveness of an artificial system administrator in dealing with open-ended system problems, by mediating communications between a generative AI and a Kubernetes cluster.

The idea is to restrict to focus the application on framing the problem and defer all troubleshooting, and eventually, mitigations, to the AI.

## Overview

<!-- TOC -->

- [Kubenstein](#kubenstein)
  - [Concept](#concept)
  - [Overview](#overview)
  - [Features](#features)
  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [CLI setup](#cli-setup)
    - [Configuration](#configuration)
  - [Usage](#usage)
  - [AI Integration](#ai-integration)
  - [Troubleshooting](#troubleshooting)
  - [Contributing](#contributing)
  - [License](#license)
  - [Acknowledgments](#acknowledgments)
  - [Contact](#contact)
  - [Demo](#demo)
  - [Roadmap](#roadmap)
  - [Security](#security)
  - [Code of Conduct](#code-of-conduct)
  - [Changelog](#changelog)
  - [FAQ](#faq)
  - [Screenshots](#screenshots)

<!-- /TOC -->

## Features

- Adaptive assessment of cluster health
- Adaptative troubleshooting of cluster problems
- Recommendations for next steps of troubleshooting for problems without clear resolutions.

## Getting Started

### Prerequisites

- A Python 3.10 (or later) runtime environment
- The `kubectl` CLI installed with a version compatible with the Kubernetes cluster and logged in to a Kubernetes cluster
- `kubectl` logged in to a Kubernetes cluster
- An API Key to ChatGPT (only supported AI currently)

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

LOGGING_LEVEL=debug
EOF
```

## Usage

Activate the virtual environment:

```sh
${VIRTUAL_ENV_DIR}/bin/activate
pip install -r requirements.txt
```

Launch the application:

```sh
python --env-file $HOME/etc/k8s-chat.env app.py
```

## AI Integration

- The application opens a chat session with the application, initially asking it to act as a system administrator following an [assessment script](./prompts/troubleshoot-assess.txt).
- The AI is asked to provide one command at a time, waiting for the application to execute the command and return the output.
- If the AI response does not contain a single command, the AI is prodded to stick to the request of one command at a time (see the [prompt](./prompts/troubleshoot-assess.txt).)
- If the command output returns too much content, the application asks the AI to provide a suggestion using more filtering or alternatives (see the [prompt](./prompts/troubleshoot-output-too-long.txt).)
- The AI is asked to create a list of errors found during the assessment and repeat the troubleshooting steps for each error.
- Once the AI completes the assessment script and the troubleshooting of specific errors, it is asked to generate a readable report of all findings and suggestions for troubleshooting next steps.

## Troubleshooting

(under construction)

- Common issues and how to resolve them.
- Troubleshooting tips for AI integration.

## Contributing

(under construction)

- Guidelines for contributing to the project.
- Mention coding standards and pull request process.

## License

MIT License

## Acknowledgments

- I want to acknowledge Andre Tost for his 3-part blog series on [Using ChatGPT (And Other Tools) To Troubleshoot OpenShift](https://practicalkubernetes.blogspot.com/2023/02/chatgpt-and-other-tools-to-troubleshoot.html), who inspired me to create this application.

## Contact

- [@dnastacio](https://twitter.com/dnastacio)

## Demo

(under construction)

## Roadmap

- Allow human interaction on each prompt to confirm whether the application can send the response to the AI.
- Branch out the troubleshooting prompts into more specific areas, such as prompts specific to troubleshooting Networking aspects versus Storage aspects.
- Add more initial assessments about what is installed to broaden the troubleshooting into those areas and consider the presence of these other components when troubleshooting other areas.
- Add corrective actions to the scope of assistance, asking the AI to fix the cluster.

## Security

- The AI should be treated as a third-party
- The AI is unconstrained in the range of commands it will suggest
- This application is a prototype, so **DO NOT**  give it access to a production server.
- Consider creating a user credential with a narrow Cluster Role that only allows it to read specific resources in the cluster, excluding Secret resources, lest the AI inadvertently asks to see secrets in a namespace.

## Code of Conduct

[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](code_of_conduct.md)

You can access the Contributor Covenant [here](/CODE_OF_CONDUCT.md).

## Changelog

- 2023-09-17 First draft

## FAQ

(under construction)

## Screenshots

- Include screenshots or diagrams for visual representation.
