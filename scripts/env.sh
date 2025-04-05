
export CO2_METER_ROOT=$(realpath $(dirname "${BASH_SOURCE[0]:-$0}/.."))
source $CO2_METER_ROOT/venv/bin/activate
export PYTHONPATH=$CO2_METER_ROOT/src:$PYTHONPATH