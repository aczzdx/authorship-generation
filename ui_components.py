"""
The library for wrapping ipywidgets UI

To render the UI, we should import out and result_out and display them
in a Jupyter notebook.

An example code could be:

from ui_components import show_output, render

show_output()
render()

See UI_refactored.ipynb as an example.
"""

import ipywidgets as widgets
import io
from IPython.display import display
from typing import Optional, Literal, Type, Union
from generate_docx import InitialsGenerator, DocGenerator
from utils import AddressCombinator
from openrefine_caller import openrefine_reconcile, create_project
import pandas as pd

# Outputs

out = widgets.Output()
result_output = widgets.Output()
debug_out = widgets.Output()


def show_output() -> widgets.VBox:
    """ Show the layout of outputs.
    Notice that we should call render() for rendering UI components.
    :return: A ipywidgets Box of outputs
    """
    return widgets.VBox([out, result_output])


def show_debug_output() -> widgets.Output:
    """ Show the debug message.
    Notice that we should call render() for rendering UI components.
    :return: An Output widgets showing debug output
    """
    return debug_out


def render() -> None:
    """ Render all components inside the output widgets

    :return: None
    """

    tab = widgets.Tab()

    generation_tab = GenerationTab().get_tab()
    clean_tab = CleaningTab().get_tab()
    tab.children = [clean_tab, generation_tab]
    tab.set_title(0, "Data Cleaning")
    tab.set_title(1, "Generate Docx")

    title = widgets.HTML("<h1>Authorship Statement Auto Generator</h1>")
    tab.layout = widgets.Layout(width="80%", height="450px", min_width="800px")

    with out:
        out.clear_output()
        display(
            (widgets.VBox([
                title,
                tab,
            ], layout=widgets.Layout(align_items="center"))
            ))

    result_output.clear_output()
    with result_output:
        display((widgets.HTML("<h2>Log</h2>")))

    debug_out.clear_output()
    with debug_out:
        display((widgets.HTML("<h2>Debug output</h2>")))


def labelled_input_generator(label: str, layout_class: Literal['HBox', 'VBox'],
                             text_default_value: Optional[str] = None,
                             layout: Optional[widgets.Layout] = None,
                             text_class: Union[
                                 Type[widgets.Text], Type[widgets.Textarea]] = widgets.Text) -> widgets.Box:
    """Construct a labelled input field.
    :param label:  The label string of the field
    :param layout_class: The name of layout class
    :param text_default_value: The default value for the input.
    :param layout: The user-defined layout, which will override layout_class
    :param text_class: The text widget used for the user input.
    :return: An IPython widget containing a label and a text input field.
    """
    if layout is None:
        if layout_class == 'HBox':
            layout = widgets.Layout(grid_template_columns='1fr 3fr')
        else:
            layout = widgets.Layout(grid_template_columns='1fr')

    return widgets.GridBox([
        widgets.Label(label),
        text_class(value=text_default_value)
    ], layout=layout)


def label_and_input(label, text_default_value=None) -> widgets.Box:
    """
    A helper function to construct a simple labelled input.
    :param label: The label string of the field
    :param text_default_value: The default value for the input
    :return: An Ipython widget containing a label and a text input field.
    """

    return labelled_input_generator(label, 'HBox', text_default_value)


def label_and_vertical_input(label, text_default_value=None) -> widgets.Box:
    """
    A helper function to construct a simple labelled input where the input filed is beneath the label
    :param label: The label string of the field
    :param text_default_value: The default value for the input
    :return: An Ipython widget containing a label and a text input field.
    """
    return labelled_input_generator(label, 'VBox', text_default_value)


def label_and_textarea(label, text_default_value=None) -> widgets.Box:
    """
    A helper function to construct a simple labelled input where the input is a textarea
    :param label: The label string of the field
    :param text_default_value: The default value for the input
    :return: An Ipython widget containing a label and a text input field.
    """
    return labelled_input_generator(label, 'VBox', text_default_value, text_class=widgets.Textarea)


def get_labelled_input_value(box: widgets.Box) -> str:
    """
    Extract the user's input from the field created from labelled_input_generator(...)
    :param box: the widget created from the user
    :return: the value inside the field
    """
    return box.children[1].value


class GenerationTab:
    """A class that will generate the UI for generating docx.

    The UI components will be initialized and configured properly by the class initializer.
    get_tab() will return the constructed tab widget for rendering.
    """

    def __init__(self):
        self.initial_name_tags = widgets.VBox([
            label_and_input("First Name", text_default_value='First Name'),
            label_and_input("Middle Initials", text_default_value='Middle Initial(s)'),
            label_and_input("Last Name", text_default_value="Last Name")
        ])

        self.initial_examples = widgets.VBox([
            label_and_input("Initials for \"Xiang-Zhen\": ", text_default_value="X-Z"),
            label_and_input("Initials for \"Jun Soo\": ", text_default_value="J-S"),
            label_and_input("Initials for \"Baskin-Sommers\": ", text_default_value="B-S"),
            label_and_input("Initials for \"van Rooij\": ", text_default_value="vR")
        ])

        self.generate_column_names = widgets.VBox([
            label_and_input("Full Name: ", text_default_value="Compound Name + highest degree"),
            label_and_input("Role(s): ", text_default_value="Role(s)"),
            label_and_textarea("Affiliations Information (as a Python List of List):",
                               text_default_value="[['Affiliation 1 Department, Institution', "
                                                  "'City (e.g. Brisbane)', 'State', 'Country']]"),
        ])

        self.generate_contribution_priority_order = widgets.VBox([
            label_and_textarea("Roles priority: ", text_default_value="[]")
        ])

        self.accordion = self.init_accordion()

        self.clean_file_upload = widgets.FileUpload(
            accept=".csv",
            multiple=False
        )

        self.start_button = widgets.Button(
            description='Generate docx',
            icon="play",
            tooltip='Generate docx',
        )

        self.generate_status_bar = widgets.Label("")
        self.generated_output_filename = label_and_input("Output Filename:", text_default_value="demo.docx")

        self.generate_tab = widgets.VBox([
            widgets.HBox([self.clean_file_upload, self.start_button, self.generate_status_bar],
                         layout=widgets.Layout(margin="10px")),
            self.generated_output_filename,
            self.accordion
        ])

        self.start_button.on_click = lambda change: self.init_accordion()

    def init_accordion(self) -> widgets.Accordion:
        """Generate the accordion for the generation tab.
        :return: An accordion widget
        """
        accordion = widgets.Accordion(
            [self.initial_name_tags, self.initial_examples,
             self.generate_column_names, self.generate_contribution_priority_order])
        accordion.set_title(0, "Column names for reading authors' name")
        accordion.set_title(1, "Format of initials from giving examples")
        accordion.set_title(2, "Column names for generating authorship documentation")
        accordion.set_title(3, "Roles priority")
        accordion.selected_index = None
        return accordion

    @debug_out.capture()
    def start_generation(self) -> None:
        """ The callback function for generate docx

        It will extract the csv file uploaded by the upload widget, generate initials from the csv and the authorship
        document in docx.
        """
        debug_out.clear_output()
        self.generate_status_bar.value = "Generating..."

        mydict = self.clean_file_upload.value
        if len(mydict) == 0:
            self.generate_status_bar.value = "Error: there is no file uploaded"
        else:
            bytes_val = mydict[next(iter(mydict.keys()))]['content']

            f = io.BytesIO(bytes_val)
            df = pd.read_csv(f)

            initials_generator = self.setup_initials_generators()
            initials = initials_generator.transform(df)
            doc_generator = self.setup_doc_generator(df)
            doc_generator.generate(df, initials['Initial'])

            self.generate_status_bar.value = \
                "Finished! The document was generated at %s" % doc_generator.output_doc_filename

    def setup_doc_generator(self, df: pd.DataFrame) -> DocGenerator:
        """ Construct a DocGenerator and fill in parameters into it

        It will collect information from the member of this class and the data frame.

        :param df: The data frame containing the information of authors
        :return: A configured DocGenerator
        """
        doc_generator = DocGenerator()
        # FIXME: find a better way of input array
        doc_generator.whole_name = get_labelled_input_value(self.generate_column_names.children[0])
        doc_generator.role_tag = self.generate_column_names.children[1].children[1].value
        affiliation_information = eval(get_labelled_input_value(self.generate_column_names.children[2]))
        doc_generator.affiliation_tags = [x[0] for x in affiliation_information]
        for one_list in affiliation_information:
            address_combinator = AddressCombinator()
            address_combinator.tags = one_list
            df[one_list[0]] = df.apply(address_combinator.combine_address, axis=1)
        doc_generator.output_doc_filename = get_labelled_input_value(self.generated_output_filename)
        doc_generator.roles_priority = eval(
            get_labelled_input_value(self.generate_contribution_priority_order.children[0]))
        return doc_generator

    def setup_initials_generators(self):
        """ Construct an InitialsGenerator and fill in parameters into it.

        It will collect information from the member of this class.

        :return: A configured DocGenerator
        """
        initials_generator: InitialsGenerator = InitialsGenerator()
        initials_generator.first_name_tag = self.initial_name_tags.children[0].children[1].value
        initials_generator.middle_initial_tag = self.initial_name_tags.children[1].children[1].value
        initials_generator.last_name_tag = self.initial_name_tags.children[2].children[1].value
        initials_generator.initials_examples = {
            "Xiang-Zhen": get_labelled_input_value(self.initial_examples.children[0]),
            "Jun Soo": get_labelled_input_value(self.initial_examples.children[1]),
            "Baskin-Sommers": get_labelled_input_value(self.initial_examples.children[2]),
            "van Rooij": get_labelled_input_value(self.initial_examples.children[3])
        }
        return initials_generator

    def get_tab(self) -> widgets.VBox:
        """ Get the tab widget for the tab of document generation.
        :return: An IPython widget
        """

        return self.generate_tab


class CleaningTab:
    """ A class for generating the tab of data cleaning process

    The UI components will be initialized and configured by the initializer.
    get_tab() will return the configured widget.
    """

    def __init__(self):
        self.dirty_file_upload = widgets.FileUpload(
            accept=".csv",
            multiple=False
        )

        self.open_refine_go = widgets.Button(
            description="Run OpenRefine",
            icon="play",
            tooltip="Run OpenRefine",
        )

        self.open_refile_status = widgets.Label("")

        self.open_refine_tab = widgets.VBox([
            self.dirty_file_upload,
            label_and_input("Refined Output Filename", text_default_value="authors_refined.csv"),
            label_and_vertical_input("Column names for (Country, City, State)  to reconcile",
                                     text_default_value="""[['City', 'State', 'Country']]"""),
            widgets.HBox([self.open_refine_go, self.open_refile_status])
        ])

        self.email_go = widgets.Button(
            description="Fund Duplicate",
            icon="play",
            tooltip="Find Duplicate"
        )
        self.email_status = widgets.Label("")
        self.email_upload = widgets.FileUpload()
        self.email_column_tags = widgets.VBox([
            self.email_upload,
            label_and_input("Column Name for Email Address", text_default_value='Email Address'),
            widgets.HBox([self.email_go, self.email_status])
        ])
        #

        self.affiliation_go = widgets.Button(
            description="Guess"
        )
        self.affiliation_status = widgets.Label()
        self.affiliation_upload = widgets.FileUpload()
        self.coi_input = label_and_input("Disclousre Tag Name", text_default_value="Conflict of Interest/Disclosures")
        self.funding_input = label_and_input("Funding Tag Name", text_default_value="Funding Acknowledgements")

        self.generate_affiliations_tags = widgets.VBox([
            self.affiliation_upload,
            label_and_input("Output filename: ", text_default_value="authors_reference.csv"),
            widgets.Label(
                "Indices indicating Affiliation Information (indicating [Department, Street, City, Zip, Country] for each "
                "sublist)"),

            widgets.Textarea(value="""[[11, 12, 13, 14, 16],[17,18, 19, 20, 22],[23, 24, 25, 26, 28]]""",
                             layout=widgets.Layout(width='600px')),
            self.coi_input,
            self.funding_input,
            widgets.HBox([self.affiliation_go, self.affiliation_status])
        ])

        self.accordion_for_cleaning = self.setup_accordion()

        self.open_refine_go.on_click(lambda change: self.run_openrefine())
        self.email_go.on_click(lambda change: self.email_deduplicate())
        self.affiliation_go.on_click(lambda change: self.propose_data)

    def setup_accordion(self) -> widgets.Accordion:
        """ Setup for the accordion inside the cleaning tab
        :return: An Ipython accordion widget
        """
        accordion_for_cleaning = widgets.Accordion([self.open_refine_tab,
                                                    self.email_column_tags,
                                                    self.generate_affiliations_tags])
        accordion_for_cleaning.set_title(0, "Use OpenRefine for location naming matching")
        accordion_for_cleaning.set_title(1, "Find duplicate entry")
        accordion_for_cleaning.set_title(2, "Guess the department names")
        accordion_for_cleaning.selected_index = None

        return accordion_for_cleaning

    @debug_out.capture()
    def run_openrefine(self) -> None:
        """ Callback function for call OpenRefine for data reconciliation

        It will transform the csv file into pd.Dataframe, and then call functions from
        openrefine_caller.openrefine_reconcile to communicate with the OpenRefine running in the local
        machine

        """
        mydict = self.dirty_file_upload.value
        bytes_val = mydict[next(iter(mydict.keys()))]['content']

        ff = io.BytesIO(bytes_val)
        df_dirty = pd.read_csv(ff)
        df_dirty.to_csv("temp.csv")

        self.open_refile_status.value = "Calling OpenRefine..."

        output_filename = get_labelled_input_value(self.open_refine_tab.children[1])
        column_tags = eval(get_labelled_input_value(self.open_refine_tab.children[2]))

        project_id = "N/A"
        try:
            project_id = create_project("temp.csv")
            self.open_refile_status.value = "Running Reconciliation, check http://localhost:3333/project?project=" + project_id
            openrefine_reconcile("temp.csv", column_tags, output_csv=output_filename, project_id=project_id)
        except Exception as e:
            self.open_refile_status.value = (
                    "Something wrong happen, please check http://localhost:3333/project?project=" +
                    project_id)
            return

        self.open_refile_status.value = "Finished, the output has been written to %s" % output_filename

    @debug_out.capture()
    def email_deduplicate(self) -> None:
        """ Callback function to deduplicate the email addresses

        Notice that this function will use the global output widget `result_out` for outputting the result.
        """
        import io
        from address_linkage import EmailChecking

        result_output.clear_output()
        mydict = self.email_upload.value
        bytes_val = mydict[next(iter(mydict.keys()))]['content']

        ff = io.BytesIO(bytes_val)
        df_dirty = pd.read_csv(ff)

        email_check = EmailChecking()
        email_check.email_tags = self.email_column_tags.children[1].children[1].value
        duplicated_email = email_check.transform(df_dirty)

        with result_output:
            print("Possible duplicate authors (ordered by email address): ")
            for email_address, group in duplicated_email.groupby(email_check.email_tags):
                display(widgets.HTML("<h3> %s</h3>" % email_address))
                display(group)

        self.email_status.value = "Finished! Please check the following log section for duplicate rows"

    @debug_out.capture()
    def propose_data(self) -> None:
        """ Callback function for adding new columns predicting the existence of COI or funding statement
        """
        from another_record_linkage import DepartmentNameNormalizer
        from annotator import add_coi_and_funding_prediction

        mydict = self.affiliation_upload.value
        bytes_val = mydict[next(iter(mydict.keys()))]['content']
        if len(mydict) == 0:
            self.affiliation_status.value = "Error: there is no file uploaded"
            return

        ff = io.BytesIO(bytes_val)
        df = pd.read_csv(ff)

        output_filename = get_labelled_input_value(self.generate_affiliations_tags.children[1])
        indices = eval(self.generate_affiliations_tags.children[3].value)

        normalizer = DepartmentNameNormalizer()
        normalizer.address_column_indices = indices

        df_referred = normalizer.give_reference(df)

        coi_tag = get_labelled_input_value(self.coi_input)
        funding_tag = get_labelled_input_value(self.funding_input)
        df_referred = add_coi_and_funding_prediction(df_referred, coi_tag=coi_tag, funding_tag=funding_tag)

        df_referred.to_csv(output_filename)
        self.affiliation_status.value = "Finished! The output has been written in %s" % output_filename

    def get_tab(self) -> widgets.VBox:
        """ Get the tab widget for the tab of cleaning

        :return: An IPython widget
        """
        return widgets.VBox([self.accordion_for_cleaning])
