# fastapi_factory_utilities

Project Empty for Python with Poetry

## Setup

### Dev Tools

#### Python

<https://www.python.org/downloads/>

```bash
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.12 -y
```

#### Poetry

<https://python-poetry.org/>

```bash
curl -sSL https://install.python-poetry.org | python3.12 -
```

#### Pre-commit

Included in the project while in virtual environment
<https://pre-commit.com/>

#### Docker

<https://docs.docker.com/get-docker/>

#### Skaffold

<https://skaffold.dev>

```bash
curl -Lo skaffold https://storage.googleapis.com/skaffold/releases/latest/skaffold-linux-amd64
chmod +x skaffold
sudo mv skaffold /usr/local/bin
```

#### Buildpacks

<https://buildpacks.io/>

```bash
sudo add-apt-repository ppa:cncf-buildpacks/pack-cli
sudo apt-get update
sudo apt-get install pack-cli
```

#### Paketo

Included with the usage of buildpacks
<https://paketo.io/>

#### Portman

```bash
npm install -g @apideck/portman
```

### MongoDB

<https://docs.mongodb.com/manual/installation/>

```bash
sudo apt install -y mongodb
```

### 1- Dev Environment

```bash
# Initialize python virtual environment and install dependencies
./scripts/setup_dev_env.sh

pre-commit run --all-files
```

### 2- Build and Run Application on Docker

```bash
./scripts/dev-in-container.sh
```

```bash
./scripts/test_portman.sh
```
