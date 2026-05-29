package pt.unl.fct.iscf.ms1;

import io.grpc.Server;
import io.grpc.ServerBuilder;
import io.grpc.stub.StreamObserver;
import inventory.InventoryOptimizationGrpc;
import inventory.Inventory.InventoryRequest;
import inventory.Inventory.InventoryResponse;
import inventory.Inventory.InventoryAction;

import java.io.IOException;

public class DemandServer {

    public static void main(String[] args) throws IOException, InterruptedException {
        // Criar e arrancar o servidor gRPC na porta 50052
        Server server = ServerBuilder.forPort(50052)
                .addService(new DemandServiceImpl())
                .build();

        System.out.println("Servidor gRPC de Previsão (Java) a iniciar na porta 50052...");
        server.start();

        System.out.println("Servidor Java ativo e em escuta!");
        server.awaitTermination();
    }

    // Implementação do Serviço gRPC
    static class DemandServiceImpl extends InventoryOptimizationGrpc.InventoryOptimizationImplBase {

        @Override
        public void optimizeInventory(InventoryRequest request, StreamObserver<InventoryResponse> responseObserver) {
            System.out.println("Recebido pedido de previsão para o item: " + request.getItemId());

            int predictedDemand = 65; // Valor base/default caso não haja histórico

            java.util.List<Integer> history = request.getHistoricalDemandList();

            if (history.size() >= 2) {
                int tamanho = history.size();
                int ultima = history.get(tamanho - 1);       // Última encomenda
                int penultima = history.get(tamanho - 2);    // Penúltima encomenda

                // Média Ponderada: Peso 3 para a última, Peso 1 para a penúltima
                predictedDemand = (int) (((ultima * 3) + (penultima)) / 4.0);

                System.out.println("Cálculo Realizado: Última=" + ultima + ", Penúltima=" + penultima + " -> Previsão Ponderada=" + predictedDemand);
            } else {
                System.out.println(history.size() + " Histórico insuficiente ou vazio. A usar valor padrão: 65");
            }

            // Construir a resposta
            InventoryResponse response = InventoryResponse.newBuilder()
                    .setItemId(request.getItemId())
                    .setPredictedDemand(predictedDemand)
                    .setReorderQuantity(0)
                    .setAction(InventoryAction.NO_ACTION)
                    .setExplanation("Previsão calculada em Java (MS1) usando Média Móvel Ponderada das últimas encomendas.")
                    .build();

            responseObserver.onNext(response);
            responseObserver.onCompleted();
        }
    }
}