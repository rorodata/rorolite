.. rorolite documentation master file, created by
   sphinx-quickstart on Tue Feb  6 21:54:27 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

rorolite
========

rorolite is an open-source command-line tool to deploy Machine Learning
applications to your own server. It provides simple interface to provision the server to install all the required dependencies and deploy the ML application as an API.

This is a lite version of the `rorodata platform <https://rorodata.com/>`_.

Installation
------------

Install ``rorolite`` using ``pip`` ::

    $ pip install rorolite

System Requirements
-------------------

The target server should be running Ubuntu 16.04.

How to use
----------

Write a ``rorolite.yml`` specifying the host ipaddress and the services.
::

    runtime: python3

    # IP address/hostname of the target server
    host: 1.2.3.4

    # username on the target server
    user: alice

    services:
        # run the predict function in credit_risk_service module as an API on port 8000
        - name: api
          function: credit_risk_service.predict
          port: 8000

        # run gunicorn process port 8080
        - name: webapp
          command: gunicorn webapp:app -b 0.0.0.0:8080
          port: 8080

Either a function or a command can be specified as a service. When a function is specified as a service, rorolite used the `firefly <https://rorodata.github.io/firefly>`_ to deploy it as a service.

The server needs to provisioned once to install all the necessary system software and base dependencies specified by the runtime mentioned in the ``rorolite.yml`` file. All the application dependencies are installed on every deploy.

The currently available runtimes are:

* python3
* python3-keras

To provision the server, run::

    $ rorolite provision
    ...
    
To deploy your project, run::

    $ rorolite deploy
    Deploying project version 7...
    ...
    Services are live at:
      api -- http://1.2.3.4:8000/
      webapp -- http://1.2.3.4:8080/

The ``deploy`` command pushes your code to the server, sets up a virtual env, installs all the dependencies from your ``requirements.txt`` file and starts the specified services.

Inspect the running services using the ``ps`` command. 
::

    $ rorolite ps
    ...
    api                              RUNNING   pid 23796, uptime 0:02:07

The ``logs`` command allows inspecting logs of any service.
::

    $ rorolite logs api
    2017-10-25 04:13:12 firefly [INFO] Starting Firefly...    
    2017-10-25 04:15:12 predict function called

The ``run`` command allows running any command on the remote server.
::    

    $ rorolite run python train.py
    starting the training...
    reading the input files...
    building the model...
    saving the model...
    done.

Or you can even start a jupyter notebook server.
    
::

    $ rorolite run:notebook
    ...
    Copy/paste this URL into your browser when you connect for the first time,
    to login with a token:
        http://1.2.3.4:8888/?token=7f53b445100a5edc0d035fb7ce53061ff7dae351a107ebd4   

Copying files to/from remote server can be done using ``put``/``get`` commands. A directory ``/volumes/data`` is created during provisioning for storing data files, models etc.

::

    $ rorolite put data/loans.csv /volumes/data/
    ...
    [1.2.3.4] put: data/loans.csv -> /volumes/data/loans.csv

    $ rorolite get /volumes/data/model.pkl models/model.pkl
    ...
    [1.2.3.4] download: models/model.pkl <- /volumes/data/model.pkl

License
-------

rorolite is licensed under Apache 2 license. Please see `LICENSE <https://github.com/rorodata/rorolite/tree/master/LICENSE>`_ file for more details.

