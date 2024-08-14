# ***************************************************************************
# *   Copyright (c) 2020 Sudhanshu Dubey <sudhanshu.thethunder@gmail.com>   *
# *   Copyright (c) 2021 Bernd Hahnebach <bernd@bimstatik.org>              *
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

import BOPTools.SplitFeatures

import Fem
import ObjectsFem

from . import manager
from .manager import get_meshname
from .manager import init_doc


def get_information():
    return {
        "name": "Ogden",
        "meshtype": "solid",
        "meshelement": "Tet10",
        "constraints": [""],
        "solvers": ["ratel"],
        
    }


def get_explanation(header=""):
    return header + """

To run the example from Python console use:
from femexamples.ogden_ratel_material import setup
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

    # geometric objects
    # name is important because the other method in this module use obj name
    box_obj1 = doc.addObject("Part::Box", "Box1")
    box_obj1.Height = 10
    box_obj1.Width = 10
    box_obj1.Length = 20
    box_obj2 = doc.addObject("Part::Box", "Box2")
    box_obj2.Height = 10
    box_obj2.Width = 10
    box_obj2.Length = 20
    box_obj2.Placement.Base = (20, 0, 0)
    box_obj3 = doc.addObject("Part::Box", "Box3")
    box_obj3.Height = 10
    box_obj3.Width = 10
    box_obj3.Length = 20
    box_obj3.Placement.Base = (40, 0, 0)
    box_obj4 = doc.addObject("Part::Box", "Box4")
    box_obj4.Height = 10
    box_obj4.Width = 10
    box_obj4.Length = 20
    box_obj4.Placement.Base = (60, 0, 0)
    box_obj5 = doc.addObject("Part::Box", "Box5")
    box_obj5.Height = 10
    box_obj5.Width = 10
    box_obj5.Length = 20
    box_obj5.Placement.Base = (80, 0, 0)

    # make a CompSolid out of the boxes, to be able to remesh with GUI
    j = BOPTools.SplitFeatures.makeBooleanFragments(name="BooleanFragments")
    j.Objects = [box_obj1, box_obj2, box_obj3, box_obj4, box_obj5]
    j.Mode = "CompSolid"
    j.Proxy.execute(j)
    j.purgeTouched()
    doc.recompute()
    if FreeCAD.GuiUp:
        for obj in j.ViewObject.Proxy.claimChildren():
            obj.ViewObject.hide()

    geom_obj = doc.addObject("Part::Feature", "CompSolid")
    geom_obj.Shape = j.Shape.CompSolids[0]
    if FreeCAD.GuiUp:
        j.ViewObject.hide()
    doc.recompute()

    

    if FreeCAD.GuiUp:
        geom_obj.ViewObject.Document.activeView().viewAxonometric()
        geom_obj.ViewObject.Document.activeView().fitAll()

    # analysis
    analysis = ObjectsFem.makeAnalysis(doc, "Analysis")

    # solver
    solver_obj = ObjectsFem.makeSolverRatel(doc, "SolverRatel")

    solver_obj.AnalysisType = "static"
    analysis.addObject(solver_obj)
    
    
    # material
    material_obj = ObjectsFem.makeMaterialSolid(doc, "FemMaterial")
    mat = material_obj.Material
    mat["Name"] = "Concrete-Generic"
    mat["Model"] = "elasticity-isochoric-ogden-current"
    mat["YoungsModulus"] = "3.2 MPa"
    mat["PoissonRatio"] = "0.4"
    mat["nu_smoother"] = "0.39"
    mat["PoissonRatio"] = "0.4"
    mat["mu_1"] = "0.5"
    mat["mu_2"] = "0.5"
    mat["m"] = "6.3,0.012,-0.1"
    mat["alpha"] = "1.3,5.0,-2.0"
    # mat["nu_smoother"] = "0.39"
    material_obj.Material = mat
    analysis.addObject(material_obj)

    # mesh
    from .meshes.mesh_multibodybeam_tetra10 import create_nodes, create_elements
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

    doc.recompute()
    return doc
