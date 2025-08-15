import base64
import qrcode
import re
from io import BytesIO
from typing import Any, Optional, Tuple

# ******************************************************************************************
# Includes useful tools to create the content.
# ******************************************************************************************

##################################          
# Creates a QR code as an image.: https://pypi.org/project/qrcode/3.0/
# --------------------------------
# Parameter:
#   text: Text to be included in the QR code.
#   **kwargs: List of parameters which properties the QR code should have. (e.g. version, box_size, error_correction, border etc.)
def get_qr(text, **kwargs):
    qr = qrcode.QRCode(**kwargs)
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image()
    img = img.get_image()
    return img

##################################          
# Converts an image to Base64
# --------------------------------
# Parameter:
#   img: Image file
def get_img_b64(img):
    stream = BytesIO()
    img.save(stream, format='png')
    return str(base64.b64encode(stream.getvalue()), encoding='ascii')

def to_int(value: Any) -> int:
    """
    Convert a value to an integer, preserving any detected scale/unit.

    The value may be:
      - an int or float
      - a string beginning with a valid integer or float, optionally followed by a unit/scale

    Returns:
        tuple[int, Optional[str]]:
            - The integer value (only if it has no fractional part)
            - The scale/unit as a string, or None if no scale is present

    Raises:
        ValueError: If the numeric part has a fractional component
                    (e.g. "3.5cm") and would require rounding.
        TypeError: If the value cannot be parsed as a number.
    """
    num, scale = get_number_and_scale(value)
    if float(num).is_integer():
        return int(num), scale
    raise ValueError(f"Non-integer numeric value {num!r} cannot be converted to int without rounding")

def to_float(value):
    """
    Convert a value to a floating-point number, preserving any detected scale/unit.

    The value may be:
      - an int or float
      - a string beginning with a valid integer or float, optionally followed by a unit/scale
      - None (returned unchanged as None for the numeric part)

    Returns:
        tuple[float, Optional[str]]:
            - The numeric value as a float
            - The scale/unit as a string, or None if no scale is present

    Raises:
        TypeError: If the value is not None and cannot be parsed as a number.
    """
    num, scale = get_number_and_scale(value)
    return float(num), scale

def get_number_and_scale(value: Any) -> Tuple[float, Optional[str]]:
    """
    Extract a numeric value and any trailing scale/unit from the input.

    The input may be:
      - int or float: returns (float(value), None)
      - numeric string: "123" or "3.5" → (float, None)
      - numeric string with unit: "210mm", "3.5cm", "50%" → (float, "mm"/"cm"/"%")
      - numeric string with decimal but no leading zero: ".75in" → (0.75, "in")

    Returns:
        tuple[float, Optional[str]]:
            - The numeric part converted to float
            - The trailing scale/unit string, stripped of whitespace, or None if absent

    Raises:
        TypeError:
            - If value is None
            - If value cannot be parsed into a numeric part and optional scale
    """
    _re_number_and_remainder = re.compile(r"^\s*([+-]?\d+(?:\.\d+)?)(.*)$")
    if value is None:
        raise TypeError("None is not a numeric value")
    if isinstance(value, (int, float)):
        return float(value), None
    if isinstance(value, str):
        m = _re_number_and_remainder.match(value.strip())
        if m:
            num_s, scale = m.groups()
            return float(num_s), (scale.strip() or None)
    raise TypeError(f"Cannot parse {value!r} as a number with optional scale")

