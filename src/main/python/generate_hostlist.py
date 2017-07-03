# -*- coding: utf-8 -*-
"""Generating a genders file from hiera data.

This module generates a genders file from directories containing the hiera-data in hostfiles.
The hostname is split by a configurable regex into atributes as is the data from the hostfile.

"""

import logging
import re
from os import listdir
from os.path import isfile, join
from yamlreader import yaml_load, YamlReaderError


class GenerateGenders(object):
    """Generating a genders file from hiera data.

    Args:
        inputdirectories (list of tuples): list of (Name and path) of the parsed directories
        gendersfile (str):                 Full path and filename of target genders file.
                                           WILL BE OVERWRITTEN!
        domainconfig (dict):               Directory of Domains and the corresponding regex to
                                           split the hostnames into attributes.
        verbosity (str):                   Loglevel.
                                           Allowed Keywords: DEBUG, INFO, WARNING, CRITICAL
                                           Default: WARNING
    """

    def __init__(self, inputdirectories, gendersfile, domainconfig, verbosity='WARNING'):
        """See Class docstring."""
        self.inputdirectories = inputdirectories
        self.gendersfile = gendersfile
        self.log = self.__create_logger(verbosity)
        self.domainconfig = domainconfig
        self.hosts = {}

    def __create_logger(self, verbosity):
        logger = logging.getLogger(__name__)
        logger.setLevel(getattr(logging, verbosity, 30))
        console_logger = logging.StreamHandler()
        formatter = logging.Formatter('%(levelname)s:%(message)s')
        console_logger.setFormatter(formatter)
        logger.addHandler(console_logger)
        return logger

    def debug(self, message):
        """Write debug message to logger."""
        self.log.debug(message)

    def info(self, message):
        """Write info message to logger."""
        self.log.info(message)

    def warning(self, message):
        """Write warning message to logger."""
        self.log.warning(message)

    def critical(self, message):
        """Write critical message to logger."""
        self.log.critical(message)

    def get_all_hosts_from_directory(self, directory):
        """Return a list of all hosts from given directory.

        All files ending in '.yaml' will be treated as hiera hostfile,
        stripped of their extention and returned as host.

        Args:
            directory -- Read files from this directory

        Returns:
            A list of hostnames

        """
        self.info("Getting hosts from '%s'" % directory)
        hostlist = []
        for filename in listdir(directory):
            if ((isfile(join(directory, filename)) and
                 filename.endswith(".yaml") and
                 len(filename) > 5)):
                self.debug("Found host '%s'" % filename[:-5])
                hostlist.append(filename[:-5])
        return hostlist

    def get_attributes_from_hostname(self, hostname):
        """Return all attributes parsted from the hostname.

        Parses the given hostname according to the appropiate configuration in self.domainconfig.
        If a hostname has no corresponding domainconfig or does not fit the regex a warning will be
        logged and an empty dict will be returned.

        Args:
            hostname (str): The hostname to be parsed.
        Returns:
            if the domain is configured correctly and the hostname can be parsed:
                a dict of attributes
            else:
                an empty dict.
        """
        for domain in self.domainconfig.keys():
            if hostname.endswith(domain):
                try:
                    return re.match(self.domainconfig[domain], hostname).groupdict()
                except AttributeError:
                    self.warning("Hostname '{}' does not match the Regex '{}'".format(
                        hostname,
                        self.domainconfig[domain]
                    ))
                    return {}
        self.warning("Could not get attributes from hostname '{}'.".format(hostname) +
                     " No matching config found.")
        return {}

    def get_config_from_file(self, filename):
        """Return the host configuration from the hostfile.

        Parses the given YAML-File and returns the content. Will log a warning in case of malformed
        YAML or missing file and return and empty dict

        Args:
            filename (str): a filname (with path) to Read
        Returns:
            on success: a dict of attributes
            on failure: an empty dict
        """
        try:
            return yaml_load(filename)
        except YamlReaderError as exc:
            self.warning("Hostfile '{}' not a proper YAML-File: {}".format(filename, exc))
            return {}

    def get_gender_entry_for_host(self, directory_info, hostname):
        """Return an entry for a genders file.

        Merges the attributes from the parsed hostname and the attributes from the hostfile.

        Args:
            directory_info (tuple): A tuple of (Name and Path) of the source directory for the host
            hostname (str):         A string of the hostname
        Returns:
            a string containing the hostname and all attributes to be used in a genders file
        """
        filepath = join(directory_info[1], hostname + ".yaml")
        config = self.get_attributes_from_hostname(hostname)
        config.update(self.get_config_from_file(filepath))
        config_list = ["source=%s" % (directory_info[0])]
        for (key, value) in config.items():
            value = re.sub(r"[ #,=]", "_", str(value))
            config_list.append('%s=%s' % (key, value))
        config_list.sort()
        config_string = ",".join(config_list)
        return "{}	{}".format(hostname, config_string)

    def generate_genders_file(self):
        """Write the genders file.
        This method will iterate over the directory infos from self.inputdirectories,
        get all hostsfiles and the corresponding attributes and write everything to the
        genders file in self.gendersfile

        Args:
            None
        Return:
            None
        """
        gendersfile_content = []
        self.debug("Writing gendersfile '%s'" % self.gendersfile)
        for directory_info in self.inputdirectories:
            self.debug("Iterating over hosts in '%s'" % directory_info[1])
            for hostname in self.get_all_hosts_from_directory(directory_info[1]):
                gendersfile_content.append(self.get_gender_entry_for_host(directory_info, hostname))
        gendersfile_content.sort()
        try:
            with open(self.gendersfile, 'w') as gendersfilehandler:
                gendersfilehandler.write("\n".join(gendersfile_content))
        except Exception as exc:
            self.critical("Cannot write to gendersfile '%s': %s" % (self.gendersfile, exc))
            raise
