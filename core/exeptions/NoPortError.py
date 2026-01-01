class NoPortError(Exception):
    
    def __init__(self):
        self.message = "Фоновый режим работы требует указания порта для взаимодействия с внешними сервисами!"
        super().__init__(self.message)