# module03 — commands per folder

Every block is run from inside that folder. Prerequisite for all of them:

```bash
docker --version                  # client present
docker compose version            # v2 (note the space)
docker info                       # daemon actually running
```

---

## python-script

```bash
cd module03/python-script
docker build -t python-script .                      # build the image from the Dockerfile
docker images python-script                          # verify the image exists
docker run --rm python-script                        # run it; prints banner and exits
docker run --rm -it python-script bash               # shell inside to inspect /app
docker history python-script                         # one layer per Dockerfile instruction
docker rmi python-script                             # remove the image
```

---

## ruby-script

Same four instructions as `python-script`, different interpreter. Write the Dockerfile
yourself first; the one in the folder is the reference solution.

```bash
cd module03/ruby-script
docker run --rm -v "$PWD":/app -w /app ruby:3.3-slim ruby script.rb   # run with no build at all
docker build -t ruby-script .                        # build the image
docker images ruby-script                            # verify the image exists
docker run --rm ruby-script                          # run it; prints a random quote
diff <(grep -v '^#' Dockerfile) <(grep -v '^#' ../python-script/Dockerfile)   # only base image + interpreter differ
docker rmi ruby-script                               # remove the image
```

---

## java

Ships a pre-built `JavaApp.jar`; the image only supplies a JRE.

```bash
cd module03/java
docker build -t java-app .                           # build (add --platform linux/amd64 on Apple Silicon if it fails)
docker run --rm java-app                             # run the jar
docker run --rm java-app ls /app                     # verify COPY . . also copied the Dockerfile
docker images --format 'table {{.Repository}}\t{{.Size}}'   # compare image sizes
```

---

## flask-node

Flask portal + Express API + Mongo. Port 5001 (UI), 3000 (API).

```bash
cd module03/flask-node
docker compose up --build                            # build all + create network + start, logs in foreground
docker compose up -d --build                         # same, detached
docker compose ps                                    # service status and published ports
curl -s localhost:3000/grades                        # verify API answers (returns [] when empty)
open http://localhost:5001                           # verify UI: submit a grade, then the Grades tab
docker compose exec flask python -c "import socket; print(socket.gethostbyname('node-api'))"   # DNS by service name works
docker compose logs -f node-api                      # follow one service
docker compose exec node-api sh                      # shell into a running service
docker compose up -d --build flask                   # rebuild and replace one service only
docker compose down                                  # stop + remove containers and network (mongo data kept)
docker compose down -v                               # ...and delete the named volume (data loss)
```

Manual variant, to show what Compose replaces:

```bash
docker build -t node-api ./grade-submission-api      # build API image
docker build -t flask-portal ./grade-submission-portal   # build portal image
docker network create my-network                     # user-defined bridge => embedded DNS
docker run -d --name mongo --network my-network -e MONGO_INITDB_DATABASE=grade_db mongo
docker run -d --name node-api --network my-network -p 3000:3000 -e DB_HOST=mongo -e DB_PORT=27017 -e DB_NAME=grade_db node-api
docker run -d --name flask --network my-network -p 5001:5001 -e GRADE_SERVICE_HOST=node-api flask-portal
docker rm -f mongo node-api flask                    # tear down the three containers
docker network rm my-network                         # remove the network
```

---

## microservices

Seven services, five languages. First build is ~5–15 min (Maven + CRA).

```bash
cd module03/microservices
docker compose up --build                            # build and start everything
docker compose logs -f order-management              # watch the slow Java build/boot
docker compose ps                                    # all seven up, with their ports
open http://localhost:4000                           # the UI / API gateway
curl -s localhost:3001/api/products | head -c 300    # product-catalog (Node)
curl -s localhost:3002/api/inventory                 # product-inventory (Flask)
curl -s "localhost:8080/shipping-fee?product_id=1"   # shipping-and-handling (Go)
curl -s localhost:8000/api/contact-message           # contact-support-team (Flask)
curl -s localhost:9090/api/orders/1/cart             # order-management (Spring)
curl -s -X POST localhost:3003/api/signup -H 'Content-Type: application/json' \
  -d '{"firstName":"Ada","lastName":"L","address":"1 St","postalCode":"X","email":"a@b.c","password":"pw"}'   # profile-management
docker compose exec ecommerce-ui getent hosts product-catalog   # service name resolves inside the network
curl http://product-catalog:3001/api/products        # ...and not from the host (expected failure)
docker compose down                                  # stop + remove
docker compose down --rmi local                      # ...and delete the images this project built
```

---

## postgres_ex

No Dockerfile on purpose — both services are stock images, so there is nothing to build.
Postgres 5432, pgAdmin 5050. Creds `admin`/`admin`, db `users`.

```bash
cd module03/postgres_ex
docker compose up -d                                 # pull images and start (nothing to build)
docker compose ps                                    # verify both containers are up
docker compose exec db psql -U admin -d users -c '\l'   # verify Postgres from inside the container
psql postgresql://admin:admin@localhost:5432/users   # verify from the host (needs a local psql)
open http://localhost:5050                           # pgAdmin — login admin@gmail.com / admin
                                                     # Add New Server => Host: db, Port: 5432 (not localhost)
docker compose logs -f db                            # follow Postgres logs
docker compose down                                  # stop; table data survives in the named volume
docker compose down -v                               # ...and destroy the volume
```

---

## statusboard-uv

Flask app packaged with uv. Host port 8000. Needs outbound internet.

```bash
cd module03/statusboard-uv
docker compose up -d --build                         # build with uv sync --frozen --no-dev, then start
docker compose ps                                    # verify it is up
open http://localhost:8000                           # verify the status table and incidents tab
curl -sI localhost:8000 | head -1                    # verify it serves without a browser
docker run --rm statusboard-uv ls /app               # verify .dockerignore kept demo fixtures out
docker run --rm statusboard-uv whoami               # shows root — the missing USER instruction
docker images --format '{{.Repository}}\t{{.Size}}' | grep statusboard   # compare against the Poetry image
docker compose build                                 # cache demo: first build installs everything
touch app.py && docker compose build                 # uv sync re-runs, because COPY . . invalidated it
docker compose logs -f                               # follow app logs
docker compose down                                  # stop + remove
```

Plain-docker equivalent:

```bash
docker build -t statusboard .                        # build without compose
docker run --rm -p 8000:8000 statusboard             # run in the foreground
```

---

## statusboard-poetry

Byte-identical app, packaged with Poetry. Host port 8001, so both can run at once.

```bash
cd module03/statusboard-poetry
docker compose up -d --build                         # build with poetry install --without dev, then start
docker compose ps                                    # verify it is up
open http://localhost:8001                           # verify the UI on the other port
curl -sI localhost:8001 | head -1                    # verify without a browser
docker run --rm statusboard-poetry ls /app          # what actually shipped
docker run --rm statusboard-poetry /app/.venv/bin/pip list | wc -l   # 12 app packages, not Poetry's ~50
docker compose down                                  # stop + remove
```

Compare the two builds:

```bash
cd module03
diff statusboard-uv/app.py statusboard-poetry/app.py && echo identical   # only packaging differs
docker images --format '{{.Repository}}\t{{.Size}}' | grep statusboard    # 268 MB vs 332 MB
```

---

## Global cleanup

```bash
docker compose down -v                               # per project, from its own directory
docker ps -a                                         # what is still around
docker system df                                     # disk used by images/containers/volumes/cache
docker system prune                                  # stopped containers, unused networks, dangling images
docker system prune -a --volumes                     # nuke everything unused, volumes included
```
