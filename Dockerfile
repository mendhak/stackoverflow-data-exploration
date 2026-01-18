FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y \
    cmake \
    g++ \
    make \
    git \
    libexpat1 \
    libexpat1-dev \
    libpqxx-dev \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /app

RUN git clone https://github.com/sth/sodata.git . && \
    mkdir -p build && \
    cd build && \
    cmake .. && \
    make pgimport && \
    cp pgimport /usr/local/bin/

WORKDIR /data

ENTRYPOINT ["pgimport"]
CMD ["-h"]
