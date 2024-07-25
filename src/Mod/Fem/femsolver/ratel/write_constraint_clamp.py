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

__title__ = "FreeCAD FEM ratel constraint clamp"
__url__ = "https://www.freecad.org"

import FreeCAD

def get_analysis_types():
    return "all"    # write for all analysis types


def get_constraint_title():
    return "Clamp Constraints"


def write_constraint(f, femobjs_fixed, femobjs_displacement, ratel_writer):

    str_face_map_fixed = [value for key, value in ratel_writer.mesh_object.FaceMapping.items() if key.startswith("ConstraintFixed")]
    face_map_fixed = {}

    for str_fixed in str_face_map_fixed:
        str_fixed_li = str_fixed.split(");")[:-1]
        for str_fixed_ele in str_fixed_li:
            str_li = str_fixed_ele.split(", ")
            face_map_fixed[(str_li[0])[1:]] = str_li[1]

    
    str_face_map_disp = [value for key, value in ratel_writer.mesh_object.FaceMapping.items() if key.startswith("ConstraintDisplacement")]
    face_map_disp = {}

    for str_disp in str_face_map_disp:
        str_disp_li = str_disp.split(");")[:-1]
        for str_disp_ele in str_disp_li:
            str_li = str_disp_ele.split(", ")
            face_map_disp[(str_li[0])[1:]] = str_li[1]

    face_numbers= []
    for femobj_fixed in femobjs_fixed:
        for _, sub_elements_fixed in femobj_fixed["Object"].References:
            for sub_element_fixed in sub_elements_fixed:
                if sub_element_fixed.startswith("Face"):
                    face_number = sub_element_fixed[4:].strip()
                    face_num = face_map_fixed.get(face_number, face_number)
                    face_numbers.append(face_num)
                else:
                    FreeCAD.Console.PrintError("Ratel doesn't support constraints on Vertices or Edges \n")

                    

    for femobj_displ in femobjs_displacement:
        for _, sub_elements_displ in femobj_displ["Object"].References:
            for sub_element_displ in sub_elements_displ:
                if sub_element_displ.startswith("Face"):
                    face_number = sub_element_displ[4:].strip()
                    face_num = face_map_disp.get(face_number, face_number)
                    face_numbers.append(face_num)
                else:
                    FreeCAD.Console.PrintError("Ratel doesn't support constraints on Vertices or Edges \n")


    if(len(face_numbers) >0):
    
        f.write("   clamp: ")
        
        face_numbers_list = ','.join(list(set(face_numbers)))
        f.write(face_numbers_list)
        f.write("\n")

        
        for femobj_displ in femobjs_displacement:
            face_set = set()
            displ_obj = femobj_displ["Object"]
            face_numbers = []
            for _, sub_elements_displ in displ_obj.References:
                for sub_element_displ in sub_elements_displ:
                    if sub_element_displ.startswith("Face"):
                        face_number = sub_element_displ[4:]
                        face_num = face_map_disp.get(face_number, face_number)
                        face_numbers.append(face_num)
            for face_number in face_numbers:
                if(face_number not in face_set):
                    f.write("   clamp_" + face_number + "_translate: ")
                    f.write(str(FreeCAD.Units.Quantity(displ_obj.xDisplacement.getValueAs("m"))))
                    f.write(",")
                    f.write(str(FreeCAD.Units.Quantity(displ_obj.yDisplacement.getValueAs("m"))))
                    f.write(",")
                    f.write(str(FreeCAD.Units.Quantity(displ_obj.zDisplacement.getValueAs("m"))))
                    f.write("\n")
                    if ratel_writer.member.geos_beamsection or ratel_writer.member.geos_shellthickness:
                        if displ_obj.xRotation != 0 or displ_obj.yRotation != 0 or displ_obj.zRotation != 0:
                            f.write("   clamp_" + face_number + "_rotate: ")
                            f.write(str(FreeCAD.Units.Quantity(displ_obj.xRotation.getValueAs("deg"))))
                            f.write(",")
                            f.write(str(FreeCAD.Units.Quantity(displ_obj.yRotation.getValueAs("deg"))))
                            f.write(",")
                            f.write(str(FreeCAD.Units.Quantity(displ_obj.zRotation.getValueAs("deg"))))
                            f.write(",0,0")
                            f.write("\n")
                    face_set.add(face_number)