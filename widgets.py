from ipywidgets import interact, interactive, fixed, interact_manual
import ipywidgets as widgets
import pandas as pd


def label_and_input(label, label_layout=None, text_default_value=None, input_layout=None):

    if label_layout is None:
        label_layout = widgets.Layout()
    if text_default_value is None:
        text_default_value = ""
    if input_layout is None:
        input_layout = widgets.Layout()

    return widgets.HBox([
        widgets.Label(label, layout=label_layout),
        widgets.Text(value=text_default_value, input_layout=input_layout)
    ])


def label_and_textarea(label, label_layout=None, text_default_value=None, input_layout=None):

    if label_layout is None:
        label_layout = widgets.Layout()
    if text_default_value is None:
        text_default_value = ""
    if input_layout is None:
        input_layout = widgets.Layout()

    return widgets.HBox([
        widgets.Label(label, layout=label_layout),
        widgets.Textarea(value=text_default_value, input_layout=input_layout)
    ])
initial_name_tags = widgets.VBox([
    label_and_input("First Name", text_default_value='First Name'),
    label_and_input("Middle Initials", text_default_value='Middle Initial(s)'),
    label_and_input("Last Name", text_default_value="Last Name")
])

initial_examples = widgets.VBox([
    label_and_input("Xiang-Zhen: ", text_default_value="X-Z"),
    label_and_input("Jun Soo: ", text_default_value="J-S"),
    label_and_input("Baskin-Sommers: ", text_default_value="B-S"),
    label_and_input("van Rooij: ", text_default_value="vR")
])
