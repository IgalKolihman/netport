# Netport

Netport is a tool for managing single-access resources on the target Unix machine. Netport manages
the access to different types of resources on the operating system by not allowing multiple requests
to the same resource. For example ports, files, processes, network interfaces, and more...

# How it works

Netport runs in a single python process on the target machine. It uses the
[FastAPI](https://fastapi.tiangolo.com/) framework to make a high performance and easy to use REST
api server. The users can easily perform a variety of requests to various resources by using this
REST API. Requests like:

* Acquire a free port.
* Check if file exists
* Declare that a file is being used
* Start a process
* Get a list of already acquired resources

In order to maintain an active memory of the used resources, Netport communicates with a database.
There are 2 types of supported databases that netport uses: Redis database and local pythonic
database.

Both databases serve the purpose of netport, but with one draw back for the local database. The
local database doesn't save netport's state after a shutdown or a reboot.

# Installation

Make sure that python is installed on your machine (3.7 and above). Open your terminal and run the
following command: _(It is advised to use a dedicated python virtual environment for netport.)_

```shell
pip install netport
```

# Developer Installation

Install poetry by following the instructions [here](https://python-poetry.org/docs/).

Clone this repository:

```shell
git clone https://github.com/IgalKolihman/netport.git
```

Install the development environment:

```shell
poetry install --with dev
```

# Usage

Please follow the [installation procedure](#installation) for how to install the Netport server
and then run the following command in your terminal:

```sh
netport
```

After running, a link will appear in the terminal to the server's url. The API documentation will
be available at: "http://host_ip:port/docs"

For more help regarding any netport execution, run the following command:

```shell
netport -h
```