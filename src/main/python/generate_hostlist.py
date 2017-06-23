import logging
import re
from os import listdir
from os.path import isfile, join


class GenerateGenders(object):
    def __init__(self, puppet3, puppet4, gendersfile, verbosity='WARNING'):
        self.puppet3 = puppet3
        self.puppet4 = puppet4
        self.gendersfile = gendersfile
        self.log = self.create_logger(verbosity)
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
        attributes = {}
        if hostname.endswith(".ipx"):
            attributes = self.get_ipx_attributes(hostname)
        if hostname.endswith(".eu.idealo.com"):
            attributes = self.get_idealocom_attributes(hostname)
        return attributes

    def get_ipx_attributes(self, hostname):
        return {
            'domain': 'ipx',
            'hostnamegroup': re.match("(.*?)-?\d+.ipx", hostname).group(1)
        }

    def get_idealocom_attributes(self, hostname):
        # host1-name-80.fg00.stage00.eu.idealo.com
        regex = "(.*?)-?\d*\.([^.]*?)(\d*)\.([^.]*?)(\d*).eu.idealo.com"
        re_match = re.match(regex, hostname)
        hostnamegroup = re_match.group(1) or None
        functiongroup = re_match.group(2) or None
        segment = re_match.group(3) or None
        environment = re_match.group(4) or None
        location = re_match.group(5) or None
        return {
            "hostnamegroup": hostnamegroup,
            "functiongroup": functiongroup,
            "segment": segment,
            "environment": environment,
            "location": location
        }
