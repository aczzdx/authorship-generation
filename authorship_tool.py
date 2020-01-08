""" The CLI for the whole toolset

Inspired by the OpenRefine's JSON format for indicating operations, it could be a good choice
to use YAML, a JSON variant but allows comments inside. The syntax of YAML is also easy to use.

"""
import argparse
from argparse import ArgumentParser, Namespace
from typing import Union, Text, Sequence, Any, Optional

import yaml

from generate_docx import handle_generating_task


class YAMLParserAction(argparse.Action):

    def __call__(self, parser: ArgumentParser,
                 namespace: Namespace, values: Union[Text, Sequence[Any], None],
                 option_string: Optional[Text] = ...) -> None:
        """ Load the YAML file into a Python diction and saved
        :param parser:  The argparse.parser
        :param namespace:  The namespace will be affected
        :param values: a opened file handler
        :param option_string: optional string, should be None
        :return:
        """
        from io import IOBase

        if option_string is not None:
            raise ValueError("Should not have any option string")

        if not isinstance(values, IOBase):
            raise NotImplementedError("Does not support values other than opened file")

        setattr(namespace, self.dest, yaml.load(values, Loader=yaml.FullLoader))

        values.close()


parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()


def handle_cleaning_task(args: Namespace):
    print("handle_cleaning_task")


# parser for generate files

parser_generate = subparsers.add_parser("generate",
                                        help="Generate a docx from csv")
parser_generate.add_argument("configuration_yaml",
                             type=argparse.FileType("r"),
                             action=YAMLParserAction,
                             help="The filepath to the configuration file in YAML")

parser_generate.set_defaults(handler=handle_generating_task)
# parser for data clean

parser_clean = subparsers.add_parser("clean",
                                     help="Perform data cleaning")
parser_clean.set_defaults(handler=handle_cleaning_task)

args = parser.parse_args()
args.handler(args)
