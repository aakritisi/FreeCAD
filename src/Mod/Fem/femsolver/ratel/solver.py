# ***************************************************************************
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

__title__ = "FreeCAD FEM solver object Ratel"
__url__ = "https://www.freecad.org"

## @package SolverCalculix
#  \ingroup FEM

import glob
import os

import FreeCAD

from .. import solverbase
from . import writer
from . import tasks
from femtools import femutils
from femtools import membertools
from femmesh import meshsetsgetter
from .. import run

if FreeCAD.GuiUp:
    import FemGui

ANALYSIS_TYPES = ["static", "frequency", "thermomech", "check", "buckling"]
MESH_FORMAT = [".msh"]


def create(doc, name="SolverRatel"):
    return femutils.createObject(
        doc, name, Proxy, ViewProxy)


class _BaseSolverRatel:

    def on_restore_of_document(self, obj):
        temp_analysis_type = obj.AnalysisType
        obj.AnalysisType = ANALYSIS_TYPES
        if temp_analysis_type in ANALYSIS_TYPES:
            obj.AnalysisType = temp_analysis_type
        else:
            FreeCAD.Console.PrintWarning(
                "Analysis type {} not found. Standard is used.\n"
                .format(temp_analysis_type)
            )
            obj.AnalysisType = ANALYSIS_TYPES[0]
        
        self.add_attributes(obj)


    def add_attributes(self, obj):
        if not hasattr(obj, "AnalysisType"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "AnalysisType",
                "Fem",
                "Type of the analysis"
            )
            obj.AnalysisType = ANALYSIS_TYPES
            obj.AnalysisType = ANALYSIS_TYPES[0]

        if not hasattr(obj, "MeshFormat"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "MeshFormat",
                "Fem",
                "Format for generating mesh"
            )
        obj.MeshFormat = MESH_FORMAT
        obj.MeshFormat = MESH_FORMAT[0]
        


class Proxy(solverbase.Proxy, _BaseSolverRatel):
    """The Fem::FemSolver's Proxy python type, add solver specific properties
    """

    Type = "Fem::SolverRatel"

    def __init__(self, obj):
        super(Proxy, self).__init__(obj)
        obj.Proxy = self
        self.add_attributes(obj)
        

    def onDocumentRestored(self, obj):
        self.on_restore_of_document(obj)

    def createMachine(self, obj, directory, testmode=False):
        return run.Machine(
            solver=obj, directory=directory,
            check=tasks.Check(),
            prepare=tasks.Prepare(),
            solve=tasks.Solve(),
            results=tasks.Results(),
            testmode=testmode)

    def editSupported(self):
        return True

    def edit(self, directory):
        pattern = os.path.join(directory, "*.yml")
        FreeCAD.Console.PrintMessage("{}\n".format(pattern))
        f = glob.glob(pattern)[0]
        FemGui.open(f)

    def execute(self, obj):
        return


class ViewProxy(solverbase.ViewProxy):
    pass


