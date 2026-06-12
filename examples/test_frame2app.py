import pandas as pd
from frame2app import AutoForm


def test_build_basic():
    df = pd.DataFrame({
        'age': [18, 25, 32, 45, 60],
        'income': [20000, 35000, 50000, 70000, 90000],
        'gender': ['Male', 'Female', 'Female', 'Male', 'Female'],
        'flag': [True, False, True, True, False],
        'target': [0, 1, 0, 1, 1],
    })
    app = AutoForm(data=df, target='target', overrides={'gender': {'widget': 'radio'}})
    ui = app.build()
    assert ui is not None
    assert 'age' in app.widgets
    assert 'gender' in app.widgets
    assert 'target' not in app.widgets


if __name__ == '__main__':
    test_build_basic()
    print('OK')
