import os
import sys
lib_path = os.path.abspath('../')
sys.path.append(lib_path)

try:
    import unittest2 as unittest
except ImportError:
    import unittest
import mock

import tempfile

import makerbot_driver
import warnings

class SingleHeadReading(unittest.TestCase):

  def setUp(self):
    self.p = makerbot_driver.Gcode.GcodeParser()
    self.s = makerbot_driver.Gcode.GcodeStates()
    self.s.values['build_name'] = 'test'
    self.profile = makerbot_driver.Profile('ReplicatorSingle')
    self.s.profile = self.profile
    self.p.state = self.s
    self.s3g= makerbot_driver.s3g()
    with tempfile.NamedTemporaryFile(suffix='.gcode', delete=False) as input_file:
      pass
    input_path = input_file.name
    os.unlink(input_path)
    self.writer = makerbot_driver.Writer.FileWriter(open(input_path, 'wb'))
    self.s3g.writer = self.writer
    self.p.s3g = self.s3g

  def tearDown(self):
    self.profile = None
    self.s = None
    self.writer = None
    self.s3g = None
    self.p = None

  def test_single_head_slicer(self):
    the_file = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        '..',
        'doc',
        'gcode_samples',
        'slic3r_single_extrusion_20mm_box.gcode'
        )
    the_file = preprocess_file_with_prepro(the_file, 'SlicerPreprocessor')
    execute_file(the_file, self.p)

  def test_single_head_skeinforge_single_20mm_box(self):
    the_file = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 
        '..',
        'doc', 
        'gcode_samples', 
        'skeinforge_single_extrusion_20mm_box.gcode'
        )
    the_file = preprocess_file_with_prepro(the_file, 'Skeinforge50Preprocessor')
    execute_file(the_file, self.p) 

  def test_single_head_skeinforge_single_snake(self):
    the_file = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 
        '..',
        'doc', 
        'gcode_samples', 
        'skeinforge_single_extrusion_snake.gcode'
        )
    the_file = preprocess_file_with_prepro(the_file, 'Skeinforge50Preprocessor')
    execute_file(the_file, self.p) 

  def test_single_head_miracle_grue(self):
    the_file = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 
        '..',
        'doc', 
        'gcode_samples', 
        'miracle_grue_single_extrusion_20_mm_box.gcode'
        )
    execute_file(the_file, self.p) 

class DualHeadReading(unittest.TestCase):

  def setUp(self):
    self.p = makerbot_driver.Gcode.GcodeParser()
    self.s = makerbot_driver.Gcode.GcodeStates()
    self.s.values['build_name'] = 'test'
    self.profile = makerbot_driver.Profile('ReplicatorDual')
    self.s.profile = self.profile
    self.p.state = self.s
    self.s3g = makerbot_driver.s3g()
    with tempfile.NamedTemporaryFile(suffix='.gcode', delete=False) as input_file:
      pass
    input_path = input_file.name
    os.unlink(input_path)
    self.writer = makerbot_driver.Writer.FileWriter(open(input_path, 'wb'))
    self.s3g.writer = self.writer
    self.p.s3g = self.s3g

  def tearDown(self):
    self.profile = None
    self.s = None
    self.writer = None
    self.s3g = None
    self.p = None

  def test_dual_head_skeinforge_hilbert_cube(self):
    the_file = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 
        '..',
        'doc', 
        'gcode_samples', 
        'skeinforge_dual_extrusion_hilbert_cube.gcode')
    the_file = preprocess_file_with_prepro(the_file, 'Skeinforge50Preprocessor')
    the_file = preprocess_file_with_prepro(the_file, 'CoordinateRemovalPreprocessor')
    execute_file(the_file, self.p) 

  def test_single_head_skeinforge_single_20mm_box(self):
    the_file = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 
        '..',
        'doc', 
        'gcode_samples', 
        'skeinforge_single_extrusion_20mm_box.gcode'
        )
    the_file = preprocess_file_with_prepro(the_file, 'Skeinforge50Preprocessor')
    execute_file(the_file, self.p) 

  def test_single_head_skeinforge_single_snake(self):
    the_file = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 
        '..',
        'doc', 
        'gcode_samples', 
        'skeinforge_single_extrusion_snake.gcode')
    the_file = preprocess_file_with_prepro(the_file, 'Skeinforge50Preprocessor')
    execute_file(the_file, self.p) 

  def test_single_head_miracle_grue(self):
    the_file = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        '..',
        'doc',
        'gcode_samples',
        'miracle_grue_single_extrusion_20_mm_box.gcode',
        )
    execute_file(the_file,self.p) 

def preprocess_file_with_prepro(the_file, prepro):
  factory = makerbot_driver.Preprocessors.PreprocessorFactory()
  prepro = factory.create_preprocessor_from_name(prepro)
  with tempfile.NamedTemporaryFile(delete=True, suffix='.gcode') as f:
    processed_file_path = f.name
  prepro.process_file(the_file, processed_file_path)
  return processed_file_path

def execute_file(the_file, parser):
  ga = makerbot_driver.GcodeAssembler(parser.state.profile)
  start, end, variables = ga.assemble_recipe()
  start_gcode = ga.assemble_start_sequence(start)
  end_gcode = ga.assemble_end_sequence(end)
  parser.environment.update(variables)
  for line in start_gcode:
    parser.execute_line(line)
  with open(the_file) as f:
    for line in f:
      parser.execute_line(line)
  for line in end_gcode:
    parser.execute_line(line)

if __name__ == '__main__':
  unittest.main()
