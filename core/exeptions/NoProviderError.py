class NoProviderError(Exception):
    
    def __init__(self, provider_name: str):
        self.message = f"Провайдер {provider_name} не был корректно инициализирован"
        super().__init__(self.message)