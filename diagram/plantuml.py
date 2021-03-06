from __future__ import absolute_import
from .base import BaseDiagram
from .base import BaseProcessor
from subprocess import Popen as execute, PIPE, STDOUT
from os.path import abspath, dirname, exists, join
from tempfile import NamedTemporaryFile


class PlantUMLDiagram(BaseDiagram):
    def __init__(self, processor, text):
        super(PlantUMLDiagram, self).__init__(processor, text)
        self.file = NamedTemporaryFile(suffix='.png')

    def generate(self):
        puml = execute(
            [
                'java',
                '-jar',
                self.proc.plantuml_jar_path,
                '-pipe',
                '-tpng'
            ],
            stdin=PIPE,
            stdout=self.file)
        puml.communicate(self.text)
        if puml.wait() != 0:
            print "Error Processing Diagram:"
            print self.text
            return
        else:
            return self.file


class PlantUMLProcessor(BaseProcessor):
    DIAGRAM_CLASS = PlantUMLDiagram
    PLANTUML_VERSION_STRING = 'PlantUML version 7232'

    def load(self):
        self.find_plantuml_jar()
        self.check_plantuml_version()

    def find_plantuml_jar(self):
        self.plantuml_jar_file = 'plantuml-%s.jar' % (7232,)
        self.plantuml_jar_path = None

        self.plantuml_jar_path = abspath(
            join(
                dirname(__file__),
                self.plantuml_jar_file
            )
        )
        assert exists(self.plantuml_jar_path), \
            "can't find " + self.plantuml_jar_file

    def check_plantuml_version(self):
        puml = execute(
            [
                'java',
                '-jar',
                self.plantuml_jar_path,
                '-version'
            ],
            stdout=PIPE,
            stderr=STDOUT
        )
        version_output = ''
        first = True

        while first or puml.returncode is None:
            first = False
            (stdout, stderr) = puml.communicate()
            version_output += stdout

        print "Version Detection:"
        print version_output

        assert puml.returncode == 0, "PlantUML returned an error code"
        assert self.PLANTUML_VERSION_STRING in version_output, \
            "error verifying PlantUML version"

    def extract_blocks(self, view):
        pairs = (
            (
                start, view.find('@end', start.begin()))
                for start in view.find_all('@start')
            )
        return (view.full_line(start.cover(end)) for start, end in pairs)
