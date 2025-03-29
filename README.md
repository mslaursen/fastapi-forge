# FastAPI-Forge  
🚀 Build FastAPI Projects — Fast, Scalable, and Hassle-Free!  

FastAPI-Forge lets you define your database models through a UI, letting you select additional optional services, and then generates a full working project for you, with tests and endpoints.
The generated project follows best practices, in an easy-to-work with and scalable architecture. It will contain SQLAlchemy models of the database models you've defined in the UI, along with implementations of your selected services.

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
Skip the web UI and generate your project directly from the terminal:

```bash
fastapi-forge start --no-ui
```

### `--from-yaml`
Load a custom YAML configuration (can be generated through the UI):

```bash
fastapi-forge start --from-yaml=~/path/to/config.yaml
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
