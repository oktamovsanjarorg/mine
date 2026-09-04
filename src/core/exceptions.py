class BotError(Exception):
    """Base exception for the bot."""
    pass

class NotFoundError(BotError):
    """Raised when a resource is not found."""
    pass

class PermissionError(BotError):
    """Raised when user lacks permissions."""
    pass

class ValidationError(BotError):
    """Raised when input validation fails."""
    pass

class RateLimitError(BotError):
    """Raised when rate limits are exceeded."""
    pass

class ExternalAPIError(BotError):
    """Raised when external API calls fail."""
    def __init__(self, message: str, service_name: str, status_code: int):
        super().__init__(message)
        self.service_name = service_name
        self.status_code = status_code

class StorageError(BotError):
    """Raised on storage/minio operations failure."""
    pass

class DatabaseError(BotError):
    """Raised on database operation failure."""
    pass

class ConfigurationError(BotError):
    """Raised when configuration is invalid or missing."""
    pass
