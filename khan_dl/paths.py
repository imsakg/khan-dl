"""Portable filename components; caller-selected output roots are preserved."""
from pathlib import Path
import re
import unicodedata


_RESERVED = {'CON', 'PRN', 'AUX', 'NUL'} | {
    prefix + str(i) for prefix in ('COM', 'LPT') for i in range(1, 10)
}


def safe_component(value):
    value = unicodedata.normalize('NFC', str(value))
    value = ''.join(c for c in value if not unicodedata.category(c).startswith('C'))
    value = re.sub(r'[<>:"/\\|?*%]', '_', value).strip(' .')
    value = value.encode('utf-8')[:160].decode('utf-8', errors='ignore').rstrip(' .')
    value = value or 'untitled'
    if value.split('.')[0].upper() in _RESERVED:
        value = '_' + value
    return value


def output_template(root, title):
    # Literal percent signs in the user-selected root must not become placeholders.
    return str(Path(root)).replace('%', '%%') + '/' + safe_component(title) + '.%(ext)s'
