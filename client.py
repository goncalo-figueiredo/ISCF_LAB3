import grpc
import inventory_pb2
import inventory_pb2_grpc

def run():
    # 1. Abrir um canal de comunicação com o servidor na porta correspondente
    print("A tentar conectar ao servidor gRPC...")
    with grpc.insecure_channel('localhost:50051') as channel:
        
        # 2. Criar o Stub (o representante do serviço no cliente)
        stub = inventory_pb2_grpc.InventoryOptimizationStub(channel)

        # 3. Criar um pedido com dados fictícios
        # Neste cenário, o stock (50) é MENOR que a procura prevista (70) + reorder level (10)
        request = inventory_pb2.InventoryRequest(
            item_id="PROD-123",
            current_stock=50,
            predicted_demand=70,
            reorder_level=10
        )

        print(f"\nA enviar pedido para o item '{request.item_id}'...")
        
        # 4. Invocar o RPC no servidor
        try:
            response = stub.OptimizeInventory(request)
            print("\n--- RESPOSTA DO SERVIDOR ---")
            print(f"Item ID: {response.item_id}")
            print(f"Quantidade a encomendar: {response.reorder_quantity}")
            # Em Protobuf, para obtermos o nome do Enum (ex: REORDER) em vez do número (3), usamos:
            action_name = inventory_pb2.InventoryAction.Name(response.action)
            print(f"Ação recomendada: {action_name}")
            print(f"Explicação: {response.explanation}")
            print("----------------------------\n")
            
        except grpc.RpcError as e:
            # Captura os erros que programámos no servidor (ex: valores negativos)
            print(f"\nErro gRPC [{e.code()}]: {e.details()}")

if __name__ == '__main__':
    run()