"""
disease_prediction.py — ML-based Disease Prediction Module for Agriculture KG.

Provides disease prediction for crops based on:
- Symptoms (visual, physiological)
- Environmental conditions (temperature, humidity, soil conditions)
- Seasonal patterns
- Crop type and growth stage

Uses a rule-based ML approach (decision tree / pattern matching) that works offline.
Can be extended with scikit-learn for more advanced models.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional
import json
import os
import re
from enum import Enum


class Severity(Enum):
    """Disease severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Disease:
    """A crop disease."""
    disease_id: str
    name: str
    scientific_name: str
    affected_crops: list[str]  # crop_ids
    symptoms: list[str]
    conditions: dict[str, Any]  # favorable conditions
    treatments: list[str]
    prevention: list[str]
    severity: Severity = Severity.MEDIUM
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "disease_id": self.disease_id,
            "name": self.name,
            "scientific_name": self.scientific_name,
            "affected_crops": self.affected_crops,
            "symptoms": self.symptoms,
            "conditions": self.conditions,
            "treatments": self.treatments,
            "prevention": self.prevention,
            "severity": self.severity.value,
            "metadata": self.metadata,
        }


@dataclass
class PredictionResult:
    """Result of a disease prediction."""
    disease_id: str
    disease_name: str
    confidence: float  # 0.0 to 1.0
    severity: Severity
    matching_symptoms: list[str]
    recommended_treatments: list[str]
    prevention_measures: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "disease_id": self.disease_id,
            "disease_name": self.disease_name,
            "confidence": self.confidence,
            "severity": self.severity.value,
            "matching_symptoms": self.matching_symptoms,
            "recommended_treatments": self.recommended_treatments,
            "prevention_measures": self.prevention_measures,
            "metadata": self.metadata,
        }


@dataclass
class EnvironmentalConditions:
    """Environmental conditions for disease prediction."""
    temperature: float  # Celsius
    humidity: float  # percentage
    rainfall: float  # mm
    soil_ph: float
    soil_moisture: float  # percentage
    season: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "temperature": self.temperature,
            "humidity": self.humidity,
            "rainfall": self.rainfall,
            "soil_ph": self.soil_ph,
            "soil_moisture": self.soil_moisture,
            "season": self.season,
        }


class DiseasePredictor:
    """
    ML-based disease prediction engine.

    Uses pattern matching and rule-based classification to predict diseases
    based on symptoms and environmental conditions.
    """

    def __init__(self):
        self.diseases: dict[str, Disease] = {}
        self._load_default_diseases()

    def _load_default_diseases(self):
        """Load default disease data."""
        diseases = [
            Disease(
                disease_id="disease_blast",
                name="Blast",
                scientific_name="Magnaporthe oryzae",
                affected_crops=["rice_001"],
                symptoms=["diamond-shaped lesions", "gray centers", "brown margins", "leaf drying"],
                conditions={"temperature": (25, 30), "humidity": (80, 100), "rainfall": "high"},
                treatments=["fungicide application", "resistant varieties", "proper spacing"],
                prevention=["balanced fertilization", "avoid excessive nitrogen", "crop rotation"],
                severity=Severity.HIGH,
            ),
            Disease(
                disease_id="disease_rust",
                name="Rust",
                scientific_name="Puccinia spp.",
                affected_crops=["wheat_001", "soybean_001"],
                symptoms=["orange-brown pustules", "yellowing", "leaf spots", "reduced vigor"],
                conditions={"temperature": (15, 25), "humidity": (70, 90), "rainfall": "moderate"},
                treatments=["fungicide spray", "remove infected leaves", "resistant varieties"],
                prevention=["crop rotation", "proper spacing", "avoid overhead irrigation"],
                severity=Severity.MEDIUM,
            ),
            Disease(
                disease_id="disease_blight_late",
                name="Late Blight",
                scientific_name="Phytophthora infestans",
                affected_crops=["potato_001", "tomato_001"],
                symptoms=["water-soaked lesions", "white fuzz on undersides", "rapid defoliation", "tuber rot"],
                conditions={"temperature": (10, 25), "humidity": (90, 100), "rainfall": "high"},
                treatments=["copper-based fungicides", "remove infected plants", "destroy crop debris"],
                prevention=["resistant varieties", "proper drainage", "avoid overhead watering"],
                severity=Severity.CRITICAL,
            ),
            Disease(
                disease_id="disease_blight_early",
                name="Early Blight",
                scientific_name="Alternaria solani",
                affected_crops=["potato_001", "tomato_001"],
                symptoms=["concentric rings", "yellowing", "leaf drop", "stem lesions"],
                conditions={"temperature": (24, 29), "humidity": (70, 90), "rainfall": "moderate"},
                treatments=["chlorothalonil", "mancozeb", "remove infected leaves"],
                prevention=["mulching", "crop rotation", "proper spacing"],
                severity=Severity.MEDIUM,
            ),
            Disease(
                disease_id="disease_wilt",
                name="Wilt",
                scientific_name="Fusarium oxysporum",
                affected_crops=["cotton_001", "tomato_001"],
                symptoms=["yellowing of lower leaves", "wilting during day", "stunted growth", "vascular discoloration"],
                conditions={"temperature": (25, 35), "humidity": (60, 80), "soil_ph": (5.5, 6.5)},
                treatments=["soil fumigation", "resistant varieties", "biological control"],
                prevention=["crop rotation", "soil solarization", "proper drainage"],
                severity=Severity.HIGH,
            ),
            Disease(
                disease_id="disease_powdery_mildew",
                name="Powdery Mildew",
                scientific_name="Erysiphe spp.",
                affected_crops=["wheat_001", "tomato_001", "potato_001"],
                symptoms=["white powdery spots", "leaf curling", "stunted growth", "reduced yield"],
                conditions={"temperature": (15, 27), "humidity": (50, 70), "rainfall": "low"},
                treatments=["sulfur-based fungicides", "potassium bicarbonate", "neem oil"],
                prevention=["proper spacing", "avoid overhead watering", "resistant varieties"],
                severity=Severity.MEDIUM,
            ),
            Disease(
                disease_id="disease_mosaic",
                name="Yellow Mosaic",
                scientific_name="Mungbean yellow mosaic virus",
                affected_crops=["soybean_001"],
                symptoms=["yellow mosaic pattern", "leaf curling", "stunted growth", "reduced pod formation"],
                conditions={"temperature": (25, 35), "humidity": (60, 80), "rainfall": "moderate"},
                treatments=["insect vector control", "remove infected plants", "resistant varieties"],
                prevention=["whitefly control", "border cropping", "resistant varieties"],
                severity=Severity.HIGH,
            ),
            Disease(
                disease_id="disease_charcoal_rot",
                name="Charcoal Rot",
                scientific_name="Macrophomina phaseolina",
                affected_crops=["soybean_001", "groundnut_001"],
                symptoms=["wilting", "premature drying", "black microsclerotia", "stem discoloration"],
                conditions={"temperature": (30, 40), "humidity": (40, 60), "rainfall": "low"},
                treatments=["fungicide seed treatment", "crop rotation", "organic amendments"],
                prevention=["drought-resistant varieties", "irrigation management", "crop rotation"],
                severity=Severity.MEDIUM,
            ),
            Disease(
                disease_id="disease_leaf_curl",
                name="Leaf Curl",
                scientific_name="Tomato leaf curl virus",
                affected_crops=["tomato_001", "cotton_001"],
                symptoms=["upward curling of leaves", "yellowing", "stunted growth", "reduced fruit set"],
                conditions={"temperature": (25, 35), "humidity": (60, 80), "rainfall": "moderate"},
                treatments=["insect vector control", "remove infected plants", "resistant varieties"],
                prevention=["whitefly control", "netting", "resistant varieties"],
                severity=Severity.HIGH,
            ),
            Disease(
                disease_id="disease_scab",
                name="Scab",
                scientific_name="Streptomyces scabies",
                affected_crops=["potato_001"],
                symptoms=["rough lesions", "corky tissue", "pitted spots", "reduced marketability"],
                conditions={"temperature": (20, 25), "humidity": (70, 90), "soil_ph": (6.5, 7.5)},
                treatments=["acidic soil amendments", "resistant varieties", "proper irrigation"],
                prevention=["maintain soil pH below 5.5", "crop rotation", "adequate irrigation"],
                severity=Severity.LOW,
            ),
        ]
        for disease in diseases:
            self.diseases[disease.disease_id] = disease

    def predict(
        self,
        crop_id: str,
        symptoms: list[str],
        conditions: EnvironmentalConditions | None = None,
        top_n: int = 5,
    ) -> list[PredictionResult]:
        """
        Predict diseases based on symptoms and conditions.

        Args:
            crop_id: ID of the crop
            symptoms: List of observed symptoms
            conditions: Environmental conditions
            top_n: Number of top predictions to return

        Returns:
            List of PredictionResult sorted by confidence
        """
        predictions = []

        for disease in self.diseases.values():
            # Check if disease affects this crop
            if crop_id not in disease.affected_crops:
                continue

            # Calculate symptom match score
            matching_symptoms = []
            for symptom in symptoms:
                symptom_lower = symptom.lower()
                for disease_symptom in disease.symptoms:
                    if symptom_lower in disease_symptom.lower() or disease_symptom.lower() in symptom_lower:
                        matching_symptoms.append(disease_symptom)
                        break

            if not matching_symptoms:
                continue

            # Calculate confidence based on symptom overlap
            symptom_score = len(matching_symptoms) / len(disease.symptoms) if disease.symptoms else 0

            # Calculate condition match score
            condition_score = 0.0
            if conditions:
                temp_match = 0.0
                if "temperature" in disease.conditions:
                    temp_range = disease.conditions["temperature"]
                    if temp_range[0] <= conditions.temperature <= temp_range[1]:
                        temp_match = 1.0
                    else:
                        temp_match = max(0, 1 - abs(conditions.temperature - sum(temp_range) / 2) / 10)

                humidity_match = 0.0
                if "humidity" in disease.conditions:
                    hum_range = disease.conditions["humidity"]
                    if hum_range[0] <= conditions.humidity <= hum_range[1]:
                        humidity_match = 1.0
                    else:
                        humidity_match = max(0, 1 - abs(conditions.humidity - sum(hum_range) / 2) / 20)

                condition_score = (temp_match + humidity_match) / 2

            # Combined confidence
            confidence = (symptom_score * 0.7) + (condition_score * 0.3)

            if confidence > 0.1:
                predictions.append(PredictionResult(
                    disease_id=disease.disease_id,
                    disease_name=disease.name,
                    confidence=round(min(1.0, confidence), 2),
                    severity=disease.severity,
                    matching_symptoms=matching_symptoms,
                    recommended_treatments=disease.treatments,
                    prevention_measures=disease.prevention,
                    metadata={
                        "symptom_score": round(symptom_score, 2),
                        "condition_score": round(condition_score, 2),
                    "total_symptoms": len(disease.symptoms),
                    "matched_symptoms": len(matching_symptoms),
                    "scientific_name": disease.scientific_name,
                    "affected_crops": disease.affected_crops,
                    "conditions": disease.conditions,
                    "all_symptoms": disease.symptoms,
                    "severity_value": disease.severity.value,
                }))

        predictions.sort(key=lambda x: x.confidence, reverse=True)
        return predictions[:top_n]

    def get_disease(self, disease_id: str) -> Disease | None:
        """Get a disease by ID."""
        return self.diseases.get(disease_id)

    def search_diseases(self, query: str) -> list[Disease]:
        """Search diseases by name or symptoms."""
        query_lower = query.lower()
        results = []
        for disease in self.diseases.values():
            if (query_lower in disease.name.lower() or
                query_lower in disease.scientific_name.lower() or
                any(query_lower in s.lower() for s in disease.symptoms)):
                results.append(disease)
        return results

    def get_diseases_for_crop(self, crop_id: str) -> list[Disease]:
        """Get all diseases that affect a specific crop."""
        return [d for d in self.diseases.values() if crop_id in d.affected_crops]

    def add_disease(self, disease: Disease) -> None:
        """Add a new disease to the predictor."""
        self.diseases[disease.disease_id] = disease

    def get_all_diseases(self) -> list[Disease]:
        """Get all diseases."""
        return list(self.diseases.values())

    def get_statistics(self) -> dict[str, Any]:
        """Get predictor statistics."""
        return {
            "total_diseases": len(self.diseases),
            "severity_counts": {
                severity.value: sum(1 for d in self.diseases.values() if d.severity == severity)
                for severity in Severity
            },
            "affected_crops": list(set(
                crop_id for d in self.diseases.values() for crop_id in d.affected_crops
            )),
        }
