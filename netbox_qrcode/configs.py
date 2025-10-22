from .utilities import to_int, to_float


class QRPrintConfigValue:
    """
    Represents a single configuration field whose value can come from layered sources
    (e.g., a static configuration default and a higher-priority request-provided value).

    The instance resolves its effective value via the `value` property, preferring `preferred`
    when set, otherwise falling back to `default`. If the declared `field_type` is `int` or
    `float`, the effective value is parsed at initialization time into a numeric component
    (`number`) and an associated scale (`scale`) using the module's numeric parsing helpers.

    Parameters:
    - name (str): Logical field name (identifier) for this config value.
    - field_type (type): Expected type for the value. When `int` or `float`, numeric parsing
        is applied to populate `number` and `scale`.
    - default (str | None): Fallback value used when `preferred` is not provided.
    - preferred (str | None): Highest-priority value (e.g., from a request or user input).

    Attributes:
    - name (str): Field identifier.
    - type (type): Declared field type used to guide parsing (`int`, `float`, etc.).
    - default (str | None): Fallback value.
    - preferred (str | None): Highest-priority value.
    - value (str | None): Resolved effective value (`preferred` if set, else `default`).
    - number (int | float | None): Parsed numeric value if `type` is `int` or `float`, else `None`.
    - scale (str | None): Parsed scale/unit suffix associated with the numeric value, if any,
        else `None`.

    Examples:
    - QRPrintConfigValue("rows", int, default="10") -> value: "10", number: 10, scale: None
    - QRPrintConfigValue("size", float, preferred="12.5mm") -> value: "12.5mm", number: 12.5, scale: "mm"
    """
    def __init__(self, name: str, field_type: type, default: str | None = None, preferred: str | None = None):
        self.name = name
        self.type = field_type
        self.default = default
        self.preferred = preferred
        self.number = None
        self.scale = None

        self.__set_grid()

    @property
    def value(self):
        """Return the best (highest priority) value."""
        if self.preferred is not None:
            return self.preferred
        else:
            return self.default

    def __set_grid(self):
        if self.value is not None:
            if self.type == int:
                self.number, self.scale = to_int(self.value)
            elif self.type == float:
                self.number, self.scale = to_float(self.value)

    def __repr__(self):
        """Debug-friendly representation."""
        return f"<QRPrintConfigValue {self.name}={self.value!r}>"

class QRPrintConfig:
    """Parses print config settings from 2 configuration dicts and exposes them as attributes."""
    field_types: dict[str, type] = {
        'page_rows': int,
        'page_columns': int,
        'label_height': float,
        'label_width': float,
        'page_width': float,
        'page_height': float,
        'page_top_margin': float,
        'page_bottom_margin': float,
        'page_left_margin': float,
        'page_right_margin': float,
    }    

    def __init__(self, default_config: dict, preferred_config: dict):
        self._plugin_config = default_config
        self._preferred_config = preferred_config

        for name, ftype in self.field_types.items():
            default_value = default_config.get(name, None)
            preferred_value = self._preferred_config.get(name, None)
            config_value = QRPrintConfigValue(name, ftype, default=default_value, preferred=preferred_value)
            setattr(self, name, config_value)

    @property
    def scales(self):
        """Return a set of all detected scales in the config."""
        scales = set()
        for name in self.field_types:
            value: QRPrintConfigValue = getattr(self, name)
            if value.scale is not None:
                scales.add(value.scale)
        return scales

    def as_dict(self):
        return {name: getattr(self, name).value for name in self.field_types}