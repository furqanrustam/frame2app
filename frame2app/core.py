from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Union

import pandas as pd
import ipywidgets as widgets
from IPython.display import clear_output, display

ButtonAction = Union[str, Callable[[Dict[str, Any]], Any]]
FieldConfig = Dict[str, Any]
Validator = Callable[[Any], Union[bool, str, Tuple[bool, str]]]


class AutoFormError(Exception):
    """Base exception for Frame2App."""


class ValidationError(AutoFormError):
    """Raised when form validation fails."""


@dataclass
class ValidationResult:
    valid: bool
    errors: Dict[str, str]


class AutoForm:
    """
    Flexible DataFrame-driven GUI builder for Colab/Jupyter using ipywidgets.

    Supports:
    - Fully automatic widget generation from pandas DataFrame columns
    - Fully manual field configuration
    - Hybrid automatic + per-column overrides
    - Flexible button names and callbacks
    - Built-in button actions: reset, clear_output, show_values, to_dataframe, validate
    - Input validation hooks
    - Export helpers: dict, DataFrame, JSON
    """

    BUILTIN_ACTIONS = {
        "reset",
        "clear_output",
        "show_values",
        "to_dataframe",
        "validate",
    }

    def __init__(
        self,
        data: pd.DataFrame,
        fields: Union[str, List[str], Dict[str, FieldConfig]] = "auto",
        *,
        target: Optional[str] = None,
        exclude: Optional[List[str]] = None,
        overrides: Optional[Dict[str, FieldConfig]] = None,
        buttons: Optional[Dict[str, ButtonAction]] = None,
        layout: str = "vertical",
        title: Optional[str] = None,
        subtitle: Optional[str] = None,
        description_width: str = "160px",
        width: str = "100%",
        output: bool = True,
        show_output: Optional[bool] = None,
        border: bool = True,
        auto_display_result: bool = True,
    ):
        if not isinstance(data, pd.DataFrame):
            raise TypeError("data must be a pandas DataFrame.")

        if data.empty:
            raise ValueError("data must not be empty. At least one row is needed for inference.")

        self.data = data
        self.target = target
        self.exclude = exclude or []
        self.overrides = overrides or {}
        self.buttons = buttons or {"Submit": "show_values", "Reset": "reset"}
        self.layout = layout
        self.title = title
        self.subtitle = subtitle
        self.description_width = description_width
        self.width = width
        self.border = border
        self.auto_display_result = auto_display_result

        if show_output is not None:
            output = show_output
        self.use_output = output

        self.widgets: Dict[str, widgets.Widget] = {}
        self.button_widgets: Dict[str, widgets.Button] = {}
        self.output_widget = widgets.Output() if self.use_output else None
        self.container: Optional[widgets.Widget] = None

        self.field_configs = self._prepare_fields(fields)

    # ---------------------------------------------------------------------
    # Field preparation and inference
    # ---------------------------------------------------------------------
    def _prepare_fields(
        self,
        fields: Union[str, List[str], Dict[str, FieldConfig]],
    ) -> Dict[str, FieldConfig]:
        if fields == "auto":
            selected_columns = [
                col
                for col in self.data.columns
                if col != self.target and col not in self.exclude
            ]
            prepared = {col: self._infer_field_config(col) for col in selected_columns}

        elif isinstance(fields, list):
            self._validate_columns(fields)
            prepared = {col: self._infer_field_config(col) for col in fields}

        elif isinstance(fields, dict):
            self._validate_columns(list(fields.keys()))
            prepared = {}
            for col, user_config in fields.items():
                base_config = self._infer_field_config(col)
                base_config.update(user_config or {})
                prepared[col] = base_config
        else:
            raise ValueError("fields must be 'auto', a list of column names, or a dict config.")

        # Hybrid mode: automatic/manual fields plus selected overrides.
        for col, override_config in self.overrides.items():
            if col not in self.data.columns:
                raise ValueError(f"Override column '{col}' not found in DataFrame.")
            if col not in prepared:
                prepared[col] = self._infer_field_config(col)
            prepared[col].update(override_config or {})

        return prepared

    def _validate_columns(self, columns: Iterable[str]) -> None:
        missing = [col for col in columns if col not in self.data.columns]
        if missing:
            raise ValueError(f"Columns not found in DataFrame: {missing}")

    def _infer_field_config(self, column: str) -> FieldConfig:
        series = self.data[column].dropna()
        dtype = series.dtype
        label = self._humanize_label(column)

        config: FieldConfig = {
            "label": label,
            "required": False,
            "disabled": False,
            "placeholder": f"Enter {label}",
            "width": "90%",
        }

        if series.empty:
            config.update({"type": "text", "widget": "text", "default": ""})
            return config

        unique_count = int(series.nunique())

        if pd.api.types.is_bool_dtype(dtype):
            config.update({
                "type": "boolean",
                "widget": "checkbox",
                "default": bool(series.mode().iloc[0]),
            })

        elif pd.api.types.is_integer_dtype(dtype):
            # Low-cardinality integers are often category codes, not continuous numbers.
            if unique_count <= 10:
                options = sorted(series.unique().tolist())
                config.update({
                    "type": "categorical",
                    "widget": "dropdown",
                    "options": options,
                    "default": series.mode().iloc[0],
                })
            else:
                config.update({
                    "type": "integer",
                    "widget": "int_slider",
                    "min": int(series.min()),
                    "max": int(series.max()),
                    "step": 1,
                    "default": int(series.median()),
                })

        elif pd.api.types.is_float_dtype(dtype):
            config.update({
                "type": "float",
                "widget": "float_slider",
                "min": float(series.min()),
                "max": float(series.max()),
                "step": self._guess_float_step(series),
                "default": float(series.median()),
            })

        elif pd.api.types.is_datetime64_any_dtype(dtype):
            config.update({
                "type": "date",
                "widget": "date_picker",
                "default": None,
            })

        else:
            # Object/string columns: categorical if low-cardinality, text otherwise.
            if unique_count <= 30:
                options = sorted(series.astype(str).unique().tolist())
                config.update({
                    "type": "categorical",
                    "widget": "dropdown",
                    "options": options,
                    "default": options[0] if options else None,
                })
            else:
                config.update({
                    "type": "text",
                    "widget": "text",
                    "default": "",
                })

        return config

    @staticmethod
    def _humanize_label(column: str) -> str:
        return str(column).replace("_", " ").strip().title()

    @staticmethod
    def _guess_float_step(series: pd.Series) -> float:
        value_range = float(series.max() - series.min())
        if value_range <= 1:
            return 0.01
        if value_range <= 10:
            return 0.1
        return 1.0

    # ---------------------------------------------------------------------
    # Widget creation
    # ---------------------------------------------------------------------
    def _create_widget(self, column: str, config: FieldConfig) -> widgets.Widget:
        widget_type = config.get("widget", "text")
        label = config.get("label", self._humanize_label(column))
        disabled = bool(config.get("disabled", False))

        common_style = {"description_width": self.description_width}
        common_layout = widgets.Layout(width=config.get("width", "90%"))

        if widget_type in ["int_slider", "slider"]:
            return widgets.IntSlider(
                value=int(config.get("default", config.get("min", 0))),
                min=int(config.get("min", 0)),
                max=int(config.get("max", 100)),
                step=int(config.get("step", 1)),
                description=label,
                disabled=disabled,
                style=common_style,
                layout=common_layout,
                continuous_update=bool(config.get("continuous_update", False)),
            )

        if widget_type == "float_slider":
            return widgets.FloatSlider(
                value=float(config.get("default", config.get("min", 0.0))),
                min=float(config.get("min", 0.0)),
                max=float(config.get("max", 1.0)),
                step=float(config.get("step", 0.1)),
                description=label,
                disabled=disabled,
                style=common_style,
                layout=common_layout,
                continuous_update=bool(config.get("continuous_update", False)),
            )

        if widget_type == "range_slider":
            min_value = int(config.get("min", 0))
            max_value = int(config.get("max", 100))
            default = config.get("default", (min_value, max_value))
            return widgets.IntRangeSlider(
                value=tuple(default),
                min=min_value,
                max=max_value,
                step=int(config.get("step", 1)),
                description=label,
                disabled=disabled,
                style=common_style,
                layout=common_layout,
                continuous_update=bool(config.get("continuous_update", False)),
            )

        if widget_type == "float_range_slider":
            min_value = float(config.get("min", 0.0))
            max_value = float(config.get("max", 1.0))
            default = config.get("default", (min_value, max_value))
            return widgets.FloatRangeSlider(
                value=tuple(default),
                min=min_value,
                max=max_value,
                step=float(config.get("step", 0.1)),
                description=label,
                disabled=disabled,
                style=common_style,
                layout=common_layout,
                continuous_update=bool(config.get("continuous_update", False)),
            )

        if widget_type in ["int_text", "number"]:
            return widgets.IntText(
                value=int(config.get("default", 0)),
                description=label,
                disabled=disabled,
                style=common_style,
                layout=common_layout,
            )

        if widget_type in ["float_text", "decimal"]:
            return widgets.FloatText(
                value=float(config.get("default", 0.0)),
                description=label,
                disabled=disabled,
                style=common_style,
                layout=common_layout,
            )

        if widget_type == "dropdown":
            options = list(config.get("options", []))
            default = config.get("default", options[0] if options else None)
            return widgets.Dropdown(
                options=options,
                value=default if default in options else None,
                description=label,
                disabled=disabled,
                style=common_style,
                layout=common_layout,
            )

        if widget_type == "combobox":
            options = [str(x) for x in config.get("options", [])]
            default = str(config.get("default", ""))
            return widgets.Combobox(
                value=default,
                placeholder=config.get("placeholder", f"Select or enter {label}"),
                options=options,
                description=label,
                ensure_option=bool(config.get("ensure_option", False)),
                disabled=disabled,
                style=common_style,
                layout=common_layout,
            )

        if widget_type == "radio":
            options = list(config.get("options", []))
            default = config.get("default", options[0] if options else None)
            return widgets.RadioButtons(
                options=options,
                value=default if default in options else None,
                description=label,
                disabled=disabled,
                style=common_style,
                layout=common_layout,
            )

        if widget_type == "select_multiple":
            options = list(config.get("options", []))
            default = tuple(config.get("default", []))
            return widgets.SelectMultiple(
                options=options,
                value=default,
                description=label,
                disabled=disabled,
                style=common_style,
                layout=common_layout,
            )

        if widget_type == "checkbox":
            return widgets.Checkbox(
                value=bool(config.get("default", False)),
                description=label,
                disabled=disabled,
                indent=bool(config.get("indent", False)),
                layout=common_layout,
            )

        if widget_type == "textarea":
            return widgets.Textarea(
                value=str(config.get("default", "")),
                placeholder=config.get("placeholder", f"Enter {label}"),
                description=label,
                disabled=disabled,
                style=common_style,
                layout=common_layout,
                rows=int(config.get("rows", 4)),
            )

        if widget_type == "date_picker":
            return widgets.DatePicker(
                value=config.get("default", None),
                description=label,
                disabled=disabled,
                style=common_style,
                layout=common_layout,
            )

        if widget_type == "password":
            return widgets.Password(
                value=str(config.get("default", "")),
                placeholder=config.get("placeholder", f"Enter {label}"),
                description=label,
                disabled=disabled,
                style=common_style,
                layout=common_layout,
            )

        if widget_type == "file_upload":
            return widgets.FileUpload(
                description=label,
                disabled=disabled,
                multiple=bool(config.get("multiple", False)),
                layout=common_layout,
            )

        if widget_type == "html":
            return widgets.HTML(value=str(config.get("value", "")))

        # Default fallback: text input.
        return widgets.Text(
            value=str(config.get("default", "")),
            placeholder=config.get("placeholder", f"Enter {label}"),
            description=label,
            disabled=disabled,
            style=common_style,
            layout=common_layout,
        )

    # ---------------------------------------------------------------------
    # Buttons and actions
    # ---------------------------------------------------------------------
    def _create_buttons(self) -> widgets.HBox:
        button_list = []
        for button_name, action in self.buttons.items():
            button = widgets.Button(
                description=str(button_name),
                button_style=self._infer_button_style(str(button_name)),
                tooltip=f"Click {button_name}",
                layout=widgets.Layout(width="auto"),
            )
            button.on_click(self._make_button_handler(str(button_name), action))
            self.button_widgets[str(button_name)] = button
            button_list.append(button)

        return widgets.HBox(button_list, layout=widgets.Layout(gap="8px", flex_flow="row wrap"))

    @staticmethod
    def _infer_button_style(button_name: str) -> str:
        name = button_name.lower()
        if any(word in name for word in ["submit", "run", "predict", "detect", "save", "execute", "send"]):
            return "primary"
        if any(word in name for word in ["reset", "clear"]):
            return "warning"
        if any(word in name for word in ["delete", "remove", "danger"]):
            return "danger"
        if any(word in name for word in ["success", "confirm", "approve"]):
            return "success"
        return ""

    def _make_button_handler(self, button_name: str, action: ButtonAction) -> Callable[[widgets.Button], None]:
        def handler(button: widgets.Button) -> None:
            if self.output_widget is not None:
                with self.output_widget:
                    self._execute_action(button_name, action)
            else:
                self._execute_action(button_name, action)

        return handler

    def _execute_action(self, button_name: str, action: ButtonAction) -> None:
        if action == "clear_output":
            if self.output_widget is not None:
                self.output_widget.clear_output()
            else:
                clear_output()
            return

        # Clear previous output for all other actions, unless user disables it.
        if self.output_widget is not None:
            self.output_widget.clear_output(wait=True)

        if action == "reset":
            self.reset()
            print("Form reset.")
            return

        if action == "show_values":
            print(self.get_values())
            return

        if action == "to_dataframe":
            display(self.to_dataframe())
            return

        if action == "validate":
            result = self.validate()
            if result.valid:
                print("Validation passed.")
            else:
                print("Validation failed:")
                for field, message in result.errors.items():
                    print(f"- {field}: {message}")
            return

        if callable(action):
            validation = self.validate()
            if not validation.valid:
                print("Validation failed:")
                for field, message in validation.errors.items():
                    print(f"- {field}: {message}")
                return

            result = action(self.get_values())
            if self.auto_display_result and result is not None:
                display(result)
            return

        raise ValueError(
            f"Unsupported action for button '{button_name}'. "
            f"Use a callable or one of: {sorted(self.BUILTIN_ACTIONS)}"
        )

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    def build(self) -> widgets.Widget:
        form_items: List[widgets.Widget] = []

        if self.title:
            form_items.append(widgets.HTML(f"<h3 style='margin-bottom: 4px'>{self.title}</h3>"))
        if self.subtitle:
            form_items.append(widgets.HTML(f"<p style='margin-top: 0; color: #555'>{self.subtitle}</p>"))

        field_widgets = []
        for column, config in self.field_configs.items():
            widget = self._create_widget(column, config)
            self.widgets[column] = widget
            field_widgets.append(widget)

        form_items.extend(self._layout_fields(field_widgets))
        form_items.append(self._create_buttons())

        if self.output_widget is not None:
            form_items.append(self.output_widget)

        border_value = "1px solid #ddd" if self.border else "none"
        self.container = widgets.VBox(
            form_items,
            layout=widgets.Layout(border=border_value, padding="12px", width=self.width),
        )
        return self.container

    def _layout_fields(self, field_widgets: List[widgets.Widget]) -> List[widgets.Widget]:
        if self.layout == "horizontal":
            return [widgets.HBox(field_widgets, layout=widgets.Layout(gap="8px", flex_flow="row wrap"))]

        if self.layout == "grid":
            return [
                widgets.GridBox(
                    field_widgets,
                    layout=widgets.Layout(
                        grid_template_columns="repeat(2, minmax(300px, 1fr))",
                        grid_gap="8px",
                    ),
                )
            ]

        if self.layout == "accordion":
            accordion = widgets.Accordion(children=field_widgets)
            for idx, column in enumerate(self.field_configs.keys()):
                accordion.set_title(idx, self.field_configs[column].get("label", self._humanize_label(column)))
            return [accordion]

        # Default vertical layout.
        return field_widgets

    def display(self) -> None:
        display(self.build())

    def get_values(self) -> Dict[str, Any]:
        values: Dict[str, Any] = {}
        for column, widget in self.widgets.items():
            value = getattr(widget, "value", None)
            if isinstance(value, tuple):
                value = list(value)
            values[column] = value
        return values

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame([self.get_values()])

    def to_json(self, **kwargs: Any) -> str:
        return self.to_dataframe().to_json(orient="records", **kwargs)

    def validate(self) -> ValidationResult:
        errors: Dict[str, str] = {}
        values = self.get_values()

        for column, config in self.field_configs.items():
            value = values.get(column)
            label = config.get("label", column)

            if config.get("required", False) and self._is_empty(value):
                errors[column] = f"{label} is required."
                continue

            if value is not None and value != "":
                if "min" in config and isinstance(value, (int, float)) and value < config["min"]:
                    errors[column] = f"{label} must be >= {config['min']}."
                    continue

                if "max" in config and isinstance(value, (int, float)) and value > config["max"]:
                    errors[column] = f"{label} must be <= {config['max']}."
                    continue

            validator = config.get("validator")
            if validator is not None:
                validator_result = validator(value)
                if validator_result is True:
                    continue
                if validator_result is False:
                    errors[column] = f"{label} is invalid."
                elif isinstance(validator_result, str):
                    errors[column] = validator_result
                elif isinstance(validator_result, tuple):
                    is_valid, message = validator_result
                    if not is_valid:
                        errors[column] = str(message)

        return ValidationResult(valid=len(errors) == 0, errors=errors)

    @staticmethod
    def _is_empty(value: Any) -> bool:
        if value is None:
            return True
        if isinstance(value, str) and value.strip() == "":
            return True
        if isinstance(value, (list, tuple, set, dict)) and len(value) == 0:
            return True
        return False

    def reset(self) -> None:
        for column, widget in self.widgets.items():
            config = self.field_configs[column]
            if isinstance(widget, widgets.FileUpload):
                continue
            if "default" in config:
                try:
                    widget.value = config["default"]
                except Exception:
                    pass

    def set_value(self, column: str, value: Any) -> None:
        if column not in self.widgets:
            raise ValueError(f"Column '{column}' has no widget. Has build()/display() been called?")
        self.widgets[column].value = value

    def set_values(self, values: Dict[str, Any]) -> None:
        for column, value in values.items():
            if column in self.widgets:
                self.widgets[column].value = value

    def get_widget(self, column: str) -> widgets.Widget:
        if column not in self.widgets:
            raise ValueError(f"Column '{column}' has no widget. Has build()/display() been called?")
        return self.widgets[column]
