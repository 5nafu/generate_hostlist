import logging
import re
from os import listdir
from os.path import isfile, join


class GenerateGenders(object):
    def __init__(self, inputdirectories, gendersfile, domainconfig, verbosity='WARNING'):
        self.inputdirectories = inputdirectories
        self.gendersfile = gendersfile
        self.log = self.create_logger(verbosity)
        self.domainconfig = domainconfig
        self.hosts = {}

    def create_logger(self, verbosity):
        logger = logging.getLogger(__name__)
        logger.setLevel(getattr(logging, verbosity))
        console_logger = logging.StreamHandler()
        formatter = logging.Formatter('%(levelname)s:%(message)s')
        console_logger.setFormatter(formatter)
        logger.addHandler(console_logger)
        return logger

    def debug(self, message):
        self.log.debug(message)

    def info(self, message):
        self.log.info(message)

    def warning(self, message):
        self.log.warning(message)

    def critical(self, message):
        self.log.critical(message)

    def get_all_hosts_from_directory(self, directory):
        self.info("Getting hosts from '%s'" % directory)
        hostlist = []
        for filename in listdir(directory):
            if isfile(join(directory, filename)) and filename.endswith(".yaml") and len(filename) > 5:
                self.log.debug("Found host '%s'" % filename[:-5])
                hostlist.append(filename[:-5])
        return hostlist

    def get_attributes_from_hostname(self, hostname):
        for domain in self.domainconfig.keys():
            if hostname.endswith(domain):
                try:
                    return re.match(self.domainconfig[domain], hostname).groupdict()
                except AttributeError:
                    self.warning("Hostname '{}' does not match the Regex '{}'".format(
                        hostname,
                        self.domainconfig[domain]
                    ))
        self.warning("Could not get attributes from hostname '{}'. No matching config found.".format(hostname))

    def get_json_from_file(self, filename):
        pass
