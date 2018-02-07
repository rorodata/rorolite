# rorolite

rorolite is a command-line tool to deploy ML applications written in Python to your own server with a single command. It is an open-source tool licensed under Apache license.

The interface of `rorolite` is based on the interface of [rorodata platform][rorodata]. While `rorolite` is limited to running programs on already created server, the [rorodata platform][rorodata] allows allocating compute resources on demand and provides more tools to streamline data science.

Currently `rorolite` is limited to deploying one project per server.

It only supports Ubuntu/Debian distributions of Linux, preferably Ubuntu 16.04. 

[rorodata]: http://rorodata.com/

## Install

Install `rorolite`  using `pip`:

    $ pip install rorolite

## How To Use

Write a `rorolite.yml` specifying the host ipaddress and the services.

    runtime: python3-keras
    host: 1.2.3.4

    services:
        - name: api
          function: credit_risk_service.predict
          port: 8000

        - name: webapp
          command: gunicorn webapp:app
          port: 8080

Either a function or a command can be specified as a service. When a function is specified as a service, `rorolite` used the [firefly][] to deploy it as a service.

[firefly]: http://firefly-python.readthedocs.io/

The server needs to provisioned once to install all the necessary system software and base dependencies specified by the runtime mentioned in the `rorolite.yml` file. All the application dependencies are installed on every deploy.

The currently available runtimes are:

* python3
* python3-keras

To provision the server, run:

    $ rorolite provision
    ...
    
To deploy your project, run:

    $ rorolite deploy
    Deploying project version 7...
    ...
    Services are live at:
      api -- http://1.2.3.4:8000/
      webapp -- http://1.2.3.4:8080/

The `deploy` command pushes your code to the server, sets up a virtual env, installs all the dependencies from your `requirements.txt` file and starts the specified services.

Inspect the running services using the `ps` command.

    $ rorolite ps
    ...
    api                              RUNNING   pid 23796, uptime 0:02:07

The `logs` command allows inspecting logs of any service.

    $ rorolite logs api
    2017-10-25 04:13:12 firefly [INFO] Starting Firefly...    
    2017-10-25 04:15:12 predict function called

The `run` command allows running any command on the remote server.
    
    $ rorolite run python train.py
    starting the training...
    reading the input files...
    building the model...
    saving the model...
    done.

Or you can even start a jupyter notebook server.
    
    $ rorolite run:notebook
    ...
    Copy/paste this URL into your browser when you connect for the first time,
    to login with a token:
        http://1.2.3.4:8888/?token=7f53b445100a5edc0d035fb7ce53061ff7dae351a107ebd4   

Copying files to/from remote server can be done using ``put``/``get`` commands. A directory ``/volumes/data`` is created during provisioning for storing data files, models etc.

    $ rorolite put data/loans.csv /volumes/data/
    ...
    [1.2.3.4] put: data/loans.csv -> /volumes/data/loans.csv

    $ rorolite get /volumes/data/model.pkl models/model.pkl
    ...
    [1.2.3.4] download: models/model.pkl <- /volumes/data/model.pkl

## Sample Applications

Checkout the following sample applications written for rorolite:

* [iris-demo](https://github.com/rorodata/iris-demo)
* [rorolite-demo](https://github.com/rorodata/rorolite-demo)

## LICENSE

rorolite is licensed under Apache 2 license. Please see LICENSE file for more details.
