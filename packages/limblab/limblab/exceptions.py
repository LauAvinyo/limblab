class LimbLabError(Exception):
    """Base exception for all limblab errors."""


class VolumeProcessingError(LimbLabError):
    """Raised when a volume processing operation (clean, rotate, extract, etc.) fails."""

class StagingError(LimbLabError):
    """Raised when limb staging fails."""


class ConnectionError(StagingError):
    """Raised when there is a connection error to the staging server."""