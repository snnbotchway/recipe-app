from django.core.exceptions import ValidationError


def validate_file_size(file):
    """Ensures that the maximum size of the file being uploaded is 2MB."""

    max_size_kb = 2000
    if file.size > max_size_kb * 1024:
        raise ValidationError(
            f"The size of the image specified is {int(file.size / 1000)+1}KB but cannot be larger than {max_size_kb}KB")  # noqa
