import glob
import os
import pytest
from pathlib import Path
from typing import Dict, Any

# These will be imported from the schemas repository
from schemas.python.can_frame import CANIDFormat
from schemas.python.json_formatter import format_file
from schemas.python.signals_testing import obd_testrunner

REPO_ROOT = Path(__file__).parent.parent.absolute()

TEST_CASES = [
    # 2015 model year
    {
        "model_year": "2015",
        "signalset": "default.json",
        "tests": [
            # Tire pressures
            ("DA26056122600108A109C10AD10BE", {
                "TLX_TP_FR": 220.5,
                "TLX_TP_FL": 236.0,
                "TLX_TP_RR": 245.5,
                "TLX_TP_RL": 230.0,
            }),
            ("DA26056122600107E108D10A310B1", {
                "TLX_TP_FR": 215.0,
                "TLX_TP_FL": 225.5,
                "TLX_TP_RR": 239.5,
                "TLX_TP_RL": 220.5,
            }),
            
            # ATF Temperature
            ("DB3305612230834F", {
                "TLX_ATF": 39.0,  # (79-40) where 79 is the hex value 4F
            }),
            ("DB3305612230836A", {
                "TLX_ATF": 66.0,  # (106-40) where 106 is the hex value 6A
            }),
            
            # Transmission gear
            ("DB33056122308601", {
                "TLX_GEAR": "D1",
            }),
            ("DB33056122308604", {
                "TLX_GEAR": "D4",
            }),
            ("DB33056122308608", {
                "TLX_GEAR": "D8",
            }),
            ("DB3305612230860E", {
                "TLX_GEAR": "N",
            }),
            ("DB3305612230860F", {
                "TLX_GEAR": "R",
            }),
            ("DB33056122308600", {
                "TLX_GEAR": "P",
            }),
            
            # Active cylinders
            ("DB33056122261506", {
                "TLX_ACTIVE_CYL": 6,
            }),
            ("DB33056122261504", {
                "TLX_ACTIVE_CYL": 4,
            }),
            ("DB33056122261503", {
                "TLX_ACTIVE_CYL": 3,
            }),
            
            # Engine coolant temperature
            ("DB3305610105AF", {
                "TLX_ECT": 85.0,  # (175-40) where 175 is the hex value AF
            }),
            ("DB3305610105C8", {
                "TLX_ECT": 110.0,  # (200-40) where 200 is the hex value C8
            }),
            ("DB330561010578", {
                "TLX_ECT": 40.0,  # (120-40) where 120 is the hex value 78
            }),
        ]
    },
]

def load_signalset(filename: str) -> str:
    """Load a signalset JSON file from the standard location."""
    signalset_path = REPO_ROOT / "signalsets" / "v3" / filename
    with open(signalset_path) as f:
        return f.read()

@pytest.mark.parametrize(
    "test_group",
    TEST_CASES,
    ids=lambda test_case: f"MY{test_case['model_year']}"
)
def test_signals(test_group: Dict[str, Any]):
    """Test signal decoding against known responses."""
    signalset_json = load_signalset(test_group["signalset"])

    # Run each test case in the group
    for response_hex, expected_values in test_group["tests"]:
        try:
            obd_testrunner(
                signalset_json,
                response_hex,
                expected_values,
                can_id_format=CANIDFormat.ELEVEN_BIT
            )
        except Exception as e:
            pytest.fail(
                f"Failed on response {response_hex} "
                f"(Model Year: {test_group['model_year']}, "
                f"Signalset: {test_group['signalset']}): {e}"
            )

def get_json_files():
    """Get all JSON files from the signalsets/v3 directory."""
    signalsets_path = os.path.join(REPO_ROOT, 'signalsets', 'v3')
    json_files = glob.glob(os.path.join(signalsets_path, '*.json'))
    # Convert full paths to relative filenames
    return [os.path.basename(f) for f in json_files]

@pytest.mark.parametrize("test_file",
    get_json_files(),
    ids=lambda x: x.split('.')[0].replace('-', '_')  # Create readable test IDs
)
def test_formatting(test_file):
    """Test signal set formatting for all vehicle models in signalsets/v3/."""
    signalset_path = os.path.join(REPO_ROOT, 'signalsets', 'v3', test_file)

    formatted = format_file(signalset_path)

    with open(signalset_path) as f:
        assert f.read() == formatted

if __name__ == '__main__':
    pytest.main([__file__])
