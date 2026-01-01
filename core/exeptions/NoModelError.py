class NoModelError(Exception):
    
    def __init__(self, provider_name: str):
        self.message = f"Провайдер {provider_name} не смог получить имя ИИ модели"
        super().__init__(self.message)