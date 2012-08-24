"""
A set of preprocessors for the skeinforge engine
"""

from Preprocessor import *
from RpmPreprocessor import *
from RemoveRepGStartEndGcode import *
from errors import *
from .. import Gcode
import contextlib
import os
import tempfile

class Skeinforge50Preprocessor(Preprocessor):
  """
  A Preprocessor that takes a skeinforge 50 file without start/end
  and replaces/removes deprecated commands with their replacements.

  Removals:
    G21
    G90
    M105
    M104

  """

  def __init__(self):
    self.code_map = {
        'G21'     :     self._transform_g21,
        'G90'     :     self._transform_g90,
        'M105'    :     self._transform_m105,
        'M104'    :     self._transform_m104,
        }

  def process_file(self, input_path, output_path):
    """
    Given a filepath, reads each line of that file and, if necessary, 
    transforms it into another format.  If either of these filepaths
    do not lead to .gcode files, we throw a NotGCodeFileError.

    @param input_path: The input file path
    @param output_path: The output file path
    """
    self.inputs_are_gcode(input_path, output_path)
    start_end_gcode_preprocessor = RemoveRepGStartEndGcode()
    with tempfile.NamedTemporaryFile(suffix='.gcode', delete=True) as f:
      removed_start_end = f.name
    start_end_gcode_preprocessor.process_file(input_path, removed_start_end)
    rp = RpmPreprocessor()
    with tempfile.NamedTemporaryFile(suffix='.gcode', delete=True) as f:
      remove_rpm_path = f.name
    rp.process_file(removed_start_end, remove_rpm_path)
    #Open both the files
    with contextlib.nested(open(remove_rpm_path), open(output_path, 'w')) as (i, o):
      #For each line in the input file
      for read_line in i:
        line = self._transform_line(read_line)
        o.write(line)            

  def _transform_line(self, line):
    """Given a line, transforms that line into its correct output

    @param str line: Line to transform
    @return str: Transformed line
    """
    for key in self.code_map:
      if key in line:
        #transform the line
        line = self.code_map[key](line)
        break
    return line

  def _transform_g21(self, input_line):
    """
    Given a line that has an "G21" command, transforms it into
    the proper output.  The s3g gcode parser uses mm positioning by default, 
    so this command is not required.

    @param str input_line: The line to be transformed
    @return str: The transformed line
    """
    codes, flags, comments = Gcode.parse_line(input_line)
    if 'G' in codes and codes['G'] == 21:
      return_line = ''
    else:
      return_line = input_line
    return return_line

  def _transform_g90(self, input_line):
    """
    Given a line that has an "G90" command, transforms it into
    the proper output. The s3g gcode parser uses absolute positioning by default.

    @param str input_line: The line to be transformed
    @return str: The transformed line
    """
    codes, flags, comments = Gcode.parse_line(input_line)
    if 'G' in codes and codes['G'] == 90:
      return_line = ''
    else:
      return_line = input_line
    return return_line

  def _transform_m104(self, input_line):
    """
    Given a line that has an "M104" command, transforms it into 
    the proper output.  Skeinforge-50 has a tendency to output
    M104 commands at the end of a print to cool down the extruder.
    However, it tends to omit the obligatory T code required by s3g's
    Gcode parser.  So, we totally remove this line if there is no T 
    code, and keep this line if there is a T code.

    @param str input_line: The line to be transformed
    @return str: The transformed line
    """
    codes, flags, comments = Gcode.parse_line(input_line)
    if 'M' not in codes or codes['M'] != 104:
      return_line = input_line
    elif 'T' in codes:
      return_line = input_line
    else:
      return_line = ''
    return return_line      

  def _transform_m105(self, input_line):
    """
    Given a line that has an "M105" command, transforms it into
    the proper output.

    @param str input_line: The line to be transformed
    @return str: The transformed line
    """
    codes, flags, comments = Gcode.parse_line(input_line)
    if 'M' in codes and codes['M'] == 105:
      return_line = ''
    else:
      return_line = input_line
    return return_line
