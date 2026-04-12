class ApplicationNotFoundError(Exception):
    """Raised when an application id does not exist."""


class EmptyFileError(Exception):
    """Raised when an uploaded file has no content."""


class UnsupportedFileTypeError(Exception):
    """Raised when a file extension or MIME type is not supported."""


class StorageFailureError(Exception):
    """Raised when the storage backend cannot persist an upload."""


class DocumentNotFoundError(Exception):
    """Raised when a document id does not exist."""


class DocumentPageNotFoundError(Exception):
    """Raised when a document page cannot be found."""


class ProcessingFailureError(Exception):
    """Raised when the processing pipeline cannot complete."""
