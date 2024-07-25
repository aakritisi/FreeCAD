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
    
    str_face_map = [value for key, value in ratel_writer.mesh_object.FaceMapping.items() if key.startswith("ConstraintPressure")]
    face_map = {}

    for str_val in str_face_map:
        str_li = str_val.split(");")[:-1]
        for str_ele in str_li:
            str_li = str_ele.split(", ")
            face_map[(str_li[0])[1:]] = str_li[1]

     
    
    face_numbers = []
    for femobj_press in femobjs_pressure:
        face_set = set()
        pressure_obj = femobj_press["Object"]
        pressure_quantity = FreeCAD.Units.Quantity(pressure_obj.Pressure.getValueAs("Pa"))
        
        for _, sub_elements in pressure_obj.References:
            for sub_element in sub_elements:
                if sub_element.startswith("Face"):
                    face_number = sub_element[4:].strip()
                    face_num = face_map.get(face_number, face_number)
                    face_numbers.append(face_num)
                else:
                    FreeCAD.Console.PrintError("Ratel doesn't support constraints on Vertices or Edges \n")


    if not face_map:
        f.write("   pressure: ")
        f.write(','.join(face_numbers))
        f.write("\n")
    else:
        face_numbers_list = ','.join(list(set(face_map.values())))
        f.write("   pressure: ")
        f.write(face_numbers_list)
        f.write("\n")    

    if(len(face_numbers) > 0):
        for face_number in face_numbers:
            if(face_number not in face_set):
                f.write("   pressure_" + face_number + ": ")
                f.write(str(pressure_quantity))
                f.write("\n")
                face_set.add(face_number)
                

