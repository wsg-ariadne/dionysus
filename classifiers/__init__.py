from .calliope import CalliopeModel
from .janus import JanusModel


CALLIOPE_MODEL = CalliopeModel('classifiers/calliope.pickle', 'classifiers/calliope_reference.csv')
JANUS_MODEL = JanusModel('classifiers/janus')


# Janus results
JANUS_CLASSIFICATIONS = {
    0: 'absent',
    1: 'even',
    2: 'weighted'
}