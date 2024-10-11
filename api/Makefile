# Параметры теста
THREADS = 12
CONNECTIONS = 12
DURATION = 30s
URL = http://localhost:8080/question
SCRIPT = post.lua

install-wrk:
	@echo "Installing wrk..."
	sudo apt-get update
	sudo apt-get install -y wrk

load-test:
	@echo "Running load test with $(THREADS) threads, $(CONNECTIONS) connections for $(DURATION)..."
	wrk -t$(THREADS) -c$(CONNECTIONS) -d$(DURATION) -s $(SCRIPT) $(URL)

