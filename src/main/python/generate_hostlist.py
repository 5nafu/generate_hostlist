import logging
import re
from yamlreader import yaml_load, YamlReaderError
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
            if ((isfile(join(directory, filename)) and
                 filename.endswith(".yaml") and
                 len(filename) > 5)):
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
                    return {}
        self.warning("Could not get attributes from hostname '{}'.".format(hostname) +
                     " No matching config found.")
        return {}

    def get_config_from_file(self, filename):
        try:
            return yaml_load(filename)
        except YamlReaderError as e:
            self.warning("Hostfile '{}' not a proper YAML-File: {}".format(filename, e))
            return {}

    def get_gender_entry_for_host(self, directory_info, hostname):
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
