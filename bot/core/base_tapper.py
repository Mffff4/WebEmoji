class BaseTapper:
    def log_message(self, message) -> str:
        return f"<ly>{self.session_name}</ly> | {message}" 