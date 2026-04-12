FROM oven/bun:1

WORKDIR /app

COPY frontend/package.json frontend/bun.lockb* ./

RUN bun install

COPY frontend ./

EXPOSE 3000

CMD ["bun", "run", "dev"]