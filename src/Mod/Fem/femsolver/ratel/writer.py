# ***************************************************************************
# *   Copyright (c) 2015 Przemo Firszt <przemo@firszt.eu>                   *
# *   Copyright (c) 2015 Bernd Hahnebach <bernd@bimstatik.org>              *
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

__title__ = "FreeCAD FEM solver Ratel writer"
__url__ = "https://www.freecad.org"

## \addtogroup FEM
#  @{

import time
from os.path import join

import FreeCAD
import codecs
from FreeCAD import Units



from . import write_constraint_clamp as con_clamp
from . import write_constraint_traction as con_traction
from . import write_constraint_pressure as con_pressure
from .. import writerbase
from femtools import constants

class FemInputWriterRatel(writerbase.FemInputWriter):
    def __init__(
        self,
        analysis_obj,
        solver_obj,
        mesh_obj,
        member,
        dir_name=None,
        mat_geo_sets=None
    ):
        writerbase.FemInputWriter.__init__(
            self,
            analysis_obj,
            solver_obj,
            mesh_obj,
            member,
            dir_name,
            mat_geo_sets
        )
        self.mesh_name = self.mesh_object.Name
        self.file_name = join(self.dir_name, self.mesh_name + ".yml")

    # ********************************************************************************************
    # write Ratel input
    def write_solver_input(self):

        time_start = time.process_time()
        FreeCAD.Console.PrintMessage("\n")  # because of time print in separate line
        FreeCAD.Console.PrintMessage("Ratel solver input writing...\n")
        FreeCAD.Console.PrintMessage(
            "Input file:{}\n"
            .format(self.file_name)
        )
        
        inpfile = codecs.open(self.file_name, "w", encoding="utf-8")

        inpfile.write("bc:\n")

        self.write_constraints_propdata_clamp(inpfile, self.member.cons_fixed, self.member.cons_displacement, con_clamp)
        self.write_constraints_propdata(inpfile, self.member.cons_force, con_traction)
        self.write_constraints_propdata(inpfile, self.member.cons_pressure, con_pressure)
       
        inpfile.close()

        writetime = round((time.process_time() - time_start), 3)
        FreeCAD.Console.PrintMessage(
            "Writing time Ratel input file: {} seconds.\n".format(writetime)
        )

        # return
        if self.femelement_count_test is True:
            return self.file_name
        else:
            FreeCAD.Console.PrintError(
                "Problems on writing input file, check report prints.\n\n"
            )
            return ""

    
    def write_constraints_propdata_clamp(
        self,
        f,
        femobjs_fixed,
        femobjs_displacement,
        con_module
    ):

        if (not femobjs_fixed) and (not femobjs_displacement):
            return

        analysis_types = con_module.get_analysis_types()
        if analysis_types != "all" and self.analysis_type not in analysis_types:
            return
        con_module.write_constraint(f, femobjs_fixed, femobjs_displacement, self)

    def write_constraints_propdata(
        self,
        f,
        femobjs_con,
        con_module
    ):
        
        if (not femobjs_con):
            return

        analysis_types = con_module.get_analysis_types()
        if analysis_types != "all" and self.analysis_type not in analysis_types:
            return
        con_module.write_constraint(f, femobjs_con, self)


##  @}
