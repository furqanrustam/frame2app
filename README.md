# Frame2App

**Frame2App** is a lightweight Python library that automatically creates interactive GUI forms from pandas DataFrames using `ipywidgets`.

It is designed for **Google Colab** and **Jupyter Notebook** users who want to quickly create input forms, machine learning demo interfaces, data-entry forms, and notebook-based mini apps without manually creating sliders, dropdowns, text boxes, checkboxes, and buttons one by one.

---

## Main Idea

```text
pandas DataFrame + automatic/manual/hybrid field configuration + flexible callbacks
→ interactive notebook GUI
```

Instead of manually writing:

```python
age = widgets.IntSlider(...)
gender = widgets.Dropdown(...)
submit_button = widgets.Button(...)
```

you can write:

```python
from frame2app import AutoForm

app = AutoForm(data=df)
app.display()
```

Frame2App inspects the DataFrame and creates suitable widgets automatically.

---

## Why Frame2App?

Notebook users often build quick GUIs for:

- machine learning prediction demos
- disease prediction apps
- network intrusion detection demos
- fraud detection forms
- student performance prediction
- loan approval demos
- customer churn demos
- data-entry forms
- survey forms
- rule-based systems
- API testing forms
- teaching and classroom examples

Frame2App makes this process faster by generating the form from the data structure.

---

## Key Features

- Automatic GUI generation from pandas DataFrames
- Fully manual field configuration
- Hybrid mode: automatic widgets with manual overrides
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
  - accordion, if supported by your installed version
- Useful for ML demos, notebook apps, forms, and data collection workflows

---

## Installation

### Install from PyPI

```bash
pip install frame2app
```

### Install from GitHub

```bash
pip install git+https://github.com/furqanrustam/frame2app.git
```

### Install locally for development

```bash
git clone https://github.com/furqanrustam/frame2app.git
cd frame2app
pip install -e .
```

---

## Google Colab Setup

For Google Colab, use the following installation command to avoid cached or stale package versions:

```python
import sys

!"{sys.executable}" -m pip install --no-cache-dir --force-reinstall frame2app
```

Then enable the Colab widget manager:

```python
from google.colab import output
output.enable_custom_widget_manager()
```

Then import:

```python
from frame2app import AutoForm
```

If widgets still do not appear, restart the Colab runtime:

```text
Runtime → Restart runtime
```

Then run the import and widget code again.

---

## Quick Colab Test

```python
import sys

!"{sys.executable}" -m pip install --no-cache-dir --force-reinstall frame2app

from google.colab import output
output.enable_custom_widget_manager()
```

```python
import pandas as pd
from frame2app import AutoForm

df = pd.DataFrame({
    "age": [18, 25, 32, 45, 60],
    "gender": ["Male", "Female", "Female", "Male", "Female"],
    "income": [20000, 35000, 50000, 70000, 90000],
    "target": [0, 1, 0, 1, 1]
})

def run(values):
    print("Values:")
    print(values)

app = AutoForm(
    data=df,
    target="target",
    title="Colab Frame2App Test",
    buttons={
        "Run": run,
        "Show Values": "show_values",
        "As DataFrame": "to_dataframe",
        "Reset": "reset",
        "Clear Output": "clear_output"
    }
)

app.display()
```

---

## Basic Automatic Usage

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
    title="Automatic GUI",
    buttons={
        "Submit": submit,
        "Show Values": "show_values",
        "As DataFrame": "to_dataframe",
        "Reset": "reset",
        "Clear Output": "clear_output"
    }
)

app.display()
```

---

## Automatic GUI Generation

Frame2App automatically selects widgets based on DataFrame column types and cardinality.

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

Hybrid mode allows you to generate most widgets automatically and customize only selected fields.

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
        "Show Values": "show_values",
        "Reset": "reset"
    },
    title="Hybrid Auto + Custom GUI"
)

app.display()
```

This means:

- `age` uses your custom slider settings
- `gender` uses your custom radio buttons
- `city` uses your custom dropdown
- all other fields are generated automatically

---

## Fully Manual Mode

You can also define every widget yourself.

```python
app = AutoForm(
    data=df,
    title="Manual GUI",
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
        "Show Values": "show_values",
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
| `"validate"` | Run validation checks, if supported by installed version |

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
        "Show Values": "show_values",
        "Reset": "reset"
    }
)

app.display()
```

---

## Exporting Values

After displaying an app, you can access form values programmatically.

```python
values = app.get_values()
```

Example output:

```python
{
    "age": 30,
    "income": 50000,
    "gender": "Female"
}
```

Export as a one-row DataFrame:

```python
row_df = app.to_dataframe()
```

Export as JSON, if supported by your installed version:

```python
json_data = app.to_json()
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
| `range_slider` | Integer range slider, if supported by installed version |
| `float_range_slider` | Float range slider, if supported by installed version |
| `html` | HTML display widget, if supported by installed version |

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
| `data` | `pandas.DataFrame` | Input DataFrame used to infer fields |
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

## Testing a PyPI Installation

To make sure you are testing the PyPI version and not a local editable install, use a clean virtual environment.

```bash
python -m venv frame2app_test_env
frame2app_test_env\Scripts\activate
python -m pip install --upgrade pip
python -m pip install frame2app
```

Check the installation:

```bash
python -c "from frame2app import AutoForm; import frame2app; print(frame2app.__version__); print('PyPI install working')"
```

Check where the package is loaded from:

```bash
python -c "import frame2app; print(frame2app.__file__)"
```

The path should point to `site-packages`, not your local development folder.

---

## Troubleshooting

### Colab widgets do not appear

Run:

```python
import sys

!"{sys.executable}" -m pip uninstall frame2app -y
!"{sys.executable}" -m pip install --no-cache-dir --force-reinstall frame2app

from google.colab import output
output.enable_custom_widget_manager()
```

Then restart the runtime and run your notebook again.

### Jupyter says `ModuleNotFoundError`

Make sure the package is installed in the same Python environment used by Jupyter:

```python
import sys
print(sys.executable)
```

Then install using that Python:

```python
import sys

!"{sys.executable}" -m pip install frame2app
```

### Buttons work but output is not visible

Try using:

```python
app = AutoForm(
    data=df,
    output=False,
    buttons={
        "Run": submit,
        "Reset": "reset"
    }
)

app.display()
```

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

Check package before upload:

```bash
python -m pip install twine
python -m twine check dist/*
```

Upload to TestPyPI:

```bash
python -m twine upload --repository testpypi dist/*
```

Upload to PyPI:

```bash
python -m twine upload dist/*
```

---

## Publishing Notes

Before publishing a new version, update `pyproject.toml`:

```toml
[project]
name = "frame2app"
version = "0.1.1"
description = "Flexible DataFrame-based GUI builder for Colab and Jupyter using ipywidgets."
authors = [
    { name = "Furqan Rustam", email = "furqan.rustam1@gmail.com" }
]

[project.urls]
Homepage = "https://github.com/furqanrustam/frame2app"
Repository = "https://github.com/furqanrustam/frame2app"
Issues = "https://github.com/furqanrustam/frame2app/issues"
```

Also update the version in:

```python
frame2app/__init__.py
```

Example:

```python
__version__ = "0.1.1"
```

Then clean old build files:

```bash
rmdir /s /q dist
rmdir /s /q build
rmdir /s /q frame2app.egg-info
```

Rebuild:

```bash
python -m build
python -m twine check dist/*
```

Upload:

```bash
python -m twine upload dist/*
```

Important: PyPI does not allow uploading the same version twice. Every new release must use a new version number.

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
