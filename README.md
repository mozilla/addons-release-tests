# Release Tests for the [Mozilla Addons Website][amo].

## Prerequisites
You'll need to have the following programs installed in your system:
- [Python 3][python]
- dependencies listed in the `requirements.txt` file
  - navigate to the project root directory and run `pip install -r requirements.txt`
- [geckodriver][geckodriver]
  - if you extract the geckodriver in your main Python directory you can call the driver at runtime from the command line
  - on a Windows machine, python is usually installed in `C:\Users\AppData\Local\Programs\Python`
- [Docker for Windows][docker]
  

## How to run the tests locally
### Clone the repository

You'll need to clone this repo using Git. If you do not know how to clone a GitHub
repository, check out this [help page][git-clone] from GitHub.

If you think you would like to contribute to the tests by writing or maintaining
them in the future, it would be a good idea to create a fork of this repository
first, and then clone that. GitHub also has great instructions for
[forking a repository][git-fork].

### Running tests in the foreground
These tests are meant to be run against the [AMO staging][stage] environment. We use [pytest][pytest] as our test runner.
If you want to see the tests being run on your local machine you can do this simply by 
navigating to the project directory and running the following command:
```
pytest --driver Firefox --variables stage.json --variables users.json
```
You can also run tests from one single test file by specifying the file name:

```
pytest test_search.py --driver Firefox --variables stage.json --variables users.json
```
Or you can run a specific test name:

```
pytest test_search.py::test_name_of_choice --driver Firefox --variables stage.json --variables users.json
```

- _note that you need to have all the requirements installed for this to work_
- _we are using pytest `--variables` as a tool to store reusable test data_



### Running tests on selenium-standalone with Docker and PowerShell

Before starting, make sure that Docker is up and running and you have switched to Wndows continers.
- _to make the container switch, click on the Docker icon in the system tray and select "Switch to Windows continaers"_

1. Build the selenium-standalone image based on the Dockerfile instructions:
```
docker image build -t firefox-standalone:latest .
```
- _note that the process can take a while; you will know that the image was successfully built when docker exits without any errors in the build logs_

2. Once the image is built successfully you can start a container based on it:
```
docker run -p 4444:4444 --shm-size 2g --rm firefox-standalone:latest
```
- _the contianer is successfully initialized if you see `Selenium Server is up and running on port 4444` as the last entry_
- _you can also load `localhost:4444` in your browser and make sure you see the Selenium-standalone homepage_

3. To run the tests inside the selenium-standalone container, you need to point `pytest` to `port 4444`:
```
pytest test_name.py --driver Remote --port 4444 --capability browserName firefox
```
- _we use `--driver Remote` and `--port 4444` because we want to tell our tests to run against the Selenium-standalone server inside our container_
- _the tests will run headless (the browser should not open). If the browser opens, your set-up might not be correct_


### Adding a test

The tests are written in Python using a POM, or Page Object Model. The plugin we use for this is called [pypom][pypom]. Please read the documentation there for good examples
on how to use the Page Object Model when writing tests.

The pytest plugin that we use for running tests has a number of advanced command
line options available too. The full documentation for the plugin can be found [here][pytest-selenium].


### Mobile and Desktop testing

If you would like to add or edit tests please consider that these are run on both a mobile resolution and a desktop resolution. The mobile resolution is ```738x414 (iPhone 7+)```, the desktop resolution is: ```1920x1080```. Your tests should be able to work on both.


### Debugging a failure

Whether a test passes or fails will result in a HTML report being created. This report will have detailed information of the test run and if a test does fail, it will provide geckodriver logs, terminal logs, as well as a screenshot of the browser when the test failed. 
We use a pytest plugin called [pytest-html][pytest-html] to create this report. The report can be found within the project directory and is named `ui-test.html`. It should be viewed within a browser.

[amo]: https://addons.mozilla.org
[stage]: https://addons.allizom.org
[python]: https://www.python.org/downloads/
[docker]: https://www.docker.com/products/docker-desktop
[addons-frontend]: https://github.com/mozilla/addons-frontend/
[addons-server]: https://github.com/mozilla/addons-server
[addons-server-docs]: https://addons-server.readthedocs.io/en/latest/topics/install/docker.html
[addons-server-selenium-testing]: https://addons-server.readthedocs.io/en/latest/topics/development/testing.html#selenium-integration-tests
[flake8]: http://flake8.pycqa.org/en/latest/
[git-clone]: https://help.github.com/articles/cloning-a-repository/
[git-fork]: https://help.github.com/articles/fork-a-repo/
[geckodriver]: https://github.com/mozilla/geckodriver/releases
[pypom]: http://pypom.readthedocs.io/en/latest/
[pytest]: https://docs.pytest.org/en/latest/
[pytest-html]: https://github.com/pytest-dev/pytest-html
[pytest-selenium]: http://pytest-selenium.readthedocs.org/
[ReadTheDocs]: https://addons-server.readthedocs.io/en/latest/topics/development/testing.html#selenium-integration-tests
[Selenium]: http://selenium-python.readthedocs.io/index.html
[selenium-api]: http://selenium-python.readthedocs.io/locating-elements.html
