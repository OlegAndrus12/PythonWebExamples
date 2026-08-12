# Docker cheat sheet

Companion to [README.md](README.md). Commands are grouped by what you are trying to do,
not by which noun they start with.

Two conventions throughout:

- `IMAGE` — a name like `statusboard-uv`, `python:3.12-slim`, or an id like `b92fc3127a5c`
- `CTR` — a container name like `statusboard-uv`, or an id. Ids can be abbreviated to any
  unambiguous prefix: `docker logs b92f`.

---

## Is it working?

```bash
docker --version                 # client version
docker compose version           # v2 uses a SPACE; `docker-compose` is the old v1 binary
docker info                      # errors if the daemon is not running
docker system df                 # disk used by images / containers / volumes / build cache
```

---

## Images

| Command | What it does |
| --- | --- |
| `docker build -t NAME .` | build from `./Dockerfile`; `.` is the **build context** |
| `docker build -t NAME -f path/to/Dockerfile ctx/` | Dockerfile and context in different places |
| `docker build --no-cache -t NAME .` | ignore every cached layer |
| `docker build --platform linux/amd64 -t NAME .` | build for another architecture |
| `docker build --target builder -t NAME .` | stop at a named stage in a multi-stage build |
| `docker build --build-arg KEY=value -t NAME .` | pass an `ARG` |
| `docker images` | list local images |
| `docker images NAME --format '{{.Size}}'` | just the size |
| `docker pull IMAGE` | fetch without running |
| `docker tag IMAGE user/name:1.0` | add a second name to the same image |
| `docker push user/name:1.0` | upload (needs `docker login`) |
| `docker rmi IMAGE` | delete; `-f` even if containers reference it |
| `docker history IMAGE` | one row per layer — find what made the image fat |
| `docker inspect IMAGE` | full JSON: env, cmd, layers, labels |
| `docker save IMAGE -o out.tar` / `docker load -i out.tar` | move an image without a registry |

**Build context gotcha.** Everything in the context directory is sent to the daemon before
the build starts. A missing `.dockerignore` next to `node_modules/` or `.venv/` means
uploading hundreds of megabytes on every build.

---

## Running containers

```bash
docker run IMAGE                          # run in the foreground
docker run -d IMAGE                       # detached (background)
docker run --rm IMAGE                     # delete the container when it exits
docker run -it IMAGE bash                 # interactive shell, overriding CMD
docker run -d -p 8088:80 --name web IMAGE # the Part 0 command
```

### Flags worth memorising

| Flag | Meaning |
| --- | --- |
| `-d` | detached — return the prompt immediately |
| `--rm` | auto-remove on exit; use for anything throwaway |
| `-it` | interactive + TTY — required for a usable shell |
| `-p HOST:CONTAINER` | publish a port. **Left = yours, right = the app's** |
| `-P` | publish every `EXPOSE`d port on random host ports |
| `--name NAME` | stable name; also the DNS hostname on a user-defined network |
| `-e KEY=value` | one environment variable |
| `--env-file .env` | a fileful of them |
| `-v NAME:/path` | named volume (Docker-managed) |
| `-v "$PWD":/app` | bind mount (host path) |
| `-w /app` | working directory |
| `--network NET` | join a user-defined network |
| `-u 1000:1000` | run as a specific uid:gid |
| `--entrypoint sh` | replace `ENTRYPOINT`, not just `CMD` |
| `--platform linux/amd64` | run a foreign-arch image under emulation |
| `--restart unless-stopped` | restart policy |

Anything after the image name replaces `CMD`:

```bash
docker run --rm python-script python -c "import sys; print(sys.version)"
```

---

## Inspecting and debugging

```bash
docker ps                        # running containers
docker ps -a                     # including stopped ones
docker ps --format '{{.Names}}\t{{.Ports}}\t{{.Status}}'

docker logs CTR                  # all output so far
docker logs -f --tail=100 CTR    # follow, starting from the last 100 lines

docker exec -it CTR sh           # shell inside a RUNNING container (bash on Debian images)
docker exec CTR env              # one-off command, no TTY needed

docker inspect CTR                                     # everything, as JSON
docker inspect -f '{{.State.Health.Status}}' CTR       # healthcheck state
docker inspect -f '{{.NetworkSettings.IPAddress}}' CTR # IP on the default bridge
docker port CTR                  # actual port mappings
docker top CTR                   # processes inside
docker stats                     # live CPU / memory, all containers
docker diff CTR                  # files changed since the image was built
docker cp CTR:/app/services.json ./   # copy out (works in both directions)
```

**The container exited and you don't know why** — `docker ps -a` for the exit code, then
`docker logs CTR`. Exit 0 = the main process finished normally (a container lives exactly
as long as PID 1). Exit 137 = killed, usually out of memory.

**The image won't even start** — override the entrypoint and look around:

```bash
docker run --rm -it --entrypoint sh IMAGE
```

---

## Lifecycle

```bash
docker stop CTR                  # SIGTERM, then SIGKILL after 10s
docker stop -t 30 CTR            # give it 30s
docker kill CTR                  # SIGKILL immediately
docker start CTR                 # start a stopped container again
docker restart CTR
docker rm CTR                    # delete a stopped container
docker rm -f CTR                 # stop and delete in one go
docker rm -f $(docker ps -aq)    # nuke every container
```

---

## Networks

Why this matters at all: **inside a container, `localhost` is that container.** Two
containers cannot reach each other over loopback, and `-p` does not connect them — it
only connects *you* to one of them. See Part 2 of the README.

```bash
docker network ls
docker network create my-network
docker network inspect my-network        # which containers are attached, and their IPs
docker network connect my-network CTR    # attach a running container
docker network disconnect my-network CTR
docker network rm my-network
docker network prune                     # remove all unused networks
```

| Network | Container-to-container DNS? |
| --- | --- |
| default `bridge` | **No** — IP addresses only, and they change on restart |
| user-defined bridge (`docker network create`) | **Yes** — resolve each other by container name |
| Compose's `<project>_default` | **Yes** — resolve each other by *service* name |
| `--network host` | no isolation; container shares the host stack (Linux only) |
| `--network none` | no networking at all |

Test name resolution from inside:

```bash
docker run --rm --network my-network busybox nslookup other-container
docker compose exec svc getent hosts other-service
```

`busybox` is used because it is tiny and ships `ping`/`nslookup` — most application
images do not.

---

## Volumes and mounts

```bash
docker volume ls
docker volume create data
docker volume inspect data       # includes Mountpoint, the real path on disk
docker volume rm data
docker volume prune              # delete all unused volumes
```

| Form | Syntax | Use for |
| --- | --- | --- |
| Named volume | `-v data:/var/lib/postgresql/data` | database storage; survives `docker rm` |
| Bind mount | `-v "$PWD":/app` | live-reloading source, config files |
| Single file | `-v "$PWD/services.json":/app/services.json` | one config file |
| Read-only | `-v "$PWD":/app:ro` | anything the container should not write |
| tmpfs | `--tmpfs /tmp` | scratch space that never touches disk |

**A container's writable layer dies with the container.** If data must outlive
`docker rm`, it belongs in a volume — or, better, in a database.

---

## Compose

Run from the directory containing `docker-compose.yaml`. `SVC` is a service name from
that file.

| Command | What it does |
| --- | --- |
| `docker compose up` | build if needed, create network, start, stream logs |
| `docker compose up -d` | same, detached |
| `docker compose up -d --build` | force a rebuild first — **the one you want after editing code** |
| `docker compose up -d SVC` | start one service (and its `depends_on`) |
| `docker compose down` | stop and remove containers + networks |
| `docker compose down -v` | ...and delete named volumes (**data loss**) |
| `docker compose down --rmi local` | ...and delete images this project built |
| `docker compose build --no-cache` | rebuild from scratch |
| `docker compose ps` | status of this project's containers |
| `docker compose ls` | all Compose projects running on the machine |
| `docker compose logs -f SVC` | follow one service |
| `docker compose exec SVC sh` | shell into a running service |
| `docker compose run --rm SVC CMD` | one-off container (not the running one) |
| `docker compose restart SVC` | |
| `docker compose stop` / `start` | without removing anything |
| `docker compose config` | print the merged, resolved file — validates syntax |
| `docker compose pull` | refresh images that are not built locally |

**`exec` vs `run`**: `exec` enters the container that is already up; `run` starts a new
throwaway one. Use `exec` for debugging, `run` for tasks like migrations.

**`depends_on` orders startup, not readiness.** For real readiness the dependency needs a
`healthcheck:` and:

```yaml
depends_on:
  db:
    condition: service_healthy
```

---

## Dockerfile reference

| Instruction | Notes |
| --- | --- |
| `FROM image:tag` | first instruction; `AS name` labels a stage |
| `WORKDIR /app` | `cd`, and creates the directory if missing |
| `COPY src dst` | host → image. Respects `.dockerignore` |
| `COPY --from=builder /a /b` | pull from an earlier stage, or another image |
| `COPY --chown=user:group src dst` | set ownership while copying |
| `ADD` | `COPY` plus URL fetching and tar auto-extraction. **Prefer `COPY`** |
| `RUN cmd` | executes at **build** time, creates a layer |
| `CMD ["exe","arg"]` | default command at **run** time; overridden by `docker run … cmd` |
| `ENTRYPOINT ["exe"]` | the fixed executable; `CMD` becomes its default arguments |
| `ENV KEY=value` | set at build time *and* present at runtime |
| `ARG KEY=default` | build time only; not in the final image |
| `EXPOSE 8000` | documentation only — it opens nothing. `-p` is what publishes |
| `USER app` | drop root for everything after it |
| `VOLUME /data` | declare a mount point |
| `HEALTHCHECK CMD …` | non-zero exit = unhealthy |
| `LABEL key=value` | metadata |
| `STOPSIGNAL SIGTERM` | signal sent by `docker stop` |

**Exec form vs shell form.** `CMD ["python", "app.py"]` runs the binary as PID 1 and
receives signals correctly. `CMD python app.py` wraps it in `/bin/sh -c`, which usually
swallows `SIGTERM`, so `docker stop` waits the full 10 seconds and then kills it. Always
use the JSON array form.

### The caching rule

Each instruction is a cached layer. Changing one invalidates it and everything after it.
So: **install dependencies before copying source.**

```dockerfile
COPY pyproject.toml uv.lock ./     # changes rarely
RUN uv sync --frozen --no-dev      # expensive — stays CACHED
COPY . .                           # changes constantly
```

Flip those and every edit to `app.py` reinstalls the world. Verify with:

```bash
docker build -t x . && touch app.py && docker build -t x .   # look for CACHED
```

---

## Cleanup

```bash
docker container prune           # stopped containers
docker image prune               # dangling (untagged) images
docker image prune -a            # every image not used by a container
docker volume prune              # unused volumes
docker network prune             # unused networks
docker builder prune             # build cache

docker system prune              # containers + networks + dangling images
docker system prune -a --volumes # everything unused, volumes included — destructive
```

Check what it would reclaim first:

```bash
docker system df -v
```

---

## Plain Docker ↔ Compose

| Task | `docker` | `docker compose` |
| --- | --- | --- |
| Build | `docker build -t n .` | `build:` in the file, `docker compose build` |
| Start | `docker run -d --name n -p 80:80 img` | `docker compose up -d` |
| Stop & remove | `docker rm -f n` | `docker compose down` |
| Logs | `docker logs -f n` | `docker compose logs -f svc` |
| Shell | `docker exec -it n sh` | `docker compose exec svc sh` |
| Env var | `-e KEY=value` | `environment:` / `env_file:` |
| Port | `-p 8000:8000` | `ports:` |
| Volume | `-v vol:/path` | `volumes:` |
| Network | `docker network create net` + `--network net` | automatic |

---

## Common errors

| Message | Cause | Fix |
| --- | --- | --- |
| `Cannot connect to the Docker daemon` | Docker Desktop is not running | start it, then `docker info` |
| `Bind for 0.0.0.0:8000 failed: port is already allocated` | another container or process owns it | `docker ps`, `lsof -i :8000`, or change the left-hand port |
| `ECONNREFUSED 127.0.0.1:5432` *from inside a container* | using `localhost` for another container | use the service/container name |
| `getaddrinfo ENOTFOUND name` | not on the same user-defined network | same Compose project, or `--network` |
| `no matching manifest for linux/arm64` | amd64-only base image | `--platform linux/amd64` |
| `COPY failed: file not found` | path is outside the build context | move the file in, or widen the context |
| Code change has no effect | image not rebuilt | `docker compose up -d --build` |
| Exit code 137 | OOM-killed | raise the memory limit |
| Stale data after a config change | old named volume reused | `docker compose down -v` |
