# ***************************************************************************
# *   Copyright (c) 2017 Markus Hovorka <m.hovorka@live.de>                 *
# *   Copyright (c) 2017 Bernd Hahnebach <bernd@bimstatik.org>              *
# *                                                                         *
# *   This file is part of the FreeCAD CAx development system.              *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************

__title__ = "FreeCAD FEM solver Ratel tasks"
__url__ = "https://www.freecad.org"

## \addtogroup FEM
#  @{

import os
import os.path
import subprocess

from . import ratel_util
import FreeCAD
import codecs
from . import writer
from .. import run
from .. import settings
from femmesh import meshsetsgetter
from femtools import femutils
from femtools import membertools


_inputFileName = None


class Check(run.Check):

    def run(self):
        self.pushStatus("Checking analysis member...\n")
        self.check_mesh_exists()


class Prepare(run.Prepare):

    def run(self):
        mesh_obj = membertools.get_mesh_to_solve(self.analysis)[0]  # pre check done already
        meshdatagetter = meshsetsgetter.MeshSetsGetter(
            self.analysis,
            self.solver,
            mesh_obj,
            membertools.AnalysisMember(self.analysis),
        )
        meshdatagetter.get_mesh_sets()

        w = writer.FemInputWriterRatel(
            self.analysis,
            self.solver,
            mesh_obj,
            meshdatagetter.member,
            self.directory,
            meshdatagetter.mat_geo_sets
        )
        path = w.write_solver_input()
        if path != "" and os.path.isfile(path):
            self.pushStatus("Writing solver input completed.")
        else:
            self.pushStatus("Writing solver input failed.")
            self.fail()
        _inputFileName = os.path.splitext(os.path.basename(path))[0]
        
        

class Solve(run.Solve):

    def run(self):
        self.pushStatus("Executing solver...\n")

        ratel_path = FreeCAD.ParamGet(
                    "User parameter:BaseApp/Preferences/Mod/Fem/Ratel"
                ).GetString("ratelBinaryPath", "").rstrip("/")
        
        if not ratel_path:
            FreeCAD.Console.PrintError(
                "Please set Ratel binary path in preference and try again"
            )
            return
    
        # Path to Ratel binary
        ratel_binary_path = ratel_path + '/bin/ratel-quasistatic'
        input_file = os.path.join(
            self.directory, "Input" + ".yml")
        
        # Command and arguments
        command = [
            ratel_binary_path,
            '-options_file',
            input_file
        ]
        output_file_name = os.path.join(self.directory, "ratel_output.yml")
        output_file = codecs.open(output_file_name, "w", encoding="utf-8")
        
        # run solver
        self._process = subprocess.Popen(
        command,
        cwd=self.directory,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
        )
        self.signalAbort.add(self._process.terminate)
        while True:
            output = self._process.stdout.readline()
            if output == '' and self._process.poll() is not None:
                break
            if output:
                output_file.write(output.strip())
                output_file.write("\n")
                self.pushStatus(output.strip())
        
        stdout, stderr = self._process.communicate()
        if stdout:
            output_file.write(stdout)
            self.pushStatus(stdout)
        if stderr:
            print(stderr)
            self.pushStatus(stderr)
        output_file.close()
    
        FreeCAD.Console.PrintMessage(
            "Output file:{}\n"
            .format(output_file_name)
        )

        return
       

class Results(run.Results):

    def run(self):
        return

##  @}
