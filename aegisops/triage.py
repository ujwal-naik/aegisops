import re
from typing import Tuple, List, Dict, Any
from aegisops.models import TriageCategory, UnitType, Incident

class TriageEngine:
    """
    Automated disaster triage engine implementing START (Simple Triage and Rapid Treatment)
    guidelines adapted for field messaging, SMS, and radio voice-to-text transcripts.
    """

    CRITICAL_KEYWORDS = [
        r"\bunconscious\b", r"\bunresponsive\b", r"\bnot breathing\b", r"\bchoking\b",
        r"\barterial\b", r"\bheavy bleeding\b", r"\bgushing blood\b", r"\bcrush syndrome\b",
        r"\bchest pain\b", r"\bcpr\b", r"\bcardiac\b", r"\bdrowning\b", r"\bdying\b",
        r"\bwater rising\b", r"\bwaist high water\b", r"\bneck deep\b", r"\bsinking\b",
        r"\basphyxiat\w*\b", r"\bsevere head injury\b", r"\blimb severed\b"
    ]

    SERIOUS_KEYWORDS = [
        r"\bfracture\b", r"\bbroken bone\b", r"\bdeep cut\b", r"\bcannot walk\b",
        r"\blaceration\b", r"\bconcussion\b", r"\bdislocated\b", r"\bdiabetic\b",
        r"\binsulin\b", r"\bpregnant\b", r"\bmoderate burn\b", r"\bchest trauma\b",
        r"\bhypothermi\w*\b", r"\bheat stroke\b", r"\bimmobile\b"
    ]

    MINOR_KEYWORDS = [
        r"\bminor cut\b", r"\bscratches\b", r"\bwalking\b", r"\bbruised\b",
        r"\bmild pain\b", r"\bsprain\b", r"\bstable\b", r"\bneed food\b",
        r"\bneed water\b", r"\bblanket\b", r"\bshelter\b"
    ]

    DECEASED_KEYWORDS = [
        r"\bno pulse\b", r"\bcold and stiff\b", r"\bdeceased\b", r"\bdead body\b",
        r"\bfatal trauma\b", r"\brigor mortis\b", r"\bcrushed completely\b"
    ]

    HAZARD_PATTERNS = {
        "flood_water": [r"\bflood\b", r"\bwater rising\b", r"\bsubmerged\b", r"\broof\b", r"\bboat\b", r"\bcurrent\b"],
        "structural_collapse": [r"\brubble\b", r"\bdebris\b", r"\bcollapsed\b", r"\bpinned\b", r"\bcrushed\b", r"\btrapped under\b"],
        "gas_leak": [r"\bgas smell\b", r"\bgas leak\b", r"\bhissing\b", r"\bfumes\b", r"\bchemical\b"],
        "electrical_hazard": [r"\blive wire\b", r"\bpower line\b", r"\bsparking\b", r"\belectrocution\b"],
        "fire_outbreak": [r"\bfire\b", r"\bsmoke\b", r"\bflames\b", r"\bexplosion\b"]
    }

    @classmethod
    def evaluate(cls, text: str) -> Dict[str, Any]:
        """
        Analyzes raw emergency transmission text and returns structured triage assessment.
        """
        lower = text.lower()
        triage_level = TriageCategory.YELLOW  # Default fallback for unverified emergency
        base_score = 50.0

        # 1. Check Deceased / Expectant
        if any(re.search(pat, lower) for pat in cls.DECEASED_KEYWORDS):
            # Check if there are other living survivors reported in the same text
            if not any(w in lower for w in ["other people", "survivors", "children", "family", "help us"]):
                return {
                    "triage_level": TriageCategory.BLACK,
                    "urgency_score": 10.0,
                    "hazards": cls._extract_hazards(lower),
                    "survivor_count": 0,
                    "trapped_count": 0,
                    "required_unit_type": UnitType.GENERAL_EVAC
                }

        # 2. Check Critical (Immediate Red)
        critical_hits = [pat for pat in cls.CRITICAL_KEYWORDS if re.search(pat, lower)]
        serious_hits = [pat for pat in cls.SERIOUS_KEYWORDS if re.search(pat, lower)]
        minor_hits = [pat for pat in cls.MINOR_KEYWORDS if re.search(pat, lower)]

        if critical_hits or "trapped" in lower and ("water" in lower or "fire" in lower or "rubble" in lower):
            triage_level = TriageCategory.RED
            base_score = 85.0 + min(len(critical_hits) * 3.0, 15.0)
        elif serious_hits:
            triage_level = TriageCategory.YELLOW
            base_score = 55.0 + min(len(serious_hits) * 4.0, 20.0)
        elif minor_hits:
            triage_level = TriageCategory.GREEN
            base_score = 25.0 + min(len(minor_hits) * 2.0, 15.0)

        hazards = cls._extract_hazards(lower)
        survivor_count, trapped_count = cls._extract_counts(lower)

        # Hazard multiplier
        if "flood_water" in hazards or "structural_collapse" in hazards:
            base_score += 5.0
        if "fire_outbreak" in hazards or "gas_leak" in hazards:
            base_score += 7.0

        # Multi-victim boost
        if trapped_count > 0:
            base_score += min(trapped_count * 2.5, 10.0)
        if survivor_count > 3:
            base_score += min(survivor_count * 1.0, 8.0)

        urgency_score = min(max(round(base_score, 1), 5.0), 100.0)
        unit_type = cls._determine_unit(hazards, triage_level, lower)

        return {
            "triage_level": triage_level,
            "urgency_score": urgency_score,
            "hazards": hazards,
            "survivor_count": survivor_count,
            "trapped_count": trapped_count,
            "required_unit_type": unit_type
        }

    @classmethod
    def _extract_hazards(cls, text: str) -> List[str]:
        detected = []
        for hazard, patterns in cls.HAZARD_PATTERNS.items():
            if any(re.search(pat, text) for pat in patterns):
                detected.append(hazard)
        return detected

    @classmethod
    def _extract_counts(cls, text: str) -> Tuple[int, int]:
        survivors = 1
        trapped = 0

        # Number extraction heuristics
        # e.g., "5 people trapped", "family of 4", "3 kids", "2 trapped"
        trapped_match = re.search(r"(\d+)\s*(?:people|persons|victims|men|women|children|kids)?\s*(?:are\s*)?trapped", text)
        if trapped_match:
            try:
                trapped = int(trapped_match.group(1))
            except ValueError:
                trapped = 1
        elif "trapped" in text or "pinned" in text or "stuck" in text:
            trapped = 1

        people_match = re.search(r"(\d+)\s*(?:people|persons|victims|survivors|members|family of (\d+))", text)
        if people_match:
            try:
                survivors = int(people_match.group(1) or people_match.group(2))
            except (ValueError, TypeError):
                survivors = max(trapped, 1)
        else:
            survivors = max(trapped, 1)

        return survivors, trapped

    @classmethod
    def _determine_unit(cls, hazards: List[str], triage: TriageCategory, text: str) -> UnitType:
        if "flood_water" in hazards or "water" in text or "boat" in text:
            return UnitType.WATER_RESCUE
        if "structural_collapse" in hazards or "rubble" in text or "pinned" in text:
            return UnitType.HEAVY_SAR
        if triage == TriageCategory.RED:
            return UnitType.AMBULANCE
        if "medical" in text or "doctor" in text or "insulin" in text:
            return UnitType.MEDICAL_STRIKE
        if "drone" in text or "survey" in text:
            return UnitType.AERIAL_DRONE
        return UnitType.GENERAL_EVAC
