"""
Tests for the build_features.py weather processing logic.
"""
import sys
import os
import pytest

# Adjust path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.training.build_features import (
    parse_percentage,
    calculate_tertile_means,
    parse_float
)


class TestParsePercentage:
    """Tests for parse_percentage helper."""

    def test_parse_percentage_normal(self):
        assert parse_percentage("50.00%") == pytest.approx(0.50, rel=1e-3)

    def test_parse_percentage_small(self):
        assert parse_percentage("0.03%") == pytest.approx(0.0003, rel=1e-3)

    def test_parse_percentage_full(self):
        assert parse_percentage("100%") == pytest.approx(1.0, rel=1e-3)

    def test_parse_percentage_empty(self):
        assert parse_percentage("") == 0.0

    def test_parse_percentage_invalid(self):
        assert parse_percentage("not_a_number") == 0.0


class TestCalculateTertileMeans:
    """Tests for tertile mean calculation."""

    def test_tertile_simple(self):
        values = [10, 20, 30, 40, 50, 60, 70, 80, 90]
        low, mid, high = calculate_tertile_means(values)
        # Low = avg(10,20,30), Mid = avg(40,50,60), High = avg(70,80,90)
        assert low == pytest.approx(20.0, rel=1e-3)
        assert mid == pytest.approx(50.0, rel=1e-3)
        assert high == pytest.approx(80.0, rel=1e-3)

    def test_tertile_empty(self):
        low, mid, high = calculate_tertile_means([])
        assert low == 0
        assert mid == 0
        assert high == 0


class TestRegionalProfilesIntegration:
    """Integration tests for regional profiles data after pipeline run."""

    @pytest.fixture
    def regional_profiles(self):
        """Load the generated regional profiles."""
        import csv
        path = os.path.join(
            os.path.dirname(__file__), 
            '../data/processed/regional_profiles.csv'
        )
        if not os.path.exists(path):
            pytest.skip("regional_profiles.csv not found - run build_features first")
        
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)

    def test_profiles_not_empty(self, regional_profiles):
        """Ensure profiles were generated."""
        assert len(regional_profiles) > 0

    def test_profiles_have_weather_fields(self, regional_profiles):
        """Ensure weather fields exist in output."""
        sample = regional_profiles[0]
        assert 'Imputed_Temp' in sample
        assert 'Imputed_Hum' in sample
        assert 'Imputed_Rain' in sample

    def test_known_district_has_realistic_weather(self, regional_profiles):
        """Check a known district has realistic weather values."""
        # Find a sample district we know exists in the historical dataset
        akola = None
        for row in regional_profiles:
            if 'akola' in row['District'].lower():
                akola = row
                break
        
        if akola is None:
            pytest.skip("Akola district not found in profiles")
        
        temp = float(akola['Imputed_Temp'])
        hum = float(akola['Imputed_Hum'])
        rain = float(akola['Imputed_Rain'])
        
        # Realistic ranges for Indian climate
        assert 15 <= temp <= 45, f"Temperature {temp} out of range"
        assert 30 <= hum <= 95, f"Humidity {hum} out of range"
        assert 50 <= rain <= 3000, f"Rainfall {rain} out of range"

    def test_soil_values_reasonable(self, regional_profiles):
        """Ensure soil values are within expected training data ranges."""
        for row in regional_profiles[:10]:  # Check first 10
            n = float(row['Imputed_N'])
            p = float(row['Imputed_P'])
            k = float(row['Imputed_K'])
            ph = float(row['Imputed_pH'])
            
            assert 0 <= n <= 150, f"N value {n} out of range"
            assert 0 <= p <= 150, f"P value {p} out of range"
            assert 0 <= k <= 210, f"K value {k} out of range"
            assert 3.0 <= ph <= 10.0, f"pH value {ph} out of range"
