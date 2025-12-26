
def normalize_metric(value: str) -> int:
    """
    Convert metric strings like '1.2K', '1M', '1,234' to integers.
    Returns 0 if conversion fails.
    """
    if not value or value == 'N/A' or value == '':
        return 0
        
    value = str(value).upper().strip()
    
    # Remove common non-numeric chars except . and multipliers
    value = value.replace(',', '').replace('VIEWS', '').replace('LIKES', '').strip()
    
    multiplier = 1
    if 'K' in value:
        multiplier = 1000
        value = value.replace('K', '')
    elif 'M' in value:
        multiplier = 1000000
        value = value.replace('M', '')
    elif 'B' in value:
        multiplier = 1000000000
        value = value.replace('B', '')
        
    try:
        return int(float(value) * multiplier)
    except ValueError:
        return 0
