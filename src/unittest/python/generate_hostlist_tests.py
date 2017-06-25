
import unittest2 as unittest
from generate_hostlist import GenerateGenders
from mock import patch


class TestGenerateGenders(unittest.TestCase):
    def setUp(self):
        self.genders_creator = GenerateGenders(
            inputdirectories=["bar"],
            gendersfile="gendersfile"
        )
        self.expected_hosts = {
            "host-name-10.ipx": {"hostnamegroup": "host-name", "domain": "ipx"},
            "hostname-20.ipx": {"hostnamegroup": "hostname", "domain": "ipx"},
            "host1name-30.ipx": {"hostnamegroup": "host1name", "domain": "ipx"},
            "hostname40.ipx": {"hostnamegroup": "hostname", "domain": "ipx"},
            "hostname-50.fg.stage00.eu.idealo.com": {
                "hostnamegroup": "hostname",
                "functiongroup": "fg",
                "segment": None,
                "environment": "stage",
                "location": "00"
            },
            "host-name-60.fg00.stage00.eu.idealo.com": {
                "hostnamegroup": "host-name",
                "functiongroup": "fg",
                "segment": "00",
                "environment": "stage",
                "location": "00"
            },
            "hostname-70.fg00.stage00.eu.idealo.com": {
                "hostnamegroup": "hostname",
                "functiongroup": "fg",
                "segment": "00",
                "environment": "stage",
                "location": "00"
            },
            "hostname.fg00.stage00.eu.idealo.com": {
                "hostnamegroup": "hostname",
                "functiongroup": "fg",
                "segment": "00",
                "environment": "stage",
                "location": "00"
            },
            "host1-name-80.fg00.stage00.eu.idealo.com": {
                "hostnamegroup": "host1-name",
                "functiongroup": "fg",
                "segment": "00",
                "environment": "stage",
                "location": "00"
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
