# Dockerfile — Azure Service Bus Emulator (local)
# Imagem oficial publicada pela Microsoft no Docker Hub:
# https://hub.docker.com/r/microsoft/azure-messaging-servicebus-emulator
FROM microsoft/azure-messaging-servicebus-emulator:latest

VOLUME ["/var/lib/service-bus-emulator"]

EXPOSE 5672 5671

# no diretório que contém o Dockerfile:
# docker build -t sb-emulator .

# publicar as portas para sua máquina:
#    Se preferir TLS, a porta é 5671; sem TLS, 5672.
# docker run -d --name sbemu \
#     -p 5672:5672 \
#     -p 5671:5671 \
#     sb-emulator

# logs
# docker logs -f sbemu
