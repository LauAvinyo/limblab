class LimbLabError(Exception):
    """Base exception for all limblab errors."""


class VolumeProcessingError(LimbLabError):
    """Raised when a volume processing operation (clean, rotate, extract, etc.) fails."""