# Welcome to Connect Extension project EaaS e2e AsyncMock

## Next steps

You may open your favorite IDE and start working with your project, please note that this project runs using docker.
You may modify at any time the credentials used to authenticate to connect modifying the file:

*eaas_e2e_asyncmock/.eaas_e2e_asyncmock_dev.env*


In order to start your extension as standalone docker container you can access the project folder and run:

**$ docker compose up eaas_e2e_asyncmock_dev**


please note that in this way you will run the docker container and if you do changes on the code you will need to stop it and start it again.
If you would like to develop and test at same time, we recommend you to run your project using the command

**$ docker compose run eaas_e2e_asyncmock_bash**


Once you get the interactive shell, you can run your extension using the command `cextrun`, stopping the process (using ctrl+c) and starting it back will reload the changes.

Additionally, a basic boilerplate for writing unit tests has been created, you can run the tests using

**$ docker compose run eaas_e2e_asyncmock_test**


## Community Resources

Please take note about this links in order to get additional information:

* https://connect.cloudblue.com/
* https://connect.cloudblue.com/community/modules/devops/
* https://connect.cloudblue.com/community/sdk/python-openapi-client/
* https://connect-openapi-client.readthedocs.io/en/latest/
