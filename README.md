# FastAPI-Forge  
🚀 Build Production-Ready FastAPI Projects — Fast, Scalable, and Hassle-Free!  

FastAPI-Forge lets you go from database schema to a fully functional FastAPI-based project in minutes — no boilerplate, no hassle. With its clean, intuitive UI, you can define your Postgres or MySQL models and easily add optional services like Redis, message brokers, task queues, Prometheus, authentication, Elasticsearch, and more! It automatically generates everything you need — routes, DAOs, DTOs, models, and tests — following best practices in a scalable, easy-to-maintain project architecture.  

Stop boilerplating. Start building.  

---

## ✅ Requirements
- Python 3.12+
- UV
- Docker and Docker Compose (for running the generated project)
---

## 🚀 Installation
Install FastAPI-Forge:

```bash
pip install fastapi-forge
```

---

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
make up
```

- The project will run using Docker Compose, simplifying your development environment.  
- Access the SwaggerUI/OpenAPI docs at: `http://localhost:8000/docs`.  

---

## ⚙️ Command Options
Customize your project generation with these options:

### `--use-example`
Quickly spin up a project using one of FastAPI-Forge’s prebuilt example templates:

```bash
fastapi-forge start --use-example
```

### `--no-ui`
Skip the web UI and generate your project directly from the terminal — perfect for headless environments or CLI-first workflows:

```bash
fastapi-forge start --no-ui
```

### `--from-yaml`
Load a custom YAML configuration and either generate the project immediately (with `--no-ui`) or review and adjust it in the UI:

```bash
fastapi-forge start --from-yaml=~/path/to/config.yaml
```

---

## 🧑‍💻 Examples

### Use an Example Template
```bash
fastapi-forge start --use-example
```

### Generate a Project Without the UI
```bash
fastapi-forge start --no-ui
```

### Generate a Project from a YAML Configuration
```bash
fastapi-forge start --from-yaml=~/Documents/project-config.yaml
```

### Combine Options
Load a YAML config and skip the UI:
```bash
fastapi-forge start --from-yaml=~/Documents/project-config.yaml --no-ui
```

---

## 🧰 Using the Makefile
The generated project includes a `Makefile` to simplify common dev tasks:

### Start the Application
```bash
make up
```

### Run Tests
Tests are automatically generated based on your schema — no need to write them from scratch. Once the app is running (`make up`):

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

## 📦 Database Migrations with Alembic
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
