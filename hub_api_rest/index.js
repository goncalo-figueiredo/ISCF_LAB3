const express = require('express');
const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');
const path = require('path');

const app = express();
app.use(express.json());

app.use(express.static(path.join(__dirname, 'public')));

// 1. Carregar o ficheiro .proto
const PROTO_PATH = path.join(__dirname, 'inventory.proto');
const packageDefinition = protoLoader.loadSync(PROTO_PATH, {
    keepCase: true,
    longs: String,
    enums: String,
    defaults: true,
    oneofs: true
});
const inventoryProto = grpc.loadPackageDefinition(packageDefinition).inventory;

// 2. Criar os clientes gRPC
const javaClient = new inventoryProto.InventoryOptimization('localhost:50052', grpc.credentials.createInsecure());
const pythonClient = new inventoryProto.InventoryOptimization('localhost:50051', grpc.credentials.createInsecure());

// ENDPOINT 1: Simples (O que testámos e já funciona)
app.post('/api/analyze', (req, res) => {
    const { item_id, current_stock, reorder_level } = req.body;
    console.log(`\n[HUB] Pedido simples recebido para o item: ${item_id}`);

    const javaRequest = {
        item_id: item_id,
        current_stock: parseInt(current_stock) || 0,
        predicted_demand: 0,
        reorder_level: parseInt(reorder_level) || 0
    };

    javaClient.OptimizeInventory(javaRequest, (error, javaResponse) => {
        if (error) {
            console.error('[HUB] Erro ao ligar ao Java (MS1):', error.message);
            return res.status(500).json({ error: 'Erro no serviço de previsão (Java)' });
        }

        const predictedDemand = javaResponse.predicted_demand;

        const pythonRequest = {
            item_id: item_id,
            current_stock: parseInt(current_stock) || 0,
            predicted_demand: predictedDemand,
            reorder_level: parseInt(reorder_level) || 0
        };

        pythonClient.OptimizeInventory(pythonRequest, (error, pythonResponse) => {
            if (error) {
                console.error('[HUB] Erro ao ligar ao Python (MS2):', error.message);
                return res.status(500).json({ error: 'Erro no serviço de inventário (Python)' });
            }

            res.json({
                item_id: pythonResponse.item_id,
                predicted_demand: predictedDemand,
                current_stock: current_stock,
                recommended_action: pythonResponse.action,
                quantity_to_order: pythonResponse.reorder_quantity,
                explanation: pythonResponse.explanation
            });
        });
    });
});

// ENDPOINT 2: Server Streaming (Novo!)
app.post('/api/analyze-bulk', async (req, res) => {
    const { items } = req.body; // Espera um array de itens
    console.log(`\n[HUB] Pedido BULK (Streaming) recebido para ${items.length} itens.`);

    try {
        const processedRequests = [];

        // Para cada item recebido, vamos falar com o Java um a um para obter a previsão
        for (const item of items) {
            const javaRequest = {
                item_id: item.item_id,
                current_stock: parseInt(item.current_stock) || 0,
                predicted_demand: 0,
                reorder_level: parseInt(item.reorder_level) || 0
            };

            // Promessa para garantir que esperamos pela resposta do Java antes de avançar
            const javaResponse = await new Promise((resolve, reject) => {
                javaClient.OptimizeInventory(javaRequest, (err, response) => {
                    if (err) reject(err);
                    else resolve(response);
                });
            });

            // Guardamos o objeto formatado com a previsão calculada pelo Java
            processedRequests.push({
                item_id: item.item_id,
                current_stock: parseInt(item.current_stock) || 0,
                predicted_demand: javaResponse.predicted_demand,
                reorder_level: parseInt(item.reorder_level) || 0
            });
        }

        // Agora que temos a lista toda com previsões do Java, disparamos o STREAM para o Python
        console.log(`[HUB] A enviar lista para o Stream do Python...`);
        const bulkRequest = { requests: processedRequests };
        const pythonStream = pythonClient.StreamOptimizeInventory(bulkRequest);

        const finalResults = [];

        // Ouvir os dados que vêm do fluxo (stream) do Python
        pythonStream.on('data', (response) => {
            console.log(`[HUB] Stream recebeu dados do Python para o item: ${response.item_id}`);
            finalResults.push({
                item_id: response.item_id,
                recommended_action: response.action,
                quantity_to_order: response.reorder_quantity,
                explanation: response.explanation
            });
        });

        // Quando o stream do Python terminar, devolvemos a lista acumulada ao cliente REST
        pythonStream.on('end', () => {
            console.log(`[HUB] Stream do Python concluído com sucesso.`);
            res.json({ success: true, results: finalResults });
        });

        pythonStream.on('error', (err) => {
            console.error('[HUB] Erro no Stream do Python:', err.message);
            res.status(500).json({ error: 'Erro durante o processamento de stream no Python' });
        });

    } catch (error) {
        console.error('[HUB] Erro no fluxo bulk:', error.message);
        res.status(500).json({ error: 'Erro ao processar previsões em lote' });
    }
});

// Iniciar o servidor HTTP na porta 3000
const PORT = 3000;
app.listen(PORT, () => {
    console.log(`============= HUB API REST ATIVO =============`);
    console.log(`À escuta em http://localhost:${PORT}`);
    console.log(`===============================================`);
});