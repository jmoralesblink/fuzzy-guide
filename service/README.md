# Django Service Bootstrap
Django Service Bootstrap [TODO: UPDATE DESCRIPTION].

## Documentation
Beyond this readme, additional documentation on the service can be found on Confluence.

* [Tech Stack](https://blinkhealth.atlassian.net/wiki/spaces/SS/pages/2318893070/Tech+Stack) defines core technologies used by the service
* [Project Structure](https://blinkhealth.atlassian.net/wiki/spaces/SS/pages/2320367647/Project+Structure) describes how the code within the service is structured


# Local Development Setup

## Prerequisites

1. **Ensure you have the correct Python version**
   
    This service requires Python 3.9, so if you don't have it, use `pyenv` to install it, and make it the default for the project.
    ```.bash
    $ pyenv install -v 3.9.1
    $ pyenv local 3.9.1
    ```

1. **Install project dependencies**
   
    Use [Poetry](https://poetry.eustace.io) to setup the virtual environment, and pull down all dependencies.
    ```.bash
    $ poetry install
    ```
   
## PyCharm Setup

https://blinkhealth.atlassian.net/wiki/spaces/EG/pages/1882325022/PyCharm

1. **Setup the Python Interpreter**
    https://blinkhealth.atlassian.net/wiki/spaces/EG/pages/1882325022/PyCharm#Configure-Python-Interpreter

    
1. **Setup the Settings Module**
    To ensure that the settings are configured when running various commands/tools from PyCharm, you must tell it what settings to use.
    1. Open PyCharm's Preferences `⌘ + ,`
    1. Go to `Languages & Frameworks > Django`
    1. In the `Settings` option, select the `django_service_bootstrap/settings` folder
    

## Setup Database

1. **Startup DB and Redis containers**
    We need a database and Redis instance running locally during development.
    We use Aurora for our DB when deployed, in Postgres-compatible mode, so running Postgres locally will work fine.
   
    ```.bash
    # starts up db and redis
    make docker_up
    ```   
1. **Reset the database, create a user, and setup fixture data**
    The following command will wipe out the database, rebuild the schema, create a superuser account and load fixture data.
    It can be run any time you want to re-build you local database from scratch.
   
    ```.bash
    # the created user will have 'password' as its password
    make reset_db
    ```

# Running Tests Locally
* Run tests: `make test`
* Sometimes you might see a similar issue as the following: `cursor "_django_curs_4562222528_sync_8" does not exist`. 
This means your test db is out of sync with the current schema.
  * Use `make test_update_db` to re-create your test db

# Common Commands

* Add new dependencies to your library: `poetry add new_dependency`
    * Add a new dev-only dependency: `poetry add --dev new_dependency`
* Update dependencies to the latest version
    * `poetry install`
        * Get the latest versions of dependencies that match what is specified in `poetry.lock` 
    * `poetry update`
        * Get the latest versions of dependencies that match what is specified in `pyproject.toml`
    * `poetry show --outdated`
        * Show the latest versions of dependencies that are not at the latest available version
    * `poetry add my-dependency@latest`
        * Update a specific dependency to the latest released version
* Run tests: `make test`
* Run linting (with Black): `make lint`
    * We use PyTest for unit tests, along with test coverage analysis
