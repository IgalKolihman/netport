# Netport

Netport is a resource management solution for single Unix machine. Netport manages the access to
different types ot resources on the OS that cannot be accessed by multiple users.

Today Netport is capable to manage: ports, files, processes and network interfaces.

# Installation

Netport is a python module that communicates with a **Redis** database in order to hold and manage
its resources.

## Netport Server

### pip install

To Install Netport, run the following command in your python virtual environment

```sh
pip install netport
```

> ### development installation
>
> Clone this repository:
> ```sh
> git clone https://github.com/IgalKolihman/netport.git
> ```
> 
> then run:
>
> ```sh
> pip install -r reguirements. ext
> ```

### installing the redis database

Netport integrates with redis, so in order to be able to run the Netport server, a database must be
accessible somewhere in the network.

To install and run a basic Redis database locally on your PC, run the following commands:

```sh
sudo apt install redis
systemctl start redis
```

If Redis is already installed on the machine, run the following command to check the status of the
process:

```sh
systemctl status redis
```

## Netport Client

### pip install

Install the package using pip:

```sh
pip install NetportClient
```

Then import the package in your code:

```python
import netport_client
```

# Running Server

Please follow the [installation procedure](#installation) for how to install the Netport server 
and then run the following command in your terminal:

```sh
netport
```

After running, a link will appear in the terminal to the server's url. The API documentation will
be available at: "http://host_ip:port/docs"

# Configuration

When initialized, Netport tries to connect to the Redis database. Netport connects with his default
values, but it is possible to change them.

Netport will override its default values if specific environment variables are set. The following
table describes those variables and their purpose:

| *Variable*         | **Description**                   | **Defanlt** |
|--------------------|-----------------------------------|-------------|
| NETPORT_REDIS_HOST | Redis's host name to connect      | 0.0.0.0     |
| NETPORT_REDIS_PORT | Redis's DB port to connect        | 6379        |
| NETPORT_REDIS_DB   | The DB number inside redis to use | 0           |
