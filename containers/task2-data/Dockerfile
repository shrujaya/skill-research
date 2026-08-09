FROM ubuntu:24.04

RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 python3 ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /bin/bash agent

COPY --chown=agent:agent orders.csv /workspace/orders.csv

USER agent
WORKDIR /workspace

CMD ["/bin/bash"]
