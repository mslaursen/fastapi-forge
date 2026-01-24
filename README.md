# FastAPI-Forge  
UI Based FastAPI Project Generator  

*Define your database models through a UI, select services, and get a complete production-ready containerized project with tests and endpoints!* 


## Features  


### UI Power  
- [NiceGUI](https://github.com/zauberzeug/nicegui)-based interface for project design  
- Visual model creation and configuration 
- Checkbox additional services to be integrated
- Quick-add common fields
- One-click project generation  

### Auto-Generated Components
- [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy) Models  
- [Pydantic](https://github.com/pydantic/pydantic) Schemas  
- RESTful Endpoints (CRUD + more)  
- Comprehensive Test Suite (pytest)  
- DAOs (Database Access Objects)
- [Factory Boy](https://github.com/FactoryBoy/factory_boy) Test Factories  
- [Docker Compose](https://github.com/docker/compose) Setup  

### Advanced Features  
- Custom Enum support as data types  
- YAML project import/export  
- Convert existing databases into FastAPI projects via connection string! 
    - Basically lets you quickly create an API for any database.

### CI/CD Automation  
- GitHub Workflows for automated testing and linting  
  - Runs pytest suite 
  - Executes code formatting checks
  - Ensures code quality before merging  

## Optional Integrations  

| Category       | Technologies                          |
|----------------|---------------------------------------|
| Messaging      | RabbitMQ                              |
| Caching        | Redis                                 |
| Task Queues    | Celery, [TaskIQ](https://github.com/taskiq-python/taskiq)                        |
| Auth           | JWT Authentication                    |
| Monitoring     | Prometheus                            |
| Storage        | S3                                    |
| Migrations     | Alembic                               |

*Much more to come!* 

## UI for designing your API projects
![UI Interface](https://github.com/user-attachments/assets/662c7ff2-7a42-4208-ae63-dd9760145474) 
## Generated project example
![Generated Project Structure](https://github.com/user-attachments/assets/cc546f56-abd5-4eb1-b469-5940f0558255)



## Requirements
- Python 3.12+
- UV
- Docker and Docker Compose (for running the generated project)


## Quick Start 
Install FastAPI-Forge:

```bash
pip install fastapi-forge
```

## 🛠 Usage
Start the project generation process:

```bash
fastapi-forge start
```

- A web browser will open automatically.  
- Define your database schema and service specifications.  
- Once done, click `Generate` to build your API.

To start the generated project and its dependencies in Docker:

```bash
make up # Builds and runs your project along with additional services
```

- The project will run using Docker Compose, simplifying your development environment.  
- Access the SwaggerUI/OpenAPI docs at: `http://localhost:8000/docs`.  


## Command Options
Customize your project generation with these options:

### `--use-example`
Quickly spin up a project using one of FastAPI-Forge’s prebuilt example templates:

```bash
fastapi-forge start --use-example
```

### `--no-ui`
Skip the web UI and generate your project directly from the terminal:

```bash
fastapi-forge start --no-ui
```

### `--from-yaml`
Load a custom YAML configuration (can be generated through the UI):

```bash
fastapi-forge start --from-yaml=~/path/to/config.yaml
```

### `--conn-string`
Load an existing Postgres database schema:

```bash
fastapi-forge start --conn-string=postgres://user:pass@localhost/db_name
```

### Combine Options
Load a YAML config and skip the UI:
```bash
fastapi-forge start --from-yaml=~/Documents/project-config.yaml --no-ui
```


## Using the Makefile
The generated project includes a `Makefile` to simplify common dev tasks:

### Start the Application
```bash
make up
```

### Run Tests
Tests are automatically generated based on your schema. Once the app is running (`make up`):

```bash
make test
```

### Run Specific Tests
```bash
make test-filter filter="test_name"
```

### Format and Lint Code
Keep your code clean and consistent:

```bash
make lint
```

---

## Database Migrations with Alembic
If you chose Alembic for migrations during project setup, these commands will help manage your database schema:

### Generate a New Migration
```bash
make mig-gen name="add_users_table"
```

### Apply All Migrations
```bash
make mig-head
```

### Apply the Next Migration
```bash
make mig-up
```

### Roll Back the Last Migration
```bash
make mig-down
```
