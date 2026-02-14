import re
from io import BytesIO

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from PIL import Image


_COLOR_RE = re.compile(r"^#?[0-9a-fA-F]{3}$|^#?[0-9a-fA-F]{6}$")
_SHORT_HEX_LENGTH = 4
_LONG_HEX_LENGTH = 7

CATEGORY_TRANSLATIONS = {
    "Your first alphabets": {"ne": "तिम्रा पहिलो अक्षरहरू", "hi": "आपके पहले अक्षर"},
    "Let's learn Nepali": {"ne": "आउनुहोस् नेपाली सिकौं", "hi": "आइए नेपाली सीखें"},
    "Math is fun with us": {"ne": "हामीसँग गणित रमाइलो छ", "hi": "हमारे साथ गणित मजेदार है"},
    "Nepali months": {"ne": "नेपाली महिनाहरू", "hi": "नेपाली महीने"},
    "English Months": {"ne": "अंग्रेजी महिनाहरू", "hi": "अंग्रेजी महीने"},
    "7 days": {"ne": "७ दिन", "hi": "7 दिन"},
    "4 seasons": {"ne": "४ ऋतुहरू", "hi": "4 ऋतुएँ"},
    "Colors": {"ne": "रंगहरू", "hi": "रंग"},
    "Animals": {"ne": "जनावरहरू", "hi": "जानवर"},
    "Human Body": {"ne": "मानव शरीर", "hi": "मानव शरीर"},
    "Birds": {"ne": "चराहरू", "hi": "पक्षी"},
    "Punctuation Marks": {"ne": "विराम चिह्नहरू", "hi": "विराम चिह्न"},
    "World meaning": {"ne": "शब्द अर्थ", "hi": "शब्द अर्थ"},
    "Shapes": {"ne": "आकारहरू", "hi": "आकार"},
}


def _ensure_hash(value: str) -> str:
    if value.startswith("#"):
        return value
    return f"#{value}"


def _expand_short_hex(value: str) -> str:
    return f"#{value[1]}{value[1]}{value[2]}{value[2]}{value[3]}{value[3]}"


def normalize_color(value: str) -> str:
    value = value.strip()
    if not _COLOR_RE.match(value):
        raise ValidationError({"object_color": "Invalid color code."})

    value = _ensure_hash(value)

    if len(value) == _SHORT_HEX_LENGTH:
        value = _expand_short_hex(value)

    return value.lower()


def generate_color_image(hex_color: str) -> ContentFile:
    image = Image.new("RGB", (512, 512), hex_color)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return ContentFile(buffer.getvalue())


def validate_object_fields(object_image, object_color) -> None:
    if object_image and object_color:
        raise ValidationError(
            {
                "object_image": "Provide either object image or object color, not both.",
                "object_color": "Provide either object image or object color, not both.",
            }
        )


def get_category_translation(name: str) -> tuple[str | None, str | None]:
    translations = CATEGORY_TRANSLATIONS.get(name.strip())
    if not translations:
        return None, None
    return translations.get("ne"), translations.get("hi")
