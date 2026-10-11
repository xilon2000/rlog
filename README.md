# Table of Contents

* [How to Get Started](#how-to-get-started)
* [How to Build](#how-to-build)
* [How to Run Integration Tests](#how-to-run-integration-tests)
* [How to Run Manual Tests](#how-to-run-manual-tests)
* [How to Clean Up](#how-to-clean-up)


# Remote Log Service v1

## How to Get Started

Download `rlog v1.0.0` release from https://github.com/xilon2000/rlog/releases/tag/v1.0.0

Decompress the downloaded archive file.

Navigate to the project root folder.

## How to Build

Build and run the application:

```bash
docker compose up -d --build

```

## How to Run Integration Tests

Please note that it takes about 10 seconds to run.

```bash
docker compose exec leader pytest

```

## How to Run Manual Tests

### Step 1

To watch logs from all nodes in real time, open a new console window and run this command:

```bash
docker compose logs -f

```

### Step 2

Open the Swagger UI application in your browser:

[http://localhost:8000/docs](http://localhost:8000/docs)

Use the Swagger links to navigate between nodes:

Or use the following links directly:

| Node | Swagger UI |
| --- | --- |
| **leader** | http://localhost:8000/docs |
| **follower-1** | http://localhost:8001/docs |
| **follower-2** | http://localhost:8002/docs |


## How to Clean Up

```bash
docker compose down --rmi all

```