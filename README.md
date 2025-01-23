# FastAPI-Forge
Generate production-ready APIs from Database Schema specifications.

Status: Work in Progress

## Usage
Install the package:

```bash
pip install fastapi-forge
```

Start the generation process:

```
fastapi-forge start
```

* A web browser will open automatically.
* Fill out the specifications as prompted.
* Once completed, click to generate your API components.

In the root of the generated project:

```
make up
```

* The project, along with its dependencies, will now run in Docker using Docker Compose.
* The SwaggerUI/OpenAPI documentation is available at `localhost:8000/docs`
