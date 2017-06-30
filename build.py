from pybuilder.core import use_plugin, init

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.install_dependencies")
use_plugin("python.flake8")
use_plugin("python.coverage")


name = "generate_hostlist"
default_task = ["install_dependencies", "analyze"]


@init
def set_properties(project):
    project.build_depends_on('unittest2')
    project.build_depends_on('mock')
    project.build_depends_on('testfixtures')
    project.depends_on('PyYAML')
    
