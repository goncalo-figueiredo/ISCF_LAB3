import grpc
import logging
from concurrent import futures

# Importar os módulos gerados pelo Protobuf
import inventory_pb2
import inventory_pb2_grpc

class InventoryOptimizationServicer(inventory_pb2_grpc.InventoryOptimizationServicer):
    
    def OptimizeInventory(self, request, context):
        """
        Implementação do RPC OptimizeInventory.
        Recebe um pedido (request) e o contexto da chamada (context).
        """
        
        # 1. Validação de Dados (Requisito do enunciado)
        if request.current_stock < 0 or request.predicted_demand < 0 or request.reorder_level < 0:
            # Retorna um erro gRPC apropriado usando o contexto
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Stock, procura e nível de encomenda não podem ser negativos.")

        # 2. Lógica do Servidor (Baseada no enunciado)
        # if current_stock < predicted_demand + reorder_level: recommend REORDER or SCALE_UP
        if request.current_stock < (request.predicted_demand + request.reorder_level):
            action = inventory_pb2.InventoryAction.REORDER
            reorder_qty = (request.predicted_demand + request.reorder_level) - request.current_stock
            msg = "O stock atual é insuficiente. Necessário encomendar."
        
        # else: recommend NO_ACTION or SCALE_DOWN
        else:
            action = inventory_pb2.InventoryAction.NO_ACTION
            reorder_qty = 0
            msg = "O stock atual é suficiente para a procura prevista."

        # 3. Criar e devolver a Resposta
        return inventory_pb2.InventoryResponse(
            item_id=request.item_id,
            reorder_quantity=reorder_qty,
            action=action,
            explanation=msg
        )

# ... mantém o método OptimizeInventory antigo aqui em cima ...

    def StreamOptimizeInventory(self, request, context):
        """
        Implementação do RPC com Server Streaming.
        Recebe uma lista de pedidos e envia as respostas uma a uma.
        """
        print(f"Recebido pedido de streaming para {len(request.requests)} itens.")
        
        for single_req in request.requests:
            # 1. Validação de Dados
            if single_req.current_stock < 0 or single_req.predicted_demand < 0 or single_req.reorder_level < 0:
                # No streaming, se houver erro num item, podemos saltar ou enviar uma mensagem de erro na explicação
                yield inventory_pb2.InventoryResponse(
                    item_id=single_req.item_id,
                    reorder_quantity=0,
                    action=inventory_pb2.InventoryAction.NO_ACTION,
                    explanation=f"Erro: Valores negativos não permitidos para o item {single_req.item_id}."
                )
                continue

            # 2. Lógica de Decisão
            if single_req.current_stock < (single_req.predicted_demand + single_req.reorder_level):
                action = inventory_pb2.InventoryAction.REORDER
                reorder_qty = (single_req.predicted_demand + single_req.reorder_level) - single_req.current_stock
                msg = f"Stock insuficiente para {single_req.item_id}. Necessário encomendar."
            else:
                action = inventory_pb2.InventoryAction.NO_ACTION
                reorder_qty = 0
                msg = f"Stock suficiente para {single_req.item_id}."

            # 3. Enviar a resposta em fluxo contínuo (yield)
            yield inventory_pb2.InventoryResponse(
                item_id=single_req.item_id,
                reorder_quantity=reorder_qty,
                action=action,
                explanation=msg
            )

def serve():
    # Cria um servidor gRPC usando uma "pool" de threads
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Adiciona o nosso serviço ao servidor 
    inventory_pb2_grpc.add_InventoryOptimizationServicer_to_server(InventoryOptimizationServicer(), server)
    
    # Define a porta de escuta
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Servidor gRPC a correr na porta 50051...")
    
    # Mantém o servidor a correr até ser interrompido manualmente (Ctrl+C)
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig()
    serve()