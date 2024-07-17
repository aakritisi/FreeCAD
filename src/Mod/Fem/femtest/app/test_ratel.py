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

__title__ = "Ratel FEM unit tests"
__url__ = "https://www.freecad.org"

import unittest
from os.path import join

import FreeCAD

import femsolver.run
from . import support_utils as testtools
from .support_utils import fcc_print
from .support_utils import get_namefromdef


class TestRatel(unittest.TestCase):
    fcc_print("import TestRatel")

    # ********************************************************************************************
    def setUp(self):
        # setUp is executed before every test

        # new document
        self.document = FreeCAD.newDocument(self.__class__.__name__)

        # directory pre face in name
        self.pre_dir_name = "ratel_"

        # more inits
        self.mesh_name = "Mesh"
        self.test_file_dir = join(
            testtools.get_fem_test_home_dir(),
            "ratel",
        )

    # ********************************************************************************************
    def tearDown(self):
        # tearDown is executed after every test
        FreeCAD.closeDocument(self.document.Name)

    # ********************************************************************************************
    def test_00print(self):
        # since method name starts with 00 this will be run first
        # this test just prints a line with stars

        fcc_print(
            "\n{0}\n{1} run FEM TestRatel tests {2}\n{0}".format(
                100 * "*", 10 * "*", 62 * "*"
            )
        )

    # ********************************************************************************************
    def test_box_static(self):
        # set up
        from femexamples.boxanalysis_static_ratel import setup

        setup(self.document, "ratel")
        base_name = get_namefromdef("test_")
        analysis_dir = testtools.get_fem_test_tmp_dir(self.pre_dir_name + base_name)

        # test input file writing
        fea = self.input_file_writing_test(
            base_name,
            analysis_dir=analysis_dir,
            test_end=True,
        )

    def input_file_writing_test(
        self,
        base_name,
        analysis_dir=None,
        test_end=False,
    ):
        fcc_print(
            "\n--------------- "
            "Start of FEM ratel {} test"
            "---------------".format(base_name)
        )

        if analysis_dir is None:
            analysis_dir = testtools.get_fem_test_tmp_dir(self.pre_dir_name + base_name)
        analysis = self.document.Analysis
        machine_ratel = self.document.SolverRatel.Proxy.createMachine(
            self.document.SolverRatel,
            analysis_dir,
            True
        )
        machine_ratel.target = femsolver.run.PREPARE
        error = machine_ratel.start()
        machine_ratel.join()

        inpfile_given = join(self.test_file_dir, (base_name + ".yml"))
        inpfile_totest = join(analysis_dir, (self.mesh_name + ".yml"))
        fcc_print("Checking FEM inp file write...")
        fcc_print("Writing {} for {}".format(inpfile_totest, base_name))
        self.assertFalse(error, "Writing failed")

        fcc_print("Comparing {} to {}".format(inpfile_given, inpfile_totest))
        ret = testtools.compare_inp_files(inpfile_given, inpfile_totest)
        self.assertFalse(ret, "ratel writing input test failed.\n{}".format(ret))
