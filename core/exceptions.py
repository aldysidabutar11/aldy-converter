class AldyConverterError(Exception):
    """Base exception for Aldy Converter"""
    pass

class PDFCorruptedError(AldyConverterError):
    """Raised when a PDF file is corrupted or cannot be read"""
    pass

class UnsupportedFormatError(AldyConverterError):
    """Raised when a file format is not supported for the requested operation"""
    pass

class DependencyMissingError(AldyConverterError):
    """Raised when an external dependency (like MS Word, LibreOffice, Tesseract) is missing"""
    pass