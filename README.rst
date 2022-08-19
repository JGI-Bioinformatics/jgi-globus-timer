===================
JGI Globus Timer CLI
===================

The JGI Globus Timer CLI script allows for transfers using the ConfidentialAppAuthClient_ class from the Globus SDK.
This allows transfers and timer jobs to be created by a client application rather than a specific user. For more
information on authentication, check out the `Globus SDK documentation`_

.. _ConfidentialAppAuthClient: https://globus-sdk-python.readthedocs.io/en/stable/services/auth.html#globus_sdk.ConfidentialAppAuthClient
.. _Globus SDK documentation: https://globus-sdk-python.readthedocs.io/en/stable/index.html


Installation
------------
To install this package, you will want to make sure you have Poetry_ installed on your system or virtual environment.
Installation instructions for Poetry are found here_.

.. _Poetry: https://python-poetry.org/
.. _here: https://python-poetry.org/docs/#osx--linux--bashonwindows-install-instructions

Once you have that installed you can run a simple :code:`poetry install` command. Poetry will then create a virtual environment
that includes all the dependencies. You also do not need to source the environment. Instead you can run a :code:`poetry run`
command. The pyproject.toml will install the CLI as a script. To run some commands you can run this example:
.. code-block::
        > poetry run jgi-globus-timer --help
        usage: jgi-globus-timer [-h] [--secrets-file SECRETS_FILE]
                            {transfer,list,get,delete,update,ls} ...

        Create or delete a Globus timer

        positional arguments:
            {transfer,list,get,delete,update,ls}
                Create a timer to schedule data transfers

        optional arguments:
            -h, --help            show this help message and exit
            --secrets-file SECRETS_FILE
                                  path for globus client id and secret






This will run that command within the virtual environment without any sourcing.

Running a Timer Job
-------------------
To setup a timer job you will want to run the following command
.. code-block::
    ❯ poetry run jgi-globus-timer transfer --name TEST TRANSFER --label SDM TRANSFER --interval 3600 --source-endpoint [SRC UUID] --dest-endpoint [DEST UUID] --items-file tahoma.csv --stop-after-n 1

This will run a transfer at 3600s intervals. The :code:`stop_after_n 1` will make sure to stop the transfer after it ran
once.

You can view the job by providing the task id which is printed once you submit a timer job:
.. code-block::
    > poetry run jgi-globus-timer get [JOB-UUID]

You can :code:`list`, :code:`delete`, and :code:`update` your timer jobs.


List Contents of a Directory
---------------------------
JGI Globus Timer will run a recursive ls of the endpoint provided (if you have the correct permissions).
To list the contents of a directory you will want to run:
.. code-block::
    > poetry jgi-globus-timer ls [ENDPOINT-UUID]

This will recursively list all the **filenames** from the root of the Globus endpoint.

.. warning::
    If you have many files transferred at this endpoint, this process can take a very long time.
