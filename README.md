# Frame2App

Frame2App is a flexible DataFrame-based GUI builder for Google Colab and Jupyter Notebook using `ipywidgets`.

It creates interactive GUI forms from pandas DataFrames and lets users attach any custom Python function behind any button.

## Main idea

```text
DataFrame + automatic/manual/hybrid field configuration + flexible callbacks
→ notebook GUI
```

## Features

- Fully automatic GUI generation from a DataFrame
- Fully manual field configuration
- Hybrid mode: automatic for most fields, customized overrides for selected fields
- Flexible button names
- Flexible callback functions
- Built-in actions: `reset`, `clear_output`, `show_values`, `to_dataframe`, `validate`
- Validation support
- Export values as dictionary, DataFrame, or JSON
- Layouts: `vertical`, `grid`, `horizontal`, `accordion`
- Works in Google Colab and Jupyter Notebook

## Installation

```bash
pip install frame2app
```

For Google Colab:

```python
!pip install frame2app
from google.colab import output
output.enable_custom_widget_manager()
```

## Basic automatic usage

```python
import pandas as pd
from frame2app import AutoForm

sample_df = pd.DataFrame({
    "age": [18, 25, 32, 45, 60],
    "income": [20000, 35000, 50000, 70000, 90000],
    "gender": ["Male", "Female", "Female", "Male", "Female"],
    "city": ["London", "Dublin", "Paris", "London", "Berlin"],
    "has_account": [True, False, True, True, False],
    "target": [0, 1, 0, 1, 1]
})

def run_anything(values):
    print("Values received:")
    print(values)

app = AutoForm(
    data=sample_df,
    target="target",
    title="Automatic GUI",
    buttons={
        "Run Anything": run_anything,
        "Show Values": "show_values",
        "As DataFrame": "to_dataframe",
        "Reset": "reset",
        "Clear Output": "clear_output",
    }
)

app.display()
```

## Hybrid automatic + customized fields

```python
app = AutoForm(
    data=sample_df,
    target="target",
    fields="auto",
    overrides={
        "age": {
            "widget": "int_slider",
            "min": 18,
            "max": 100,
            "step": 1,
            "default": 30,
        },
        "gender": {
            "widget": "radio",
            "options": ["Male", "Female"],
            "default": "Female",
        },
        "city": {
            "widget": "combobox",
            "options": ["London", "Dublin", "Paris", "Berlin", "New York"],
            "default": "London",
        },
    },
    buttons={
        "Submit": run_anything,
        "Validate": "validate",
        "Reset": "reset",
    },
    layout="grid",
    title="Hybrid Auto + Custom GUI"
)

app.display()
```

## Fully manual fields

```python
app = AutoForm(
    data=sample_df,
    fields={
        "age": {
            "widget": "int_slider",
            "min": 18,
            "max": 100,
            "default": 30,
            "required": True,
        },
        "income": {
            "widget": "int_text",
            "default": 50000,
            "validator": lambda value: (value >= 0, "Income must be non-negative."),
        },
        "gender": {
            "widget": "dropdown",
            "options": ["Male", "Female"],
            "default": "Male",
        },
    },
    buttons={
        "Process": run_anything,
        "Reset": "reset",
    }
)

app.display()
```

## Supported widget names

- `int_slider`
- `float_slider`
- `range_slider`
- `float_range_slider`
- `int_text`
- `float_text`
- `dropdown`
- `combobox`
- `radio`
- `select_multiple`
- `checkbox`
- `textarea`
- `date_picker`
- `password`
- `file_upload`
- `text`
- `html`

## Built-in button actions

```python
buttons={
    "Show Values": "show_values",
    "Show DataFrame": "to_dataframe",
    "Validate": "validate",
    "Reset": "reset",
    "Clear Output": "clear_output",
}
```

## Custom button function

Every custom function receives the current form values as a dictionary.

```python
def my_function(values):
    print(values)

app = AutoForm(
    data=sample_df,
    buttons={"Run My Function": my_function}
)
```

## Export values

```python
values = app.get_values()
row_df = app.to_dataframe()
json_data = app.to_json()
```

## Local development

```bash
pip install -e .
```

## Build

```bash
pip install build twine
python -m build
```

## Publish

```bash
twine upload dist/*
```
