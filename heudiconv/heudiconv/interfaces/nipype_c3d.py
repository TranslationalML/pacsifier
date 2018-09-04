import os
import sys
import subprocess

from nipype.interfaces.base import traits, Directory, File, CommandLineInputSpec, TraitedSpec, CommandLine, BaseInterfaceInputSpec, BaseInterface
from nipype.pipeline.engine import Node

class Convert3DInputSpec(CommandLineInputSpec):
    in_file = File(mandatory=True, exists=True, argstr="%s", desc='Input image (Dicom)')
    out_file = File(mandatory=True, argstr="-o %s", desc='Converted image (Nifti)')

class Convert3DOutputSpec(TraitedSpec):
    out_file = File(exists=True, desc='Converted image (Nifti)')

class Convert3D(CommandLine):
    input_spec = Convert3DInputSpec
    output_spec = Convert3DOutputSpec
    _cmd = 'c3d'

    def _list_outputs(self):
        outputs = self.output_spec().get()
        outputs['out_file'] = os.path.abspath(self.inputs.out_file)
        return outputs

class Convert3DSeriesInputSpec(BaseInterfaceInputSpec):
    dicom_series_dir = Directory(mandatory=True, exists=True, argstr="%s", desc='Input image (Dicom)')
    out_file = File(mandatory=True, argstr="-o %s", desc='Converted image absolute path (Nifti)')

class Convert3DSeriesOutputSpec(TraitedSpec):
    out_file = File(exists=True, desc='Converted image absolute path (Nifti)')

class Convert3DSeries(BaseInterface):
    input_spec = Convert3DSeriesInputSpec
    output_spec = Convert3DSeriesOutputSpec

    def _run_interface(self, runtime):

        # grab series ID - subprocess.run passed a list takes care of escaping and quoting correctly if dicom_series_dir
        # has weird chars like spaces
        c3d_cmd_1 = "c3d -dicom-series-list %s" % (self.inputs.dicom_series_dir)
        
        process = subprocess.Popen(c3d_cmd_1, shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
        proc_stdout = process.communicate()[0].strip()
        # print(proc_stdout)

        # TODO improve error handling for non-zero return codes
        # hack to check the return code
        # e.g. with dicom_series_dir='~/temp/Popp_new_missing3/unpacked/442591_unpack/' we get error print but returncode
        # is 0 and stderr is empty
        #if c3d_cmd_1_out.stdout == b'SeriesNumber\tDimensions\tNumImages\tSeriesDescription\tSeriesID\n':
        #    raise RuntimeError("convert_dicom_series_to_nifti_c3d: Could not find dicom series ID from"
        #                       "{}".format(dicom_series_dir))

        c3d_cmd_1_out_split = proc_stdout.decode("utf-8").split("\t")
        dicom_series_id = c3d_cmd_1_out_split[-1].strip()

        # convert to NIFTI
        c3d_cmd_2 = ['c3d', '-dicom-series-read', self.inputs.dicom_series_dir, dicom_series_id,
                     '-o', self.inputs.out_file]
        
        c3d_cmd_2_out = subprocess.call(c3d_cmd_2, stdout=subprocess.PIPE)

        return runtime

    def _list_outputs(self):
        outputs = self._outputs().get()
        outputs['out_file'] = os.path.abspath(self.inputs.out_file)
        return outputs

    def _list_outputs(self):
        outputs = self.output_spec().get()
        outputs['out_file'] = os.path.abspath(self.inputs.out_file)
        return outputs

if __name__ == '__main__':

    if sys.argv[1] == "simple":
        converter =  Node(interface=Convert3D(),name="c3d_converter")
        converter.inputs.in_file = sys.argv[2]
        converter.inputs.out_file = sys.argv[3]
        # Execute the node
        converter.run()
    elif sys.argv[1] == "series":
        converter_dicom_series =  Node(interface=Convert3DSeries(),name="c3d_series_converter")
        converter_dicom_series.inputs.dicom_series_dir = sys.argv[2]
        converter_dicom_series.inputs.out_file = sys.argv[3]
        # Execute the node
        converter_dicom_series.run()
