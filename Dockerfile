FROM python:3.7-slim-buster

# Install required Python packages.
RUN pip install --no-cache --upgrade pip && \
    pip install --no-cache notebook azure-quantum jupytext

# Install APT prerequisites.
RUN apt-get update && \
    apt-get -y install \
                       # Not strictly needed, but Git is useful for several
                       # interactive scenarios, so we finish by adding it as
                       # well. Thankfully, Git is a small dependency (~3 MiB)
                       # given what we have already installed.
                       git \
                       # Used to retrieve node version information.
                       curl && \
    # We clean the apt cache at the end of each apt command so that the caches
    # don't get stored in each layer.
    apt-get clean && rm -rf /var/lib/apt/lists/

# Get the Azure CLI tool.
ENV AZURE_CLI_VERSION "2.14.2"
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash

# Create a user with a home directory.
# Required for mybinder.org
ARG NB_USER=jovyan
ARG NB_UID=1000
ENV USER=${NB_USER} \
    UID=${NB_UID} \
    HOME=/home/${NB_USER} \
    IQSHARP_HOSTING_ENV=iqsharp-base \
    # Some ways of invoking this image will look at the $SHELL environment
    # variable instead of chsh, so we set the new user's shell here as well.
    SHELL=/bin/bash

RUN adduser --disabled-password \
    --gecos "Default user" \
    --uid ${UID} \
    ${USER} && \
    # Set the new user's shell to be bash when logging in interactively.
    chsh -s /bin/bash ${USER}
WORKDIR ${HOME}

# Get the az quantum extension.
RUN az extension add --source https://msquantumpublic.blob.core.windows.net/az-quantum-cli/quantum-latest-py3-none-any.whl --yes

# Make sure the contents of our repo are in ${HOME}.
# These steps are required for use on mybinder.org.
USER root
COPY . ${HOME}
RUN chown -R ${USER} ${HOME}

# Finish by dropping back to the notebook user.
USER ${USER}
