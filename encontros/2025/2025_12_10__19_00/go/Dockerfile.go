FROM golang:1.21-alpine

WORKDIR /app

COPY go.mod ./
RUN go mod download

COPY src ./src

CMD ["go", "run", "./src/benchmark_sequential.go"]
