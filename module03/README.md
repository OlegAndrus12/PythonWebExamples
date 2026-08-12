# Module 03 — Docker, networking and Docker Compose

Eight self-contained examples that build up, step by step, from *"run one script in a
container"* to *"orchestrate seven polyglot services with one command"*.

Read them in order. Each one exists to introduce exactly one new idea:

| # | Directory | New idea | Language(s) |
| --- | --- | --- | --- |
| 1 | [python-script/](python-script/) | `Dockerfile`, `build`, `run` | Python |
| 2 | [ruby-script/](ruby-script/) | Write a Dockerfile yourself (exercise) | Ruby |
| 3 | [java/](java/) | Shipping a pre-built artifact | Java |
| 4 | [flask-node/](flask-node/) | **Containers must share a network** → Compose | Python + Node + Mongo |
| 5 | [microservices/](microservices/) | Compose at scale, service-to-service calls | Python + Node + Go + Java + React |
| 6 | [postgres_ex/](postgres_ex/) | Compose with *no build at all* — images + volumes | — |
| 7 | [statusboard-uv/](statusboard-uv/) | A real project: lock file, `.dockerignore` that earns its keep | Python (uv) |
| 8 | [statusboard-poetry/](statusboard-poetry/) | The same app, same lesson, different packaging tool | Python (Poetry) |

**[docker-cheatsheet.md](docker-cheatsheet.md)** — every command in this module on one
page, grouped by task. Keep it open while working through the parts below.

Supporting slides in this folder: [tcp.png](tcp.png) (TCP/OSI),
[common ports.png](common%20ports.png), [docker%20cache.png](docker%20cache.png) (layer caching).

---

## Prerequisites

```bash
docker --version           # 20.10+ ; this doc was checked against 29.3.1
docker compose version     # v2+ ; note the space — `docker-compose` is the old v1 binary
docker info                # must not error: the daemon has to be running
```

Everything below is run **from inside the example's own directory** — never from the
repo root.

> **Apple Silicon note.** A few examples pin old base images that only publish `amd64`
> (`node:14`, `openjdk:11-jre-slim`, `maven:3.6.3-openjdk-17-slim`). They still run under
> emulation, just slowly. If a build dies with `no matching manifest`, add
> `--platform linux/amd64` to `docker build`, or `platform: linux/amd64` to the compose
> service.

---

# Part 0 — the welcome container

Before building anything, run someone else's image. This is the shortest possible proof
that the daemon works, and it introduces four flags you will use all module.

```bash
docker run -d -p 8088:80 --name welcome docker/welcome-to-docker
```

Open <http://localhost:8088>.

| Flag | Meaning |
| --- | --- |
| *(no build)* | `docker/welcome-to-docker` is not on your machine, so Docker pulls it from Docker Hub first |
| `-d` | detached — run in the background and return the prompt, instead of taking over the terminal |
| `-p 8088:80` | publish **host** port 8088 to **container** port 80. The container serves on 80; you reach it on 8088 |
| `--name welcome` | a stable name, so later commands say `welcome` instead of a random hash like `nifty_bardeen` |

Nothing was built, no `Dockerfile` was involved, and the web server inside is nginx —
you never installed nginx. That is the point: an image is a shippable, pre-built
filesystem plus a default command.

Poke at it:

```bash
docker ps                     # running containers, their ports and names
docker logs welcome           # stdout/stderr of the process inside
docker exec -it welcome sh    # a shell inside the running container
    ls /usr/share/nginx/html
    exit
```

Then clean up. A detached container keeps running until you stop it:

```bash
docker stop welcome           # SIGTERM to the main process
docker rm welcome             # delete the stopped container
# or both at once:
docker rm -f welcome
```

> **Try the port swap.** `docker run -d -p 9000:80 --name welcome docker/welcome-to-docker`
> serves the same container on <http://localhost:9000>. The right-hand number is fixed by
> the software inside the image; the left-hand one is yours to choose. Keeping that
> distinction straight is most of what Part 2 is about.

---

# Part 1 — One container, one process

## 1.1 `python-script` — the minimal Dockerfile

[python-script/main.py](python-script/main.py) just prints ASCII art. The point is the
[Dockerfile](python-script/Dockerfile), which is the shortest useful one you can write:

```dockerfile
FROM python:3.14.0rc1-slim   # 1. base image = OS + runtime, already built for you
WORKDIR /app                 # 2. cd inside the image; created if missing
COPY main.py main.py         # 3. host file → image layer
CMD ["python", "main.py"]    # 4. default command when a container starts
```

### Step by step

```bash
cd module03/python-script

# 1. Build an image and tag it. The trailing "." is the BUILD CONTEXT —
#    the directory sent to the daemon, and the root for every COPY path.
docker build -t python-script .

# 2. Confirm it exists
docker images python-script

# 3. Run a container from it. --rm deletes the container after it exits.
docker run --rm python-script
```

Expected output: the ASCII "Python!" banner, then the container exits — a container
lives exactly as long as its main process.

### Things worth trying

```bash
# Override CMD at runtime — the image is a filesystem, not a fixed program
docker run --rm python-script python -c "import sys; print(sys.version)"

# Get a shell inside to look around
docker run --rm -it python-script bash
ls -l /app && pwd && exit

# See the layers the build produced, one per instruction
docker history python-script
```

### Build vs. run — the distinction people get wrong

| | `docker build` | `docker run` |
| --- | --- | --- |
| Produces | An **image** (read-only, layered) | A **container** (image + writable layer + process) |
| Runs | `RUN` instructions | `CMD` / `ENTRYPOINT` |
| Frequency | Once per code change | Any number of times per image |

---

## 1.2 `ruby-script` — your turn

[ruby-script/](ruby-script/) is `script.rb` plus a Dockerfile you should write yourself
before opening the one in the folder — it is the reference solution, not the lesson. The
script prints a random quote in an ASCII box and needs nothing but a Ruby interpreter.

### Step 1 — prove it works without building anything

Mount the source into an off-the-shelf image. Nothing is built, nothing is left behind:

```bash
cd module03/ruby-script
docker run --rm -v "$PWD":/app -w /app ruby:3.3-slim ruby script.rb
```

- `-v "$PWD":/app` — bind-mounts the host directory into the container.
- `-w /app` — sets the working directory.

This is the fastest way to run *anything* in a throwaway environment. It is also the
wrong way to ship software: nothing is reproducible, the code lives outside the image.

### Step 2 — write the Dockerfile

Write it from memory, then compare with [ruby-script/Dockerfile](ruby-script/Dockerfile):

```dockerfile
FROM ruby:3.3-slim
WORKDIR /app
COPY script.rb .
CMD ["ruby", "script.rb"]
```

```bash
docker build -t ruby-script .
docker run --rm ruby-script
```

Compare it line for line with `python-script/Dockerfile`. The structure is identical —
only the base image and the interpreter changed. **That is the whole promise of Docker:**
the interface to a Ruby app and a Python app is the same two commands.

---

## 1.3 `java` — an image over a pre-built artifact

[java/](java/) contains a compiled `JavaApp.jar` and nothing else. There is no source,
no build tool — the image only supplies a JRE:

```dockerfile
FROM openjdk:11-jre-slim   # jre, not jdk — we don't compile here
WORKDIR /app
COPY . .                   # copies JavaApp.jar (and the Dockerfile, see below)
CMD ["java", "-cp", "JavaApp.jar", "JavaApp"]
```

```bash
cd module03/java
docker build -t java-app .
docker run --rm java-app
```

### Two lessons hiding in here

**1. `COPY . .` copies too much.** The Dockerfile itself lands inside the image. That is
why the microservices examples all carry a `.dockerignore`:

```
Dockerfile
README.md
```

`.dockerignore` works like `.gitignore`, but for the build context: matched files are
never even sent to the daemon. [order-management/.dockerignore](microservices/order-management/.dockerignore)
is the serious version — it excludes `target/`, `.git/` and the Maven wrapper, which
would otherwise be uploaded on every single build.

**2. Runtime image ≠ build image.** Here the `.jar` was built on the host. In
[microservices/order-management/Dockerfile](microservices/order-management/Dockerfile)
the opposite choice was made — a full Maven image compiles *inside* the container, so the
final image carries the entire JDK and Maven's dependency cache as well as the app.
Multi-stage builds (compile in one image, copy just the artifact into a slim one) are how
you get both — sketched as an exercise at the end of **Part 6**. The size difference is
visible right now:

```bash
docker images --format "table {{.Repository}}\t{{.Size}}"
```

### Layer caching — see [docker cache.png](docker%20cache.png)

Every instruction is a cached layer. Change one, and it plus everything below it is
rebuilt. This is why dependency files are copied *before* source code everywhere in this
module — e.g. [flask-node/grade-submission-portal/Dockerfile](flask-node/grade-submission-portal/Dockerfile):

```dockerfile
COPY requirements.txt .        # changes rarely
RUN pip install -r requirements.txt   # ← expensive, stays cached
COPY . .                       # changes constantly
```

Flip those two blocks and every edit to `app.py` reinstalls Flask from scratch. Try it:
build, touch `app.py`, rebuild, and watch which steps say `CACHED`.

---

# Part 2 — Why a network is needed

This is the core of the module. We will deliberately break
[flask-node/](flask-node/) before fixing it.

### The application

Three containers:

```
  browser ──:5001──► flask (portal)  ──http://???:3000──► node-api  ──mongodb://???:27017──► mongo
             host           Python                          Node.js                          Mongo
```

- [grade-submission-portal/app.py](flask-node/grade-submission-portal/app.py) — Flask UI, port 5001.
  Calls the API at `http://${GRADE_SERVICE_HOST}:3000/grades`.
- [grade-submission-api/app.js](flask-node/grade-submission-api/app.js) — Express REST API, port 3000.
  Connects to `mongodb://${DB_HOST}:${DB_PORT}/${DB_NAME}`.
- `mongo` — official image, port 27017.

Note that **neither app hardcodes a hostname**. Both read it from an environment
variable. That is the one change an application needs to become container-friendly.

## Step 1 — build the two images

```bash
cd module03/flask-node
docker build -t node-api ./grade-submission-api
docker build -t flask-portal ./grade-submission-portal
```

## Step 2 — run them the naive way, and watch it fail

```bash
docker run -d --name mongo -e MONGO_INITDB_DATABASE=grade_db mongo
docker run -d --name node-api -p 3000:3000 \
  -e DB_HOST=localhost -e DB_PORT=27017 -e DB_NAME=grade_db node-api
docker run -d --name flask -p 5001:5001 \
  -e GRADE_SERVICE_HOST=localhost flask-portal
```

All three containers start. Now use it — open <http://localhost:5001>, submit a grade:

```bash
curl -s localhost:3000/grades          # hangs, then errors
docker logs node-api                   # MongooseServerSelectionError: connect ECONNREFUSED 127.0.0.1:27017
docker logs flask                      # ConnectionRefusedError ... localhost:3000
```

### Why

**Each container gets its own network namespace.** Inside a container, `localhost` /
`127.0.0.1` means *that container*, not your Mac and not the container next door. The
Node process looks for Mongo on its own loopback interface, finds nothing, and refuses
the connection. Same for Flask looking for the API.

`-p 3000:3000` does *not* help here. Port publishing maps a **host** port to a container
port so that *you*, from the host, can reach the service. It creates no path between two
containers. This is why the compose file publishes nothing for `mongo` — only the other
containers need it.

> See [common ports.png](common%20ports.png) for the well-known ports these examples use
> (80, 443, 5432, 27017, 3000…), and [tcp.png](tcp.png) for where this sits in the stack:
> container networking is layer 3/4 plumbing, the apps above it speak plain HTTP.

Clean up before the next step:

```bash
docker rm -f mongo node-api flask
```

## Step 3 — the default bridge is not enough

Every container without an explicit `--network` joins the built-in `bridge` network, so
they *can* reach each other — but only by IP address:

```bash
docker run -d --name mongo -e MONGO_INITDB_DATABASE=grade_db mongo
docker inspect -f '{{.NetworkSettings.IPAddress}}' mongo    # e.g. 172.17.0.2

docker run --rm busybox nslookup mongo         # can't resolve 'mongo'  ← no DNS
docker run --rm busybox ping -c1 172.17.0.2    # works                  ← but who wants this?
```

(`busybox` is used here only because it is a tiny image that ships `ping` and
`nslookup` — most application images, `node:14` included, do not.)

The default bridge has **no service discovery**. That IP is assigned at start time and
changes on every restart, so you cannot put it in a config file. Historically you used
`--link`; it is deprecated.

```bash
docker rm -f mongo
```

## Step 4 — a user-defined network, which has DNS

```bash
docker network create my-network
docker network ls
```

A user-defined bridge adds an embedded DNS server: **every container on it is resolvable
by its container name**. Now the environment variables can hold real hostnames:

```bash
docker run -d --name mongo   --network my-network \
  -e MONGO_INITDB_DATABASE=grade_db mongo

docker run -d --name node-api --network my-network -p 3000:3000 \
  -e DB_HOST=mongo -e DB_PORT=27017 -e DB_NAME=grade_db node-api

docker run -d --name flask   --network my-network -p 5001:5001 \
  -e GRADE_SERVICE_HOST=node-api flask-portal
```

Verify:

```bash
docker exec flask python -c "import socket; print(socket.gethostbyname('node-api'))"
curl -s localhost:3000/grades          # []
```

Open <http://localhost:5001>, submit a grade, then check the Grades tab. It works.

### The three rules to take away

1. `localhost` inside a container is that container. Always.
2. Container-to-container traffic uses the **container port** (`node-api:3000`), never
   the published host port. Publishing is only for host→container.
3. On a user-defined network, the **container name is the hostname**. Configuration
   should therefore be a name, injected as an env var — never an IP, never `localhost`.

## Step 5 — feel the pain, then fix it

To restart this stack after a code change you must: stop three containers, remove three
containers, rebuild two images, re-run three long `docker run` lines **in the right
order**, and remember the network. Get one env var wrong and you debug it from
`docker logs`.

That is what Compose exists to remove.

```bash
docker rm -f mongo node-api flask
docker network rm my-network
```

---

# Part 3 — Docker Compose

[flask-node/docker-compose.yaml](flask-node/docker-compose.yaml) is the same three
containers, declared instead of commanded:

```yaml
services:
  flask:
    build: { context: "./grade-submission-portal" }   # ← docker build
    ports: ["5001:5001"]                              # ← -p
    environment: [GRADE_SERVICE_HOST=node-api]        # ← -e
    depends_on: [node-api]                            # ← start order
  node-api:
    build: { context: "./grade-submission-api" }
    environment: [DB_HOST=mongo, DB_PORT=27017, DB_NAME=grade_db]
    ports: ["3000:3000"]
    depends_on: [mongo]
  mongo:
    image: mongo                                      # no build, no ports published
    volumes: [mongo-data:/data/db]                    # ← named volume
volumes:
  mongo-data:
```

### Run it

```bash
cd module03/flask-node

docker compose up --build      # build images + create network + start, logs in foreground
# or:
docker compose up -d --build   # detached
```

Then open <http://localhost:5001>, submit a grade, and view the Grades tab.

### What Compose did for you

```bash
docker compose ps            # service status
docker network ls            # note: flask-node_default — created automatically
docker volume ls             # flask-node_mongo-data
```

- **It created the network.** Every service joins `<project>_default`, and is resolvable
  by its **service name**. `GRADE_SERVICE_HOST=node-api` and `DB_HOST=mongo` are exactly
  the hostnames from Step 4 — the same mechanism, now implicit.
- **It kept `mongo` unpublished.** No `ports:` entry, so Mongo is unreachable from your
  Mac but perfectly reachable at `mongo:27017` from `node-api`. Smallest possible
  exposure — and a demonstration that publishing and networking are separate concerns.
- **It persisted the data.** `mongo-data` is a named volume, so grades survive
  `docker compose down`. They do *not* survive `down -v`.

### `depends_on` does not mean "wait until ready"

It orders *container start*, not *application readiness*. Mongo will accept connections
a second or two after its container starts, and `node-api` may well connect first —
Mongoose retries, so it recovers. Real readiness needs a `healthcheck:` plus
`depends_on: { mongo: { condition: service_healthy } }`, or a wait loop in the
entrypoint (the `zoo_api` example at the repo root does the latter with `pg_isready`).

### Everyday commands

```bash
docker compose logs -f node-api    # follow one service
docker compose exec node-api sh    # shell into a running service
docker compose restart flask
docker compose up -d --build flask # rebuild + replace one service only
docker compose down                # stop + remove containers and the network
docker compose down -v             # ...and delete the named volumes (data loss)
```

---

# Part 4 — `microservices`: Compose at scale

[microservices/](microservices/) is the same ideas with seven services in five languages.
Nothing new conceptually — only the number of moving parts.

| Service | Stack | Container port | Role |
| --- | --- | --- | --- |
| [ecommerce-ui](microservices/ecommerce-ui/) | React + Express | 4000 | UI + API gateway |
| [product-catalog](microservices/product-catalog/) | Node/Express | 3001 | Product list |
| [product-inventory](microservices/product-inventory/) | Python/Flask | 3002 | Stock levels |
| [profile-management](microservices/profile-management/) | Node + JWT | 3003 | Signup / signin |
| [contact-support-team](microservices/contact-support-team/) | Python/Flask | 8000 | Contact form |
| [shipping-and-handling](microservices/shipping-and-handling/) | Go | 8080 | Shipping fees |
| [order-management](microservices/order-management/) | Java / Spring Boot | 9090 | Cart & checkout |

### Run it

```bash
cd module03/microservices
docker compose up --build
```

**The first build takes a long time** (~5–15 min): `order-management` downloads the
whole Maven dependency tree and runs `mvn install`, and `ecommerce-ui` runs
`npm install && npm run build` for a Create-React-App client. Subsequent builds hit the
layer cache. Watch progress with `docker compose logs -f order-management`.

Then open <http://localhost:4000>.

### Smoke-test each service individually

Every service publishes its port, so you can talk to them directly from the host:

```bash
curl -s localhost:3001/api/products | head -c 300      # catalog
curl -s localhost:3002/api/inventory                   # inventory
curl -s "localhost:8080/shipping-fee?product_id=1"     # shipping (Go)
curl -s localhost:8000/api/contact-message             # support
curl -s localhost:9090/api/orders/1/cart               # orders (Spring)

curl -s -X POST localhost:3003/api/signup \
  -H 'Content-Type: application/json' \
  -d '{"firstName":"Ada","lastName":"L","address":"1 St","postalCode":"X","email":"a@b.c","password":"pw"}'
```

### How the calls actually flow

This is the part worth pausing on in the lecture.

```
browser ──/api/products──► ecommerce-ui:4000 ──http://product-catalog:3001──► product-catalog
                            (Express server)
                                                order-management:9090 ──► product-catalog:3001
                                                                      ──► product-inventory:3002
                                                                      ──► shipping-and-handling:8080
```

The React code fetches **relative** URLs — `fetch('/api/products')` in
[ProductList.js](microservices/ecommerce-ui/client/src/pages/ProductList.js) — so the
browser only ever talks to port 4000. The Express server in
[server/routes/products.js](microservices/ecommerce-ui/server/routes/products.js) then
forwards to `${REACT_APP_PRODUCT_API_HOST}:3001`, where that variable is
`http://product-catalog`, injected by compose.

Why it has to be that way: **the browser runs on your Mac, not on the Docker network.**
`http://product-catalog:3001` is meaningless to it. Only a process *inside* the network
can resolve service names — so the UI container proxies. This also removes all CORS
concerns, since everything the browser sees is same-origin.

`order-management` is the pure server-to-server case: three outbound calls, three
service names from `environment:`, mapped onto `@Value("${PRODUCT_CATALOG_API_HOST}")` in
[OrderService.java](microservices/order-management/src/main/java/com/ltp/ordermanagement/service/OrderService.java).
The defaults in
[application.properties](microservices/order-management/src/main/resources/application.properties)
are `http://localhost` — correct when a developer runs everything on their laptop, wrong
in containers, which is exactly why compose overrides them.

### Prove that service names only resolve inside the network

```bash
# From your Mac — the name does not exist out here
curl http://product-catalog:3001/api/products
# curl: (6) Could not resolve host: product-catalog

# From inside the network — resolves and answers
docker compose exec ecommerce-ui getent hosts product-catalog
docker compose exec ecommerce-ui \
  node -e "require('http').get('http://product-catalog:3001/api/products', r => console.log('status', r.statusCode))"
```

Reaching the same service through its *published* port from the host works fine
(`curl localhost:3001/api/products`) — two different paths to one container, which is the
whole distinction between publishing and networking.

### Cleanup

```bash
docker compose down
docker compose down --rmi local   # also delete the images this project built
```

---

# Part 5 — `postgres_ex`: Compose without a build

[postgres_ex/docker-compose.yaml](postgres_ex/docker-compose.yaml) has no `Dockerfile`
at all. Both services are stock images configured purely through environment variables —
the common case for infrastructure.

```bash
cd module03/postgres_ex
docker compose up -d
docker compose ps
```

| Service | Image | URL | Credentials |
| --- | --- | --- | --- |
| `db` | `postgres:15` | `localhost:5432` | `admin` / `admin`, database `users` |
| `pgadmin` | `dpage/pgadmin4` | <http://localhost:5050> | `admin@gmail.com` / `admin` |

### Connect from the host

```bash
docker compose exec db psql -U admin -d users -c '\l'
# or, with a local client:
psql postgresql://admin:admin@localhost:5432/users
```

### Connect from pgAdmin — the network lesson, one more time

Open <http://localhost:5050>, log in, then *Add New Server*:

| Field | Value |
| --- | --- |
| Host | **`db`** — not `localhost` |
| Port | **`5432`** — the container port, not the published one |
| Username / Password | `admin` / `admin` |

`localhost` would be the pgAdmin container itself. pgAdmin is inside the compose
network, so it uses the service name — identical to `DB_HOST=mongo` in Part 3.

Note `container_name: postrgres_server` (typo in the original, kept as-is) — that name is
what `docker ps` shows, but `db` is the DNS name other services use.

### Persistence

`postgres_data:/var/lib/postgresql/data` is a named volume, so your tables survive
restarts:

```bash
docker compose down       # data kept
docker compose down -v    # data destroyed
```

Note pgAdmin has *no* volume here, so its server registrations are lost on `down`. Adding
one is a good exercise.

> These credentials are committed deliberately — they are throwaway teaching values. Real
> projects keep them out of the repo (`.env` + `env_file:`, or a secret manager).

---

# Part 6 — `statusboard`: a real project, two package managers

Every example so far was a toy: a script that prints, or an app whose dependencies fit on
one `pip install` line. `statusboard` is a real project — a Flask app with a
`pyproject.toml`, a lock file, dev dependencies, tests and a folder of lecture fixtures.

It appears twice, because module01 packages it twice:

| | Copied from | Manifest + lock | Port |
| --- | --- | --- | --- |
| [statusboard-uv/](statusboard-uv/) | [module01/04_uv](../module01/04_uv/) | `pyproject.toml` + `uv.lock` | 8000 |
| [statusboard-poetry/](statusboard-poetry/) | [module01/03_poetry](../module01/03_poetry/) | `pyproject.toml` + `poetry.lock` | 8001 |

**The application is byte-identical in both** — same `app.py`, `checks.py`, `services.py`,
`incidents.py`, same templates, same CSS. Verify it:

```bash
cd module03
diff statusboard-uv/app.py statusboard-poetry/app.py && echo identical
```

Only the manifest, the lock file and the Dockerfile differ. So this is a controlled
experiment: everything that differs between the two images is attributable to the
packaging tool.

### Run both

```bash
(cd statusboard-uv     && docker compose up -d --build)
(cd statusboard-poetry && docker compose up -d --build)
```

<http://localhost:8000> and <http://localhost:8001> — a table of six public sites with
status codes and latency, plus a Cloudflare incidents tab. Both tabs make real outbound
requests, so the containers need internet.

> Port 8000 is also used by `contact-support-team` in Part 4. If both are up, change the
> left-hand number in the compose file.

## The uv build — five instructions

```dockerfile
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
WORKDIR /app
COPY . .
RUN uv sync --frozen --no-dev
CMD ["/app/.venv/bin/flask", "--app", "app", "run", "--host", "0.0.0.0", "--port", "8000"]
```

The same shape as `python-script` in Part 1.1. Three lines are worth a sentence.

**`FROM ghcr.io/astral-sh/uv:...`** — Python 3.12 with the `uv` binary already baked in,
published by uv's authors. Without it the first thing the build would do is install a
package manager. Picking a base image that already contains your toolchain is usually the
cheapest simplification available.

**`RUN uv sync --frozen --no-dev`** replaces `COPY requirements.txt` + `RUN pip install -r
requirements.txt` from every other Python example in this module, and is strictly better:

- **`--frozen`** installs exactly the versions `uv.lock` pins, and *fails* if the lock
  disagrees with `pyproject.toml` rather than silently re-resolving. The image built today
  and the image built in six months contain the same packages. Module 01 made this
  argument about your laptop; a server is the same argument with higher stakes. Compare
  with `flask-node`, whose `requirements.txt` pins `Flask==2.0.1` by hand and pins none of
  Flask's own dependencies — reproducible until the day one of them releases.
- **`--no-dev`** skips the `[dependency-groups] dev` entries — pytest, ruff, bandit,
  pre-commit. Twelve packages instead of forty-odd. `product-inventory` in Part 4 has no
  such distinction: its `requirements.txt` is whatever was needed, and all of it ships.

**`COPY . .`** copies far less than it looks like, because
[.dockerignore](statusboard-uv/.dockerignore) is doing real work. The copy inherited
`bandit_demo/`, `mypy_demo/`, `conflict/` and `pyproject.reference.toml` from module01 —
fixtures for demonstrating linters, with no business in a runtime image. Worse, `.venv/`
is a *macOS* virtualenv that would land on top of the Linux one the build creates.
`tests/` and the exported `requirements.txt` are excluded too. Check what shipped:

```bash
docker run --rm statusboard-uv ls /app
```

Same lesson as Part 1.3, with a project messy enough for it to matter.

## The Poetry build — six instructions

```dockerfile
FROM python:3.12-slim-bookworm
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
RUN pip install --no-cache-dir poetry==2.4.1
WORKDIR /app
COPY . .
RUN poetry install --without dev
CMD ["/app/.venv/bin/flask", "--app", "app", "run", "--host", "0.0.0.0", "--port", "8000"]
```

The `WORKDIR`, `COPY` and `CMD` lines are identical. Everything else differs:

**The extra instruction is `pip install poetry`.** There is no official Poetry base image,
so Poetry has to be installed before it can install anything else — an extra layer, an
extra network round trip, and a tool version somebody has to remember to pin. It is pinned
here to `2.4.1`, the version that generated `poetry.lock`.

**`POETRY_VIRTUALENVS_IN_PROJECT=true`** puts the venv at `/app/.venv` instead of Poetry's
default `~/.cache/pypoetry/virtualenvs/<project>-<hash>-py3.12`, whose name you cannot
write into a `CMD`. That is what lets the two `CMD` lines match. It is also protection
against a real trap — see below.

**`poetry install --without dev`** is `uv sync --no-dev` with different spelling. There is
no `--frozen` equivalent because Poetry refuses to install from a `poetry.lock` that no
longer matches `pyproject.toml` — same guarantee, on by default. `package-mode = false` in
`pyproject.toml` is why `--no-root` is not needed.

### The trap: `POETRY_VIRTUALENVS_CREATE=false`

The most commonly repeated advice is to disable Poetry's virtualenv entirely, reasoning
that a container is already isolated. It saves a line and it is wrong, because **Poetry
itself lives in that system Python.** Build it both ways and read what `poetry install`
prints:

| | `VIRTUALENVS_CREATE=false` | `VIRTUALENVS_IN_PROJECT=true` |
| --- | --- | --- |
| Poetry reports | `7 installs` | `12 installs` |
| Packages the app can import | ~50 | 12 |
| Where `requests` came from | **Poetry's dependency tree** | `poetry.lock` |
| Image size | 309 MB | 332 MB |

Poetry depends on `requests`, `urllib3`, `certifi`, `idna` and `charset-normalizer`
itself. With a shared environment those five were *already satisfied*, so Poetry skipped
them and the app imported whichever versions Poetry needed. On this project they happened
to match the lock file. Nothing guarantees that, and nothing tells you when it stops being
true. A lock file you do not actually install from is decoration.

Worth doing live: it is a two-character edit that makes the number on screen change.

## Side by side

| | uv | Poetry |
| --- | --- | --- |
| Dockerfile instructions | 5 | 6 |
| Tool comes from | official base image | a `pip install` layer |
| Install | `uv sync --frozen --no-dev` | `poetry install --without dev` |
| Reproducibility | explicit `--frozen` | implicit; stale lock is an error |
| Venv location | `/app/.venv` by default | needs `POETRY_VIRTUALENVS_IN_PROJECT` |
| Final image | 268 MB | 332 MB |

```bash
docker images --format '{{.Repository}}\t{{.Size}}' | grep statusboard
```

The 64 MB gap is Poetry and its ~40 dependencies sitting in the finished image with
nothing left to do. Both tools produced the same twelve application packages at the same
versions; the difference is entirely what the *tool* left behind. A second build stage
would delete both tools from the final image and close most of the gap — which is the
first row of the next table.

## What minimal costs

Five or six lines is the right starting point and the wrong ending point. Both Dockerfiles
leave the same things out, and each row is a good exercise:

| Left out | Consequence | Fix |
| --- | --- | --- |
| Dependency layer before source | Editing `app.py` re-runs the whole install | `COPY pyproject.toml uv.lock ./` → install → `COPY . .` |
| A second stage | The package manager ships to production | Install in one image, `COPY --from=builder /app/.venv` into `python:3.12-slim` |
| `USER` | Runs as root — verify with `docker run --rm statusboard-uv whoami` | `RUN useradd -u 1000 app` + `USER app` |
| `HEALTHCHECK` | `docker ps` shows `Up`, never `healthy` | `HEALTHCHECK CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/static/style.css')"` |
| A real server | Flask's dev server, which warns about itself on startup | Add gunicorn, re-lock, `gunicorn --bind 0.0.0.0:8000 app:app` |

The caching one bites first — demonstrate it:

```bash
cd statusboard-uv
docker compose build          # installs everything
touch app.py
docker compose build          # uv sync runs AGAIN, because COPY . . invalidated it
```

Reorder the three instructions and the second build says `CACHED`. That is the trick from
Part 1.3, and the first thing to add once a project has more than a handful of
dependencies. It matters more in the Poetry build, where the install step is slower.

The health check is also the missing half of Part 3's `depends_on` caveat: with one
defined, other services can wait for readiness rather than mere start.

```yaml
depends_on:
  statusboard-uv:
    condition: service_healthy
```

## State and containers

Add a service through either form, then:

```bash
docker compose down && docker compose up -d
```

Your service is still there — but only because the compose file bind-mounts the one file
that holds it:

```yaml
volumes:
  - ./services.json:/app/services.json
```

Remove that line and the addition is gone, because **a container's filesystem dies with
the container**. There are three ways out, in increasing order of correctness:

1. **Bind mount** (used here) — a host path into the container. Good for config and for
   live-reloading source in development; ties the container to a host layout.
2. **Named volume** (Parts 3 and 5) — Docker-managed storage, survives `down`, no host
   path. The right choice for a database's data directory.
3. **Don't keep state in the container at all** — put it in Postgres, as `todos/` and
   `zoo_api/` do at the repo root. [services.py](statusboard-uv/services.py) makes this
   argument itself in its module docstring, about lost writes and race conditions, before
   Docker enters the picture.

---


## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| `ECONNREFUSED 127.0.0.1:<port>` in a container | Using `localhost` for another container | Use the service/container name |
| `getaddrinfo ENOTFOUND <name>` / `unknown host` | Not on the same user-defined network, or default bridge (no DNS) | Same compose project, or `docker network create` + `--network` |
| `Bind for 0.0.0.0:5432 failed: port is already allocated` | Something else owns the host port | `lsof -i :5432`, stop it, or change the left side of `"5433:5432"` |
| Code change not reflected | Image was not rebuilt | `docker compose up -d --build` |
| `no matching manifest for linux/arm64` | amd64-only base image | `--platform linux/amd64` |
| Stale data after schema/env change | Old named volume reused | `docker compose down -v` |
| Build unexpectedly slow / huge context | Missing `.dockerignore` | Ignore `node_modules/`, `target/`, `.git/` |

## Global cleanup

```bash
docker compose down -v                   # per project, from its directory
docker ps -a                             # what is still around
docker system df                         # disk used by images/containers/volumes/cache
docker system prune                      # remove stopped containers, unused networks, dangling images
docker system prune -a --volumes         # nuke everything unused, volumes included
```

## Command reference

| Task | Plain Docker | Compose |
| --- | --- | --- |
| Build | `docker build -t name .` | `docker compose build` |
| Start | `docker run -d --name n -p 80:80 img` | `docker compose up -d` |
| Stop & remove | `docker rm -f n` | `docker compose down` |
| Logs | `docker logs -f n` | `docker compose logs -f svc` |
| Shell | `docker exec -it n sh` | `docker compose exec svc sh` |
| Network | `docker network create net` + `--network net` | automatic |
| Env var | `-e KEY=value` | `environment:` / `env_file:` |
| Volume | `-v vol:/path` | `volumes:` |
