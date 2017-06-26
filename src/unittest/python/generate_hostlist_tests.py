
import unittest2 as unittest
from generate_hostlist import GenerateGenders
from mock import patch


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
