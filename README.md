# 📦 Sistema de Otimização de Inventário - ISCF (Lab 3)

Este projeto implementa uma arquitetura de microserviços em rede para a gestão inteligente de inventário de um centro de distribuição. O ecossistema está dividido em três componentes que comunicam via HTTP/REST e gRPC.

## 🗺️ Arquitetura do Sistema

1. **Frontend / Dashboard (Web):** Interface gráfica para simular e visualizar as decisões em tempo real.
2. **Hub / Orchestrator (Node.js):** Ponto de entrada REST que orquestra as chamadas gRPC para os microserviços.
3. **MS1 - Previsão de Procura (Java):** Calcula a previsão de vendas com base no ID do item.
4. **MS2 - Otimização de Inventário (Python + Docker):** Aplica as regras de negócio em fluxo (Server Streaming gRPC).

---

## 🚀 Como Correr o Projeto (Passo a Passo)

Para meter o sistema a funcionar, precisas de abrir **3 terminais** diferentes na tua máquina.

### 1️⃣ Terminal 1: Microserviço Python (MS2)

Navega até à pasta do Python (onde encontras o `Dockerfile`).

```bash
# Construir a imagem Docker
docker build -t ms2-python-server .

# Arrancar o contentor na porta gRPC 50051
docker run -p 50051:50051 ms2-python-server
```

### 2️⃣ Terminal 2: Microserviço Java (MS1)

Abre o projeto Java no teu IDE (IntelliJ IDEA).

- Garante que as dependências do Maven foram descarregadas.
- Corre o ficheiro principal do servidor para levantar o gRPC na porta **50052**.

### 3️⃣ Terminal 3: Hub API REST & Frontend (Node.js)

Navega até à pasta `hub_api_rest`.

```bash
# 1. Instalar as dependências do Node.js (apenas na primeira vez)
npm install

# 2. Arrancar o servidor do Hub
node index.js
```

---

## 💻 Como Testar no Browser

Com os 3 terminais ativos e sem erros:

1. Abre o teu browser e acede a: `http://localhost:3000`
2. **Teste Único:** Introduz `PROD-100` ou `PROD-200`, ajusta os valores de stock e clica em "Analisar Item".
3. **Teste em Lote (Streaming):** Altera os valores na tabela e clica no botão verde "Correr Análise em Lote (Stream)" para ver a tabela gRPC Server Streaming a preencher-se em tempo real.

---

## 🛠️ Nota de Avaliação: Escolha do Streaming (gRPC)

Implementámos a opção **a) Server Streaming**, onde o cliente envia um pedido com vários itens e o servidor responde um a um em fluxo.

**Justificação para a defesa:** Esta abordagem é a mais adequada para cenários de inventário em lote, pois permite que o Hub envie uma lista pesada de uma só vez e vá processando e renderizando os resultados no ecrã à medida que o Python os calcula, sem bloquear a interface à espera do fim de todo o lote.
