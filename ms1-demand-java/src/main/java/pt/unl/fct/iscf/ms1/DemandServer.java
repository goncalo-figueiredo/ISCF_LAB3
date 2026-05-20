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

            int predictedDemand = request.getPredictedDemand();
            if (predictedDemand == 0) {
                predictedDemand = 65;
            } else {
                predictedDemand = (int) (predictedDemand * 1.2);
            }

            // Construir a resposta com os campos exatos que existem no teu .proto
            InventoryResponse response = InventoryResponse.newBuilder()
                    .setItemId(request.getItemId())
                    .setPredictedDemand(predictedDemand) // Já vai funcionar!
                    .setReorderQuantity(0) // O Java põe a zero, quem calcula isto é o Python
                    .setAction(InventoryAction.NO_ACTION)
                    .setExplanation("Previsão calculada em Java (MS1) com base numa tendência de +20%.")
                    .build();

            responseObserver.onNext(response);
            responseObserver.onCompleted();
        }
    }
}