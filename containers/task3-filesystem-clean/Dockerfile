FROM ubuntu:24.04

RUN apt-get update && apt-get install -y --no-install-recommends \
    coreutils file ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /bin/bash agent

COPY build_inbox.sh /tmp/build_inbox.sh
RUN chmod +x /tmp/build_inbox.sh \
    && /tmp/build_inbox.sh /home/agent/inbox \
    && rm /tmp/build_inbox.sh \
    && chown -R agent:agent /home/agent/inbox

USER agent
WORKDIR /home/agent

CMD ["/bin/bash"]
