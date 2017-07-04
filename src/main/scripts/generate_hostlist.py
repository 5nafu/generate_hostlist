#! /usr/bin/env python
"""Script to generate a gendersfile from a Puppet host list."""
import argparse
import copy as _copy
from yamlreader import yaml_load, data_merge, YamlReaderError
from generate_hostlist import GenerateGenders


class list2dictStore(argparse._AppendAction):
    def __init__(self,
                 option_strings,
                 dest,
                 nargs=None,
                 const=None,
                 default=None,
                 type=None,
                 choices=None,
                 required=False,
                 help=None,
                 metavar=None):
        if nargs != 2:
            raise ValueError('nargs for list2dictStore actions must be 2; if arg '
                             'strings are not supplying two values to store, '
                             'the append action may be more appropriate')
        super(list2dictStore, self).__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=nargs,
            const=const,
            default=default,
            type=type,
            choices=choices,
            required=required,
            help=help,
            metavar=metavar)

    def __call__(self, parser, namespace, values, option_string=None):
        items = _copy.copy(argparse._ensure_value(namespace, self.dest, {}))
        items[values[0]] = values[1]
        setattr(namespace, self.dest, items)


def __parse_args(*args):
    parser = argparse.ArgumentParser(description='Generate genders file from Puppet host list')
    parser.add_argument("-g",
                        "--gendersfile",
                        help="Write to this genders file (/etc/genders)",
                        )
    parser.add_argument("-i",
                        "--input",
                        help="""Directory of hiera host files.
                        Can be added multiple times.
                        The (short) name (without spaces) will be added
                        as source attribute to the genders file.""",
                        action=list2dictStore,
                        nargs=2,
                        metavar=("NAME", "DIRECTORY")
                        )
    parser.add_argument("-d",
                        "--domain",
                        help="""Configure a domain to be parsed.
                        Host matching a domain will get their hostname
                        parsed by the Regex. Any named group will be
                        added as attribute to the genders file.""",
                        action=list2dictStore,
                        nargs=2,
                        metavar=("DOMAIN", "REGEX")
                        )
    parser.add_argument("-c",
                        "--config",
                        help="""Use a yaml file to configure the script.
                        Possible entries are:
                        gendersfile (str), input (list of tuples),
                        domain (list of tuples), verbosity (one of
                        "DEBUG", "INFO", "WARNING", "CRITICAL")"""
                        )
    verbosity_parser = parser.add_mutually_exclusive_group()
    verbosity_parser.add_argument("-v",
                                  "--verbose",
                                  dest="verbosity",
                                  action='store_const',
                                  const='DEBUG',
                                  help="Print what is happening",
                                  )
    verbosity_parser.add_argument("-s",
                                  "--silent",
                                  dest="verbosity",
                                  action='store_const',
                                  const='CRITICAL',
                                  help="Output only errors",
                                  )
    parser.set_defaults(verbosity='WARNING')
    if args:
        return parser.parse_args(args)
    else:
        return parser.parse_args()


def __main():
    config_data = vars(__parse_args())
    config_data = {key: config_data[key] for key in config_data
                   if config_data[key] is not None}
    if 'config' in config_data:
        try:
            config_data = data_merge(yaml_load(config_data['config']),
                                     config_data)
        except YamlReaderError as exc:
            raise("Could not read configfile: %s" % exc)
    if len(config_data['input']) == 0:
        raise("No input direcotires configured.")
    if 'gendersfile' not in config_data:
        config_data['gendersfile'] = '/etc/genders'
    genders_generator = GenerateGenders(
        config_data.get('input'),
        config_data.get('gendersfile'),
        config_data.get('domain', {}),
        config_data.get('verbosity')
    )
    genders_generator.generate_genders_file()


if __name__ == '__main__':
    __main()
