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

__title__ = "FreeCAD FEM ratel write inpfile materials"
__url__ = "https://www.freecad.org"


import FreeCAD


def write_femelement_material(f, ratel_writer):

    for femobj in ratel_writer.member.mats_linear:
        # femobj --> dict, FreeCAD document object is femobj["Object"]

        mat_obj = femobj["Object"]
        

        if "Model" not in  mat_obj.Material:
            FreeCAD.Console.PrintError(
                "Model name required for material "
            )
            ratel_writer.femelement_count_test = False
            return
        
        model_li = mat_obj.Material["Model"].split("-")
        model = ""

        if "ogden" in model_li:
            model = "ogden"
        elif "hookean" in model_li:
            model = "neo-hookean"
        elif "rivlin" in model_li:
            model = "mooney-rivlin"
        elif "plasticity" in model_li:
            model = "linear-plasticity"
        else:
            model = "elasticity"

        print(
                model
            )
        
        YM = FreeCAD.Units.Quantity(mat_obj.Material["YoungsModulus"])
        YM_in_Pa = YM.getValueAs("Pa").Value
        PR = float(mat_obj.Material["PoissonRatio"])
       
        
        if "nu_smoother" in mat_obj.Material:
            nu_smoother = FreeCAD.Units.Quantity(mat_obj.Material["nu_smoother"])
            if nu_smoother < 0.5:
                f.write("nu_smoother: ")
                f.write(str(nu_smoother))
                f.write("\n")
            else:
                FreeCAD.Console.PrintError(
                    "nu_smoother value should be < 0.5 "
                )
                ratel_writer.femelement_count_test = False
                return 
        elif model == "neo-hookean" or model == "mooney-rivlin" or model == "ogden":
                FreeCAD.Console.PrintError(
                "nu_smoother value missing for material "
            )
                ratel_writer.femelement_count_test = False
                return
        
       
        
        
        if "mu_1" in mat_obj.Material:
            mu_1 = FreeCAD.Units.Quantity(mat_obj.Material["mu_1"])
            if mu_1 >0:
                f.write("mu_1: ")
                f.write(str(mu_1))
                f.write("\n")
            else:
                FreeCAD.Console.PrintError(
                    "mu_1 value should be > 0 "
                )
                ratel_writer.femelement_count_test = False
                return 
        elif model == "mooney-rivlin":
            FreeCAD.Console.PrintError(
                    "mu_1 value value missing for material "
                )
            ratel_writer.femelement_count_test = False
            return 
            
        if "mu_2" in mat_obj.Material:
            mu_2 = FreeCAD.Units.Quantity(mat_obj.Material["mu_2"])
            if mu_2 >0:
                f.write("mu_2: ")
                f.write(str(mu_2))
                f.write("\n")
            else:
                FreeCAD.Console.PrintError(
                    "mu_2 value should be > 0 "
                )
                ratel_writer.femelement_count_test = False
                return 
        elif model == "mooney-rivlin":
            FreeCAD.Console.PrintError(
                    "mu_2 value missing for material "
                )
            ratel_writer.femelement_count_test = False
            return 
            
        
        
        
        if "alpha" in mat_obj.Material:
            alpha = mat_obj.Material["alpha"]
            f.write("alpha: ")
            f.write(str(alpha))
            f.write("\n")
        elif model == "ogden":
            FreeCAD.Console.PrintError(
                    "alpha values missing for material "
                )
            ratel_writer.femelement_count_test = False
            return 
        
        if "m" in mat_obj.Material:
            m = mat_obj.Material["m"]
            f.write("m: ")
            f.write(str(m))
            f.write("\n")
        elif model == "ogden":
            FreeCAD.Console.PrintError(
                    "m ogden material constant values missing for material "
                )
            ratel_writer.femelement_count_test = False
            return

        
        
        if "yield_stress" in mat_obj.Material:
            yield_stress = FreeCAD.Units.Quantity(mat_obj.Material["yield_stress"])
            if yield_stress >0:
                f.write("yield_stress: ")
                f.write(str(yield_stress))
                f.write("\n")
            else:
                FreeCAD.Console.PrintError(
                    "Yield stress value should be > 0 "
                )
                ratel_writer.femelement_count_test = False
                return
        elif model == "linear-plasticity":
            FreeCAD.Console.PrintError(
                    "yield_stress value missing for material "
                )
            ratel_writer.femelement_count_test = False
            return 
            
        if "hardening_A" in mat_obj.Material:
            hardening_A = FreeCAD.Units.Quantity(mat_obj.Material["hardening_A"])
            if hardening_A >0:
                f.write("hardening_A: ")
                f.write(str(hardening_A))
                f.write("\n")
            else:
                FreeCAD.Console.PrintError(
                    "Isotropic hardening value should be > 0 "
                )
                ratel_writer.femelement_count_test = False
                return
        elif model == "linear-plasticity":
            FreeCAD.Console.PrintError(
                    "hardening_A value missing for material "
                )
            ratel_writer.femelement_count_test = False
            return

    
        if "use_AT1" in mat_obj.Material:
            use_AT1 = mat_obj.Material["use_AT1"]
            f.write("use_AT1: ")
            f.write(str(use_AT1))
            f.write("\n")

        if "use_hybrid" in mat_obj.Material:
            use_hybrid = mat_obj.Material["use_hybrid"]
            f.write("use_hybrid: ")
            f.write(str(use_hybrid))
            f.write("\n")

        if "use_offdiagonal" in mat_obj.Material:
            use_offdiagonal = mat_obj.Material["use_offdiagonal"]
            f.write("use_offdiagonal: ")
            f.write(str(use_offdiagonal))
            f.write("\n")


        
        if "fracture_toughness" in mat_obj.Material:
            fracture_toughness = FreeCAD.Units.Quantity(mat_obj.Material["fracture_toughness"])
            if fracture_toughness >0:
                f.write("fracture_toughness: ")
                f.write(str(fracture_toughness))
                f.write("\n")
            else:
                FreeCAD.Console.PrintError(
                    "Fracture toughness value should be > 0 "
                )
                ratel_writer.femelement_count_test = False
                return
        elif model == "elasticity":
            FreeCAD.Console.PrintError(
                    "fracture_toughness value missing for material "
                )
            ratel_writer.femelement_count_test = False
            return 
        
        if "characteristic_length" in mat_obj.Material:
            characteristic_length = FreeCAD.Units.Quantity(mat_obj.Material["characteristic_length"])
            if characteristic_length >0:
                f.write("characteristic_length: ")
                f.write(str(characteristic_length))
                f.write("\n")
            else:
                FreeCAD.Console.PrintError(
                    "Characteristic_length value should be > 0 "
                )
                ratel_writer.femelement_count_test = False
                return
            
        elif model == "elasticity":
            FreeCAD.Console.PrintError(
                    "Characteristic_length value missing for material "
                )
            ratel_writer.femelement_count_test = False
            return 
        
        if "residual_stiffness" in mat_obj.Material:
            residual_stiffness = FreeCAD.Units.Quantity(mat_obj.Material["residual_stiffness"])
            if residual_stiffness >0:
                f.write("residual_stiffness: ")
                f.write(str(residual_stiffness))
                f.write("\n")
            else:
                FreeCAD.Console.PrintError(
                    "Residual stiffness value should be > 0 "
                )
                ratel_writer.femelement_count_test = False
                return
        elif model == "elasticity":
            FreeCAD.Console.PrintError(
                    "residual_stiffness value missing for material "
                )
            ratel_writer.femelement_count_test = False
            return 
        
        if "damage_viscosity" in mat_obj.Material:
            damage_viscosity = FreeCAD.Units.Quantity(mat_obj.Material["damage_viscosity"])
            if damage_viscosity >0:
                f.write("damage_viscosity: ")
                f.write(str(damage_viscosity))
                f.write("\n")
            else:
                FreeCAD.Console.PrintError(
                    "Damage viscosity value should be > 0 "
                )
                ratel_writer.femelement_count_test = False
                return
        elif model == "elasticity":
            FreeCAD.Console.PrintError(
                    "damage_viscosity value missing for material "
                )
            ratel_writer.femelement_count_test = False
            return 

        if YM_in_Pa > 0:
            f.write("E: ")
            f.write(str(YM_in_Pa))
            f.write("\n")
        else:
            FreeCAD.Console.PrintError(
                "Youngs modulus value should be > 0 "
            )
            ratel_writer.femelement_count_test = False
            return

        

        if PR < 0.5:
            f.write("nu: ")
            f.write(str(PR))
            f.write("\n")
        else:
            FreeCAD.Console.PrintError(
                "Poisson ratio value should be < 0.5 "
            )
            ratel_writer.femelement_count_test = False
            return
        
        