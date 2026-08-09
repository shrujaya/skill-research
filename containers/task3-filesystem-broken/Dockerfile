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

# Permission fault: lock one ordinary file as root-owned + unreadable, after the
# broad chown above so this step wins for this single file. Since the container
# always runs as non-root `agent`, this file becomes genuinely unreadable/unmovable.
RUN chown root:root /home/agent/inbox/roadtrip.jpg \
    && chmod 000 /home/agent/inbox/roadtrip.jpg

USER agent
WORKDIR /home/agent

CMD ["/bin/bash"]
