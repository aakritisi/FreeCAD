# ***************************************************************************
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

__title__ = "FreeCAD FEM ratel constraint traction"
__url__ = "https://www.freecad.org"

import FreeCAD

def get_analysis_types():
    return "all"    # write for all analysis types


def get_constraint_title():
    return "Pressure Constraints"


def write_constraint(f, femobjs_pressure, ratel_writer):
    
    
    for femobj_press in femobjs_pressure:
        pressure_obj = femobj_press["Object"]
        pressure_quantity = FreeCAD.Units.Quantity(pressure_obj.Pressure.getValueAs("Pa"))
        face_numbers = []
        for _, sub_elements in pressure_obj.References:
            for sub_element in sub_elements:
                if sub_element.startswith("Face"):
                    face_number = sub_element[4:]
                    face_numbers.append(face_number)
                else:
                    FreeCAD.Console.PrintError("Ratel doesn't support constraints on Vertices or Edges \n")

        if(len(face_numbers) > 0):
            f.write("   pressure: ")
            face_numbers_list = ','.join(face_numbers)
            f.write(face_numbers_list)
            f.write("\n")
            for face_number in face_numbers:
                f.write("   pressure_" + face_number + ": ")
                f.write(str(pressure_quantity))
                f.write("\n")