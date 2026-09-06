"""Tests for disease_prediction.py."""

import pytest
from disease_prediction import (
    Disease, PredictionResult, EnvironmentalConditions, Severity,
    DiseasePredictor,
)


class TestDisease:
    def test_disease_fields(self):
        disease = Disease(
            disease_id="test_disease",
            name="Test Disease",
            scientific_name="Testus diseasus",
            affected_crops=["crop_001"],
            symptoms=["symptom1", "symptom2"],
            conditions={"temperature": (20, 30)},
            treatments=["treatment1"],
            prevention=["prevention1"],
        )
        assert disease.disease_id == "test_disease"
        assert disease.name == "Test Disease"
        assert disease.severity == Severity.MEDIUM

    def test_disease_to_dict(self):
        disease = Disease(
            disease_id="test_disease",
            name="Test Disease",
            scientific_name="Testus",
            affected_crops=["crop_001"],
            symptoms=["symptom1"],
            conditions={},
            treatments=[],
            prevention=[],
        )
        d = disease.to_dict()
        assert d["disease_id"] == "test_disease"
        assert d["name"] == "Test Disease"


class TestEnvironmentalConditions:
    def test_conditions_fields(self):
        conditions = EnvironmentalConditions(
            temperature=25.0,
            humidity=80.0,
            rainfall=100.0,
            soil_ph=6.5,
            soil_moisture=50.0,
            season="kharif",
        )
        assert conditions.temperature == 25.0
        assert conditions.humidity == 80.0

    def test_conditions_to_dict(self):
        conditions = EnvironmentalConditions(
            temperature=25.0,
            humidity=80.0,
            rainfall=100.0,
            soil_ph=6.5,
            soil_moisture=50.0,
            season="kharif",
        )
        d = conditions.to_dict()
        assert d["temperature"] == 25.0
        assert d["humidity"] == 80.0


class TestDiseasePredictor:
    def test_default_diseases_loaded(self):
        predictor = DiseasePredictor()
        assert len(predictor.diseases) >= 8

    def test_predict_rice_blast(self):
        predictor = DiseasePredictor()
        symptoms = ["diamond-shaped lesions", "gray centers", "brown margins"]
        results = predictor.predict("rice_001", symptoms)
        assert len(results) > 0
        assert results[0].disease_name == "Blast"

    def test_predict_potato_late_blight(self):
        predictor = DiseasePredictor()
        symptoms = ["water-soaked lesions", "white fuzz on undersides", "rapid defoliation"]
        results = predictor.predict("potato_001", symptoms)
        assert len(results) > 0
        assert results[0].disease_name == "Late Blight"

    def test_predict_tomato_early_blight(self):
        predictor = DiseasePredictor()
        symptoms = ["concentric rings", "yellowing", "leaf drop"]
        results = predictor.predict("tomato_001", symptoms)
        assert len(results) > 0
        assert results[0].disease_name == "Early Blight"

    def test_predict_with_conditions(self):
        predictor = DiseasePredictor()
        symptoms = ["orange-brown pustules", "yellowing"]
        conditions = EnvironmentalConditions(
            temperature=20.0,
            humidity=80.0,
            rainfall=50.0,
            soil_ph=6.5,
            soil_moisture=60.0,
            season="winter",
        )
        results = predictor.predict("wheat_001", symptoms, conditions)
        assert len(results) > 0

    def test_predict_no_match(self):
        predictor = DiseasePredictor()
        symptoms = ["completely unrelated symptom"]
        results = predictor.predict("wheat_001", symptoms)
        assert len(results) == 0

    def test_predict_wrong_crop(self):
        predictor = DiseasePredictor()
        symptoms = ["diamond-shaped lesions"]
        results = predictor.predict("wheat_001", symptoms)  # Blast affects rice, not wheat
        assert len(results) == 0

    def test_get_disease(self):
        predictor = DiseasePredictor()
        disease = predictor.get_disease("disease_blast")
        assert disease is not None
        assert disease.name == "Blast"

    def test_get_disease_invalid(self):
        predictor = DiseasePredictor()
        disease = predictor.get_disease("invalid")
        assert disease is None

    def test_search_diseases(self):
        predictor = DiseasePredictor()
        results = predictor.search_diseases("blast")
        assert len(results) > 0

    def test_search_diseases_by_symptom(self):
        predictor = DiseasePredictor()
        results = predictor.search_diseases("yellowing")
        assert len(results) > 0

    def test_get_diseases_for_crop(self):
        predictor = DiseasePredictor()
        diseases = predictor.get_diseases_for_crop("tomato_001")
        assert len(diseases) > 0

    def test_add_disease(self):
        predictor = DiseasePredictor()
        new_disease = Disease(
            disease_id="disease_new",
            name="New Disease",
            scientific_name="Novus morbus",
            affected_crops=["wheat_001"],
            symptoms=["new symptom"],
            conditions={},
            treatments=[],
            prevention=[],
        )
        predictor.add_disease(new_disease)
        assert "disease_new" in predictor.diseases

    def test_get_all_diseases(self):
        predictor = DiseasePredictor()
        diseases = predictor.get_all_diseases()
        assert len(diseases) >= 8

    def test_get_statistics(self):
        predictor = DiseasePredictor()
        stats = predictor.get_statistics()
        assert stats["total_diseases"] >= 8
        assert "severity_counts" in stats
        assert "affected_crops" in stats

    def test_prediction_result_to_dict(self):
        result = PredictionResult(
            disease_id="disease_test",
            disease_name="Test",
            confidence=0.85,
            severity=Severity.HIGH,
            matching_symptoms=["symptom1"],
            recommended_treatments=["treatment1"],
            prevention_measures=["prevention1"],
        )
        d = result.to_dict()
        assert d["disease_id"] == "disease_test"
        assert d["confidence"] == 0.85
        assert d["severity"] == "high"

    def test_predict_with_top_n(self):
        predictor = DiseasePredictor()
        symptoms = ["yellowing"]  # Matches multiple diseases
        results = predictor.predict("tomato_001", symptoms, top_n=2)
        assert len(results) <= 2

    def test_confidence_range(self):
        predictor = DiseasePredictor()
        symptoms = ["diamond-shaped lesions", "gray centers"]
        results = predictor.predict("rice_001", symptoms)
        for result in results:
            assert 0 <= result.confidence <= 1

    def test_severity_levels(self):
        predictor = DiseasePredictor()
        assert len(predictor.get_all_diseases()) > 0
        for disease in predictor.get_all_diseases():
            assert disease.severity in Severity
