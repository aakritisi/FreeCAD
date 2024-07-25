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
    return "Traction Constraints"


def write_constraint(f, femobjs_force, ratel_writer):
    from collections import defaultdict

    str_face_map = [value for key, value in ratel_writer.mesh_object.FaceMapping.items() if key.startswith("ConstraintForce")]
    face_map = {}

    for str_val in str_face_map:
        str_li = str_val.split(");")[:-1]
        for str_ele in str_li:
            str_li = str_ele.split(", ")
            face_map[(str_li[0])[1:]] = str_li[1]

    reverse_mapping = defaultdict(list)

    for key, value in face_map.items():
        reverse_mapping[value].append(key)

    common_entities = {value: keys for value, keys in reverse_mapping.items() if len(keys) > 1}

    face_numbers = []
    
    for femobj_force in femobjs_force:
        face_set = set()
        force_obj = femobj_force["Object"]
        direction_vec = force_obj.DirectionVector
        
        load = FreeCAD.Units.Quantity(force_obj.Force.getValueAs("N"))
        

        for ele, sub_elements in force_obj.References:
            area = 0
            for sub_element in sub_elements:
                
                if sub_element.startswith("Face"):
                    face_number = sub_element[4:].strip()
                    face_numbers.append(face_number)
                else:
                    FreeCAD.Console.PrintError("Ratel doesn't support constraints on Vertices or Edges \n")
    if not face_map:
        f.write("   traction: ")
        f.write(','.join(face_numbers))
        f.write("\n")
    else:
        face_numbers_list = ','.join(list(set(face_map.values())))
        f.write("   traction: ")
        f.write(face_numbers_list)
        f.write("\n")    

    if(len(face_numbers) > 0):
        for face_number in face_numbers:
            curr_face =  face_map.get(face_number, face_number)
            if(curr_face not in face_set):

                if(curr_face in common_entities):
                    for face_ele in common_entities[curr_face]:
                        face = ele.Shape.getElement("Face"+face_ele)
                        # convert area from mm^2 to m^2
                        area = area + round(face.Area) / 1e6
                else:
                    face = ele.Shape.getElement("Face"+face_number) 
                        # convert area from mm^2 to m^2
                    area = round(face.Area) / 1e6
                
                f.write("   traction_" + curr_face + ": ")
                tx = direction_vec.x * load/area
                f.write(str(tx) + ",")
                
                ty = direction_vec.y * load/area
                f.write(str(ty) + ",")
                
                tz = direction_vec.z * load/area
                f.write(str(tz))
                
                f.write("\n")
                face_set.add(curr_face)