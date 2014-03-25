# coding: utf-8

import os
import sipconfig
from PyQt4 import pyqtconfig

build_file = "qjuliancalendarwidget.sbf"


config = pyqtconfig.Configuration() 

qt_sip_flags = config.pyqt_sip_flags
# Run SIP to generate the code.  Note that we tell SIP where to find the qt
# module's specification files using the -I flag.
os.system(" ".join([config.sip_bin, "-c", ".", "-b", build_file, "-I", config.pyqt_sip_dir, qt_sip_flags, "qjuliancalendarwidget.sip"]))

installs = []

installs.append(["qjuliancalendarwidget.sip", os.path.join(config.pyqt_sip_dir, "qjuliancalendarwidget")])

installs.append(["qjuliancalendarwidgetconfig.py", config.pyqt_sip_dir])

makefile = pyqtconfig.QtGuiModuleMakefile(
    configuration=config,
    build_file=build_file,
    installs=installs
)

makefile.extra_lib_dirs.append(".")
makefile.extra_libs.append("qjuliancalendarwidget")

makefile.generate()

content = {
    "qjuliancalendarwidget_sip_dir":    config.pyqt_sip_dir,
    "qjuliancalendarwidget_sip_flags":  qt_sip_flags
}

sipconfig.create_config_module("qjuliancalendarwidgetconfig.py", "qjuliancalendarwidgetconfig.py.in", content)
