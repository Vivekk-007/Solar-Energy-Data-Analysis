import pandas as pd
import pytest

from streamlit_app.calculations import annual_om, annual_revenue, annualize, capacity_factor, co2_avoided, estimated_energy, net_benefit, payback_years, roi, specific_yield


def test_energy_and_annualization():
    frame = pd.DataFrame({"gti": [1000, 500, None]})
    assert estimated_energy(frame, 100, 0.8).tolist() == [80.0, 40.0, 0.0]
    assert annualize(120, 2) == pytest.approx(21914.999999)


def test_business_calculations():
    assert annual_revenue(1000, 8) == 8000
    assert annual_om(5_000_000, 0.02) == 100_000
    assert net_benefit(8000, 1000) == 7000
    assert payback_years(1_000_000, 100_000) == 10
    assert payback_years(1_000_000, 0) is None
    assert roi(100_000, 1_000_000) == 0.1
    assert co2_avoided(1000, 0.7) == 700
    assert specific_yield(150000, 100) == 1500
    assert capacity_factor(876000, 100) == 1
