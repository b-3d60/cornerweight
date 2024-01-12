# Verwende ein Basis-Image mit Python
FROM python:3.8

# Setze das Arbeitsverzeichnis im Container
WORKDIR /app

# Kopiere die Anwendungsdateien in das Arbeitsverzeichnis
COPY app.py /app/
COPY templates /app/templates/
COPY weight_logs.db /app/

# Installiere erforderliche Abhängigkeiten
RUN pip install Flask

# Öffne den Port 5000 für die Flask-Anwendung
EXPOSE 5000

# Befehl, der beim Start des Containers ausgeführt wird
CMD ["python", "app.py"]

