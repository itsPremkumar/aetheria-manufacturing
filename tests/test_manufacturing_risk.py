"""
Tests for Manufacturing Risk Extension.
Test count: 16
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'src'))

from manufacturing_risk.risk_scoring import RiskScoring, RiskScore, RiskRating
from manufacturing_risk.supply_chain import SupplyChainRisk
from manufacturing_risk.production import ProductionRisk
from manufacturing_risk.compliance import ComplianceRisk


# ──────────────────── Risk Scoring Tests ──────────────────────────────


class TestRiskScoring:
    def test_create(self):
        scoring = RiskScoring()
        assert scoring is not None

    def test_calculate_score(self):
        scoring = RiskScoring()
        assert scoring.calculate_score(3, 4) == 12

    def test_get_rating_low(self):
        scoring = RiskScoring()
        assert scoring.get_rating(3) == RiskRating.LOW

    def test_get_rating_medium(self):
        scoring = RiskScoring()
        assert scoring.get_rating(7) == RiskRating.MEDIUM

    def test_get_rating_high(self):
        scoring = RiskScoring()
        assert scoring.get_rating(12) == RiskRating.HIGH

    def test_get_rating_critical(self):
        scoring = RiskScoring()
        assert scoring.get_rating(20) == RiskRating.CRITICAL

    def test_get_action(self):
        scoring = RiskScoring()
        assert "Monitor" in scoring.get_action(RiskRating.LOW)
        assert "Mitigate" in scoring.get_action(RiskRating.MEDIUM)
        assert "Immediate" in scoring.get_action(RiskRating.HIGH)
        assert "Executive" in scoring.get_action(RiskRating.CRITICAL)

    def test_assess_risk(self):
        scoring = RiskScoring()
        risk = scoring.assess_risk(likelihood=3, impact=4, risk_id="TEST-01", category="Test")
        assert risk.score == 12
        assert risk.rating == RiskRating.HIGH

    def test_assess_risk_invalid(self):
        scoring = RiskScoring()
        try:
            scoring.assess_risk(likelihood=6, impact=1)
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

    def test_prioritize_risks(self):
        scoring = RiskScoring()
        risks = [
            RiskScore(likelihood=2, impact=2),
            RiskScore(likelihood=5, impact=5),
            RiskScore(likelihood=3, impact=3),
        ]
        prioritized = scoring.prioritize_risks(risks)
        assert prioritized[0].score == 25
        assert prioritized[-1].score == 4

    def test_get_risk_distribution(self):
        scoring = RiskScoring()
        risks = [
            RiskScore(likelihood=1, impact=1),
            RiskScore(likelihood=2, impact=2),
            RiskScore(likelihood=3, impact=3),
            RiskScore(likelihood=5, impact=5),
        ]
        distribution = scoring.get_risk_distribution(risks)
        assert distribution["Low"] == 2
        assert distribution["Medium"] == 1
        assert distribution["Critical"] == 1


# ──────────────────── Supply Chain Risk Tests ──────────────────────────


class TestSupplyChainRisk:
    def test_create(self):
        sca = SupplyChainRisk()
        assert sca is not None

    def test_concentration_analysis(self):
        sca = SupplyChainRisk()
        result = sca.analyze_supplier_concentration("company_e1")
        assert "concentration_score" in result
        assert "risk_level" in result
        assert "recommendations" in result

    def test_supply_chain_mapping(self):
        sca = SupplyChainRisk()
        result = sca.map_supply_chain("company_e1", depth=2)
        assert "company_id" in result
        assert "tiers" in result

    def test_logistics_risk(self):
        sca = SupplyChainRisk()
        route = {"origin": "Shanghai", "destination": "Los Angeles", "mode": "sea"}
        result = sca.assess_logistics_risk(route)
        assert "risk_score" in result
        assert "risk_factors" in result

    def test_supplier_health(self):
        sca = SupplyChainRisk()
        result = sca.get_supplier_financial_health("supplier_001")
        assert "risk_score" in result
        assert "recommendations" in result


# ──────────────────── Production Risk Tests ────────────────────────────


class TestProductionRisk:
    def test_create(self):
        pr = ProductionRisk()
        assert pr is not None

    def test_capacity_utilization(self):
        pr = ProductionRisk()
        result = pr.analyze_capacity_utilization("plant_001")
        assert "utilization_pct" in result
        assert "risk_level" in result
        assert "bottleneck" in result

    def test_equipment_failure(self):
        pr = ProductionRisk()
        equipment = {"name": "press_01", "mtbf_hours": 800, "age_years": 8, "last_maintenance_days_ago": 200}
        result = pr.assess_equipment_failure_risk(equipment)
        assert "risk_score" in result
        assert "recommendations" in result

    def test_quality_risk(self):
        pr = ProductionRisk()
        result = pr.assess_quality_risk("widget_a", defect_rate=0.03, recall_count=2)
        assert "risk_score" in result
        assert "recommendations" in result

    def test_labor_risk(self):
        pr = ProductionRisk()
        result = pr.assess_labor_risk("facility_001")
        assert "risk_score" in result
        assert "recommendations" in result


# ──────────────────── Compliance Risk Tests ────────────────────────────


class TestComplianceRisk:
    def test_create(self):
        cr = ComplianceRisk()
        assert cr is not None

    def test_environmental_risk(self):
        cr = ComplianceRisk()
        emissions = {"co2_tons": 5000, "voc_tons": 200}
        violations = [{"date": "2024-01-15", "type": "emissions_exceedance"}]
        result = cr.assess_environmental_risk("plant_001", emissions, violations)
        assert "risk_score" in result
        assert "recommendations" in result

    def test_safety_risk(self):
        cr = ComplianceRisk()
        incidents = [{"date": "2024-01-10", "severity": 3}, {"date": "2024-01-15", "severity": 2}]
        result = cr.assess_safety_risk("plant_001", incidents)
        assert "risk_score" in result
        assert "recommendations" in result

    def test_trade_compliance(self):
        cr = ComplianceRisk()
        result = cr.assess_trade_compliance("company_e1")
        assert "risk_score" in result
        assert "recommendations" in result

    def test_compliance_report(self):
        cr = ComplianceRisk()
        result = cr.generate_compliance_report("company_e1")
        assert "environmental" in result
        assert "safety" in result
        assert "trade" in result
        assert "overall_risk" in result
