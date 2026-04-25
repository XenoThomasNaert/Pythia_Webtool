def validate_sequence(input_value):
    """
    Validate that the input value contains only the characters A, C, T, or G
    and that the length of the input is exactly 40 base pairs.
    """
    # Check if the input value is not None
    if input_value is None:
        raise ValueError('Input is None. A valid sequence must be provided.')

    # Check if the input value contains only A, C, T, or G
    if not all(char in 'ACTG' for char in input_value):
        raise ValueError('Input contains invalid characters. Only A, C, T, or G are allowed.')

    # Check if the length of the input is exactly 40 bp
    if len(input_value) != 40:
        raise ValueError('Input length is invalid. The sequence must be exactly 40 base pairs long.')


def validate_sequence_chars(input_value, field_name="Sequence"):
    """
    Validate that the input value contains only the characters A, C, T, or G (case insensitive).
    Returns (is_valid, error_message) tuple.
    """
    # Check if the input value is not None or empty
    if input_value is None or input_value.strip() == '':
        return False, f'{field_name} is empty. A valid sequence must be provided.'

    # Convert to uppercase for validation
    input_upper = input_value.upper().strip()

    # Check if the input value contains only A, C, T, or G
    invalid_chars = set(char for char in input_upper if char not in 'ACTG')
    if invalid_chars:
        return False, f'{field_name} contains invalid characters: {", ".join(sorted(invalid_chars))}. Only A, C, T, or G are allowed.'

    return True, None
