# ***************************************************************************
# *   Copyright (c) 2019 Bernd Hahnebach <bernd@bimstatik.org>              *
# *   Copyright (c) 2020 Sudhanshu Dubey <sudhanshu.thethunder@gmail.com    *
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

import FreeCAD

import ObjectsFem

import Fem
from . import manager
from .manager import get_meshname
from .boxanalysis_base import setup_boxanalysisbase
from .manager import init_doc


def get_information():
    return {
        "name": "Box Analysis Static",
        "meshtype": "solid",
        "meshelement": "Tet10",
        "constraints": ["fixed", "displacement" "force", "pressure"],
        "solvers": ["ratel"],
        "material": "solid",
        "equations": ["mechanical"]
    }


def get_explanation(header=""):
    return header + """

To run the example from Python console use:
from femexamples.boxanalysis_static import setup
setup()


See forum topic post:
...

"""


def setup(doc=None, solvertype="ratel"):

    # init FreeCAD document
    if doc is None:
        doc = init_doc()

    # explanation object
    # just keep the following line and change text string in get_explanation method
    manager.add_explanation_obj(doc, get_explanation(manager.get_header(get_information())))

    # setup box static, add a fixed, force and a pressure constraint
    geom_obj = doc.addObject("Part::Box", "Box")
    geom_obj.Width = geom_obj.Height = 1000
    geom_obj.Length = 8000
    doc.recompute()


    analysis = ObjectsFem.makeAnalysis(doc, "Analysis")

    # mesh
    from .meshes.mesh_boxanalysis_tetra10 import create_nodes, create_elements
    fem_mesh = Fem.FemMesh()
    control = create_nodes(fem_mesh)
    if not control:
        FreeCAD.Console.PrintError("Error on creating nodes.\n")
    control = create_elements(fem_mesh)
    if not control:
        FreeCAD.Console.PrintError("Error on creating elements.\n")
    femmesh_obj = analysis.addObject(ObjectsFem.makeMeshGmsh(doc, get_meshname()))[0]
    femmesh_obj.FemMesh = fem_mesh
    femmesh_obj.Part = geom_obj
    femmesh_obj.SecondOrderLinear = False
    femmesh_obj.CharacteristicLengthMin = "8.0 mm"
    doc.recompute()

    geom_obj = doc.Box
    analysis = doc.Analysis

    # solver
    
    solver_obj = ObjectsFem.makeSolverRatel(doc, "SolverRatel")
   
    
    # solver_obj.SplitInputWriter = False
    solver_obj.AnalysisType = "static"
    analysis.addObject(solver_obj)

    # constraint fixed
    con_fixed = ObjectsFem.makeConstraintFixed(doc, "FemConstraintFixed")
    con_fixed.References = [(geom_obj, "Face3")]
    analysis.addObject(con_fixed)

    # constraint displacement
    con_disp = ObjectsFem.makeConstraintDisplacement(doc, "ConstraintDisplacement")
    con_disp.References = [(geom_obj, "Face2")]
    con_disp.xFix = False
    con_disp.xDisplacement = 1.0
    con_disp.yFix = False
    con_disp.yDisplacement = 2.0
    con_disp.zFix = False
    con_disp.zDisplacement = 0.0

    analysis.addObject(con_disp)

    # constraint force
    con_force = ObjectsFem.makeConstraintForce(doc, "FemConstraintForce")
    con_force.References = [(geom_obj, "Face6")]
    con_force.Force = "40000.0 N"
    con_force.Direction = (geom_obj, ["Edge2"])
    con_force.Reversed = True
    analysis.addObject(con_force)


    # constraint pressure
    con_pressure = ObjectsFem.makeConstraintPressure(doc, name="FemConstraintPressure")
    con_pressure.References = [(geom_obj, "Face5")]
    con_pressure.Pressure = "1000.0 Pa"
    con_pressure.Reversed = False
    analysis.addObject(con_pressure)

    doc.recompute()
    return doc
