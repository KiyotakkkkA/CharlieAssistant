class NoClientError(Exception):
    
    def __init__(self, provider_name: str):
        self.message = f"Провайдер {provider_name} не смог корректно инициальзировать клиент для взаимодействия с моделью!"
        super().__init__(self.message)