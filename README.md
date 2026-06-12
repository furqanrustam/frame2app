# Frame2App

**Frame2App** is a lightweight Python library that automatically creates interactive GUI forms from pandas DataFrames using `ipywidgets`.

It is designed for **Google Colab** and **Jupyter Notebook** users who want to quickly create input forms, ML demo interfaces, data-entry forms, and notebook-based mini apps without manually creating sliders, dropdowns, text boxes, and buttons one by one.

---

## Why Frame2App?

In many notebook projects, users repeatedly write code like this:

```python
age = widgets.IntSlider(...)
gender = widgets.Dropdown(...)
submit_button = widgets.Button(...)
```

Frame2App automates this process.

You provide a pandas DataFrame, and Frame2App creates suitable widgets based on the column types.

```python
from frame2app import AutoForm

app = AutoForm(data=df)
app.display()
```

---

## Key Features

- Automatic GUI generation from pandas DataFrames
- Hybrid mode: automatic widgets with manual overrides
- Fully manual widget configuration
- Flexible button names
- Flexible custom callback functions behind buttons
- Built-in button actions
- Works in Jupyter Notebook
- Works in Google Colab
- Export current inputs as:
  - Python dictionary
  - pandas DataFrame
  - JSON
- Basic validation support
- Multiple layout modes:
  - vertical
  - grid
  - horizontal

---

## Installation

### Install from PyPI

After publishing:

```bash
pip install frame2app
```

### Install from GitHub

```bash
pip install git+https://github.com/furqanrustam/frame2app.git
```

### Install locally for development

Clone the repository:

```bash
git clone https://github.com/furqanrustam/frame2app.git
cd frame2app
pip install -e .
```

---

## Google Colab Setup

In Google Colab, install the package and enable the widget manager:

```python
!pip install frame2app

from google.colab import output
output.enable_custom_widget_manager()
```

Then import:

```python
from frame2app import AutoForm
```

---

## Basic Example

```python
import pandas as pd
from frame2app import AutoForm

df = pd.DataFrame({
    "age": [18, 25, 32, 45, 60],
    "income": [20000, 35000, 50000, 70000, 90000],
    "gender": ["Male", "Female", "Female", "Male", "Female"],
    "city": ["London", "Dublin", "Paris", "London", "Berlin"],
    "has_account": [True, False, True, True, False],
    "target": [0, 1, 0, 1, 1]
})

def submit(values):
    print("Values received:")
    print(values)

app = AutoForm(
    data=df,
    target="target",
    buttons={
        "Submit": submit,
        "Reset": "reset",
        "Show Values": "show_values"
    }
)

app.display()
```

---

## Automatic GUI Generation

Frame2App automatically selects widgets based on DataFrame column types.

| Data type | Default widget |
|---|---|
| Integer with many unique values | IntSlider |
| Float | FloatSlider |
| Low-cardinality integer | Dropdown |
| Categorical/string with few unique values | Dropdown |
| Boolean | Checkbox |
| Long text/string | Text |
| Datetime | DatePicker |

Example:

```python
app = AutoForm(
    data=df,
    target="target",
    fields="auto"
)

app.display()
```

---

## Hybrid Mode: Automatic + Custom Widgets

Hybrid mode is one of the main strengths of Frame2App.

You can let Frame2App automatically generate most widgets and customize only selected fields.

```python
app = AutoForm(
    data=df,
    target="target",
    fields="auto",
    overrides={
        "age": {
            "widget": "int_slider",
            "min": 18,
            "max": 100,
            "step": 1,
            "default": 30
        },
        "gender": {
            "widget": "radio",
            "options": ["Male", "Female"],
            "default": "Female"
        },
        "city": {
            "widget": "dropdown",
            "options": ["London", "Dublin", "Paris", "Berlin", "New York"],
            "default": "London"
        }
    },
    buttons={
        "Run": submit,
        "Reset": "reset"
    }
)

app.display()
```

This means:

- `age` is customized
- `gender` is customized
- `city` is customized
- all other fields are automatically generated

---

## Fully Manual Mode

You can also define every widget yourself.

```python
app = AutoForm(
    data=df,
    fields={
        "age": {
            "widget": "int_slider",
            "min": 18,
            "max": 100,
            "step": 1,
            "default": 40
        },
        "income": {
            "widget": "int_text",
            "default": 50000
        },
        "gender": {
            "widget": "radio",
            "options": ["Male", "Female"],
            "default": "Male"
        },
        "city": {
            "widget": "dropdown",
            "options": ["London", "Dublin", "Paris", "Berlin"],
            "default": "Paris"
        },
        "has_account": {
            "widget": "checkbox",
            "default": True
        }
    },
    buttons={
        "Process": submit,
        "Reset": "reset"
    }
)

app.display()
```

---

## Flexible Buttons

Buttons can have any name and can call any Python function.

```python
def save_record(values):
    print("Saving record...")
    print(values)

def generate_report(values):
    print("Generating report...")
    print(values)

def call_api(values):
    print("Calling API with:")
    print(values)

app = AutoForm(
    data=df,
    target="target",
    buttons={
        "Save Record": save_record,
        "Generate Report": generate_report,
        "Call API": call_api,
        "Reset": "reset",
        "Clear Output": "clear_output"
    }
)

app.display()
```

Each custom function receives the current form values as a dictionary:

```python
{
    "age": 30,
    "income": 50000,
    "gender": "Female",
    "city": "London",
    "has_account": True
}
```

---

## Built-in Button Actions

Frame2App includes several built-in button actions.

| Action | Description |
|---|---|
| `"reset"` | Reset widgets to default values |
| `"clear_output"` | Clear output area |
| `"show_values"` | Print current values as a dictionary |
| `"to_dataframe"` | Display current values as a one-row DataFrame |
| `"validate"` | Run validation checks |

Example:

```python
buttons={
    "Show Values": "show_values",
    "As DataFrame": "to_dataframe",
    "Validate": "validate",
    "Reset": "reset",
    "Clear Output": "clear_output"
}
```

---

## Machine Learning Example

Frame2App can be used to create quick ML prediction interfaces.

```python
def predict(values):
    input_df = pd.DataFrame([values])
    prediction = model.predict(input_df)[0]

    print("Input:")
    display(input_df)

    print("Prediction:", prediction)

app = AutoForm(
    data=df,
    target="target",
    title="ML Prediction Demo",
    fields="auto",
    buttons={
        "Predict": predict,
        "Show Input": "to_dataframe",
        "Reset": "reset",
        "Clear Output": "clear_output"
    }
)

app.display()
```

Frame2App does not depend on any specific ML framework. You can use it with:

- scikit-learn
- TensorFlow
- PyTorch
- XGBoost
- LightGBM
- custom rule-based systems
- APIs
- database functions

---

## Data Entry Example

```python
records = []

def save(values):
    records.append(values)
    print("Record saved.")
    print(records)

app = AutoForm(
    data=df,
    fields="auto",
    buttons={
        "Save Record": save,
        "Reset": "reset"
    }
)

app.display()
```

---

## Exporting Values

After displaying an app, you can access form values programmatically.

```python
app.get_values()
```

Returns:

```python
{
    "age": 30,
    "income": 50000,
    "gender": "Female"
}
```

Export as DataFrame:

```python
app.to_dataframe()
```

Export as JSON, if supported by your installed version:

```python
app.to_json()
```

---

## Validation Example

You can add simple validation rules.

```python
def positive_income_validator(value):
    if value < 0:
        return False, "Income cannot be negative."
    return True, ""

app = AutoForm(
    data=df,
    fields={
        "age": {
            "widget": "int_slider",
            "min": 0,
            "max": 120,
            "default": 25,
            "required": True
        },
        "income": {
            "widget": "int_text",
            "default": 50000,
            "validator": positive_income_validator
        }
    },
    buttons={
        "Validate": "validate",
        "Submit": submit,
        "Reset": "reset"
    }
)

app.display()
```

---

## Layouts

Frame2App supports different layout modes.

### Vertical Layout

```python
app = AutoForm(
    data=df,
    layout="vertical"
)

app.display()
```

### Grid Layout

```python
app = AutoForm(
    data=df,
    layout="grid"
)

app.display()
```

### Horizontal Layout

```python
app = AutoForm(
    data=df,
    layout="horizontal"
)

app.display()
```

---

## Supported Widgets

Frame2App currently supports common `ipywidgets` components.

| Widget name | Description |
|---|---|
| `int_slider` | Integer slider |
| `float_slider` | Float slider |
| `int_text` | Integer input box |
| `float_text` | Float input box |
| `dropdown` | Dropdown menu |
| `radio` | Radio buttons |
| `checkbox` | Boolean checkbox |
| `textarea` | Multi-line text area |
| `text` | Single-line text input |
| `date_picker` | Date picker |
| `password` | Password input |
| `file_upload` | File upload widget |
| `combobox` | Editable dropdown, if supported by installed version |
| `select_multiple` | Multi-select widget, if supported by installed version |

---

## API Reference

### AutoForm

```python
AutoForm(
    data,
    fields="auto",
    target=None,
    exclude=None,
    overrides=None,
    buttons=None,
    layout="vertical",
    title=None,
    description_width="160px",
    output=True
)
```

### Parameters

| Parameter | Type | Description |
|---|---|---|
| `data` | pandas.DataFrame | Input DataFrame used to infer fields |
| `fields` | `"auto"`, list, or dict | Controls which fields appear and how |
| `target` | str or None | Target column to exclude from GUI |
| `exclude` | list or None | Columns to exclude |
| `overrides` | dict or None | Custom settings for selected fields |
| `buttons` | dict or None | Button names mapped to actions/functions |
| `layout` | str | `"vertical"`, `"grid"`, or `"horizontal"` |
| `title` | str or None | Optional form title |
| `description_width` | str | Width of widget labels |
| `output` | bool | Whether to use an output area |

---

## Project Structure

Recommended repository structure:

```text
frame2app/
├── frame2app/
│   ├── __init__.py
│   └── core.py
├── examples/
│   └── frame2app_all_tests.ipynb
├── tests/
│   └── test_frame2app.py
├── pyproject.toml
├── README.md
├── LICENSE
└── .gitignore
```

---

## Development

Install in editable mode:

```bash
pip install -e .
```

Run basic tests:

```bash
python test_frame2app.py
```

Build package:

```bash
python -m pip install build
python -m build
```

Upload to PyPI:

```bash
python -m pip install twine
twine upload dist/*
```

---

## Publishing Notes

Before publishing, update `pyproject.toml`:

```toml
[project]
name = "frame2app"
version = "0.1.0"
description = "Flexible DataFrame-based GUI builder for Colab and Jupyter using ipywidgets."
authors = [
    { name = "Furqan Rustam", email = "furqan.rustam1@gmail.com" }
]

[project.urls]
Homepage = "https://github.com/furqanrustam/frame2app"
Repository = "https://github.com/furqanrustam/frame2app"
Issues = "https://github.com/furqanrustam/frame2app/issues"
```

If the PyPI name `frame2app` is already taken, change the package name, for example:

```toml
name = "frame2app-gui"
```

The Python import can still remain:

```python
from frame2app import AutoForm
```

---

## Suggested GitHub Topics

Add these topics to the GitHub repository:

```text
python
pandas
ipywidgets
jupyter
google-colab
gui
form-builder
machine-learning
data-science
notebook
```

---

## Roadmap

Planned improvements:

- Better validation system
- More layouts
- Form sections
- Tabs and accordions
- Better styling and themes
- Model helper functions
- JSON schema export
- Streamlit/Gradio bridge
- More examples
- Documentation website

---

## License

This project is licensed under the MIT License.

---

## Author

**Furqan Rustam**

GitHub: [furqanrustam](https://github.com/furqanrustam)

---

## Citation

If you use Frame2App in teaching, demos, or research projects, please cite or link to the GitHub repository:

```text
https://github.com/furqanrustam/frame2app
```
