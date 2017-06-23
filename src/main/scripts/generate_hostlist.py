#! /usr/bin/env python
import argparse


def parse_args():
    parser = argparse.ArgumentParser(description='Generate genders file from Puppet host list')
    parser.add_argument("-g",
                        "--gendersfile",
                        help="Write to this genders file (/etc/genders)",
                        default="/etc/genders"
                        )
    parser.add_argument("-4",
                        "--puppet4",
                        help="Directory of Puppet4 host list (Puppet4/hieradata/hosts)",
                        default='Ops-Hiera/hosts',
                        action='store',
                        )
    parser.add_argument("-3",
                        "--puppet3",
                        help="Directory of Puppet3 host list (Ops-Hiera/hosts)",
                        default='Ops-Hiera/hosts',
                        action='store',
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
    return parser.parse_args()


def main():
    args = parse_args()
    genders_generator = GenerateGenders(args.verbosity, args.puppet3, args.puppet4, args.gendersfile)


if __name__ == '__main__':
    main()
