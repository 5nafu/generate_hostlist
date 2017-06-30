# coding=utf-8
import shutil
import tempfile
import yaml
import unittest2 as unittest
from os.path import join
from generate_hostlist import GenerateGenders
from mock import patch
from testfixtures import log_capture


class TestGenerateGenders(unittest.TestCase):
    def setUp(self):
        self.genders_creator = GenerateGenders(
            inputdirectories=["bar"],
            domainconfig={
                'domain': '^(?P<hostgroup>.*?)-?\d*\.(?P<domain>[^.]*)$',
                'test': '^(?P<hostgroup>.*?)-?\d*\.(?P<subdomain>[^.]*)\.(?P<domain>[^.]*)$'
            },
            gendersfile="gendersfile"
        )
        self.expected_hosts = {
            "host-name-10.domain": {
                "hostgroup": "host-name",
                "domain": "domain"
            },
            "hostname-20.testsub.test": {
                "hostgroup": "hostname",
                'subdomain': "testsub",
                "domain": "test"
            },
        }
        self.added_filelist = [
            "this.is.a.directory.yaml",
            ".yaml",
        ]

    def mock_isfile(self, filename):
        if filename.endswith("this.is.a.directory.yaml"):
            return False
        return True

    @log_capture()
    def test_logging_works(self, logcapture):
        logging_genders_creator = GenerateGenders(
            inputdirectories=[""],
            domainconfig={},
            gendersfile="",
            verbosity="DEBUG"
        )
        logging_genders_creator.debug("Debug message"),
        logging_genders_creator.info("Info message"),
        logging_genders_creator.warning("Warning message"),
        logging_genders_creator.critical("Critical message"),
        logcapture.check(
            ('generate_hostlist', 'DEBUG', 'Debug message'),
            ('generate_hostlist', 'INFO', 'Info message'),
            ('generate_hostlist', 'WARNING', 'Warning message'),
            ('generate_hostlist', 'CRITICAL', 'Critical message'),
        )

    @patch('generate_hostlist.listdir')
    @patch('generate_hostlist.isfile')
    def test_get_all_hosts_from_directory_returns_hosts(self, isfile_mock, listdir_mock):
        listdir_mock.return_value = ["%s.yaml" % host for host in self.expected_hosts.keys()] + self.added_filelist
        isfile_mock.side_effect = self.mock_isfile
        hostlist = self.genders_creator.get_all_hosts_from_directory("foobar")
        self.assertItemsEqual(hostlist, self.expected_hosts.keys())

    def test_get_correct_attributes_from_hostname(self):
        for hostname in self.expected_hosts.keys():
            self.assertEqual(
                self.genders_creator.get_attributes_from_hostname(hostname),
                self.expected_hosts[hostname],
                msg="Hostname '{}' not asserted".format(hostname)
            )

    @log_capture()
    def test_get_log_for_wrong_regex(self, logcapture):
        self.assertEqual(
            self.genders_creator.get_attributes_from_hostname("foobar.test"),
            {}
        )
        logcapture.check((
            'generate_hostlist',
            'WARNING',
            "Hostname 'foobar.test' does not match the Regex '^(?P<hostgroup>.*?)-?\d*\.(?P<subdomain>[^.]*)\.(?P<domain>[^.]*)$'"
        ))

    @log_capture()
    def test_get_log_for_wrong_domain(self, logcapture):
        self.assertEqual(
            self.genders_creator.get_attributes_from_hostname("foobar.invalid"),
            {}
        )
        logcapture.check((
            'generate_hostlist',
            'WARNING',
            "Could not get attributes from hostname 'foobar.invalid'. No matching config found."
        ))


class TestGenerateGendersWithFiles(unittest.TestCase):
    def setUp(self):
        self.genders_creator = GenerateGenders(
            inputdirectories=[],
            domainconfig={},
            gendersfile=""
        )
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_get_proper_data_from_file(self):
        data = {
            'role': 'foobar',
            'stage': 'somestage',
            'comment': 'This is only an example hiera-file',
            'contact': 'nobody@nowhere.invalid',
            'kostenstelle': '9876',
        }
        filename = join(self.test_dir, 'test.yaml')
        with open(filename, 'w') as f:
            f.write(yaml.dump(data))

        self.assertEqual(
            self.genders_creator.get_config_from_file(filename),
            data
        )

    @log_capture()
    def test_get_no_data_from_incorrect_file(self, logcapture):
        data = "role: 'Foobar"
        filename = join(self.test_dir, 'test.yaml')
        with open(filename, 'w') as f:
            f.write(data)

        self.assertEqual(
            self.genders_creator.get_config_from_file(filename),
            {}
        )
        logcapture.check((
            'generate_hostlist',
            'WARNING',
            "Hostfile '{}' not a proper YAML-File".format(filename)
        ))

    @log_capture()
    def test_get_proper_data_from_file(self, logcapture):
        filename = join(self.test_dir, 'nonexistent.yaml')
        self.assertEqual(
            self.genders_creator.get_config_from_file(filename),
            {}
        )
        logcapture.check((
            'generate_hostlist',
            'WARNING',
            "Could not read host configuration: [Errno 2] No such file or directory: '{}'".format(filename)
        ))
