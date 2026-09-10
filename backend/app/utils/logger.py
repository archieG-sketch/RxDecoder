import logging
import re
import sys

# Regex patterns for basic PHI detection to ensure zero PHI leakage in logs
PHI_PATTERNS = [
    (re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'), '[PHONE_MASKED]'),
    (re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'), '[EMAIL_MASKED]'),
    (re.compile(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'), '[DATE_MASKED]'),
    (re.compile(r'\b(MRN|ID|SSN)[:#\s]*\w+\b', re.IGNORECASE), '[ID_MASKED]'),
]
SERVICE_ACCOUNT_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[^\s]+\.gserviceaccount\.com\b')

class PHIFilteringFormatter(logging.Formatter):
    def format(self, record):
        original_msg = super().format(record)
        service_accounts = []

        def preserve_service_account(match):
            service_accounts.append(match.group(0))
            return f"__SERVICE_ACCOUNT_{len(service_accounts) - 1}__"

        sanitized = SERVICE_ACCOUNT_PATTERN.sub(preserve_service_account, original_msg)
        for pattern, replacement in PHI_PATTERNS:
            sanitized = pattern.sub(replacement, sanitized)
        for index, service_account in enumerate(service_accounts):
            sanitized = sanitized.replace(f"__SERVICE_ACCOUNT_{index}__", service_account)
        return sanitized

def get_logger(name: str = "rxdecoder") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            PHIFilteringFormatter(
                "%(asctime)s | %(levelname)-7s | [%(name)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
        )
        logger.addHandler(handler)
        logger.propagate = False
    return logger

logger = get_logger("rxdecoder")
