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

__title__ = "FreeCAD FEM solver CalculiX tasks"
__author__ = "Markus Hovorka, Bernd Hahnebach"
__url__ = "https://www.freecad.org"

## \addtogroup FEM
#  @{

import os
import os.path
import subprocess

import FreeCAD

from . import writer
from .. import run
from .. import settings
from feminout import importCcxDatResults
from feminout import importCcxFrdResults
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
        # self.pushStatus("Executing solver...\n")

        # # get solver binary
        # self.pushStatus("Get solver binary...\n")
        # binary = settings.get_binary("Ratel")
        # if binary is None:
        #     self.pushStatus("Error: The Ratel binary has not been found!")
        #     self.fail()
        #     return

        # # run solver
        # self._process = subprocess.Popen(
        #     [binary, "-i", _inputFileName],
        #     cwd=self.directory,
        #     stdout=subprocess.PIPE,
        #     stderr=subprocess.PIPE
        # )
        # self.signalAbort.add(self._process.terminate)
        
        # self._process.communicate()
        # self.signalAbort.remove(self._process.terminate)
        return
       

class Results(run.Results):

    def run(self):
        return

##  @}
