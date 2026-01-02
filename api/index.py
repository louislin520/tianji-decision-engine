from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Dict
import hashlib
import os

# 🟢 Dependency Check
try:
    from lunar_python import Lunar
except ImportError:
    print("❌ Critical: 'lunar_python' missing. Run: pip install lunar_python")

app = FastAPI(
    title="Tianji V9.6 Stochastic Signal",
    description="Time-based deterministic entropy source for AI Agents.",
    version="9.6.0",
    docs_url="/docs",
    redoc_url=None
)

# ... [Core Definitions & Logic] ...

class SixGod(str, Enum):
    DA_AN = "DA_AN"
    LIU_LIAN = "LIU_LIAN"
    SU_XI = "SU_XI"
    CHI_KOU = "CHI_KOU"
    XIAO_JI = "XIAO_JI"
    KONG_WANG = "KONG_WANG"

class EnergyType(str, Enum):
    STABLE = "STABLE"
    FLOW = "FLOW"
    COMPETITIVE = "COMPETITIVE"
    NULL_STATE = "NULL_STATE"

class EntropyClass(str, Enum):
    LOW_VOLATILITY = "LOW_VOLATILITY"
    MEDIUM_VOLATILITY = "MEDIUM_VOLATILITY"
    HIGH_VOLATILITY = "HIGH_VOLATILITY"

class TianjiEngine:
    @staticmethod
    def calculate_entropy(dt: datetime):
        lunar = Lunar.fromDate(dt)
        m = abs(lunar.getMonth())
        d = lunar.getDay()
        h_idx = (dt.hour + 1) // 2 + 1
        if dt.hour == 23 or dt.hour == 0:
            h_idx = 1
        elif h_idx > 12:
            h_idx = 1
        idx_m = (m - 1) % 6
        idx_d = (idx_m + (d - 1)) % 6
        idx_h = (idx_d + (h_idx - 1)) % 6
        return list(SixGod)[idx_h], h_idx

    @staticmethod
    def get_signal_profile(god: SixGod):
        mapping = {
            SixGod.DA_AN: {"element": "WOOD", "energy_type": EnergyType.STABLE, "entropy_class": EntropyClass.LOW_VOLATILITY, "conflict_level": 0.1, "tone": "CALM", "temp_mod": -0.1, "risk": 0.2},
            SixGod.LIU_LIAN: {"element": "EARTH", "energy_type": EnergyType.STABLE, "entropy_class": EntropyClass.LOW_VOLATILITY, "conflict_level": 0.2, "tone": "PATIENT", "temp_mod": -0.2, "risk": 0.1},
            SixGod.SU_XI: {"element": "FIRE", "energy_type": EnergyType.FLOW, "entropy_class": EntropyClass.MEDIUM_VOLATILITY, "conflict_level": 0.3, "tone": "ENTHUSIASTIC", "temp_mod": 0.2, "risk": 0.6},
            SixGod.CHI_KOU: {"element": "METAL", "energy_type": EnergyType.COMPETITIVE, "entropy_class": EntropyClass.HIGH_VOLATILITY, "conflict_level": 0.85, "tone": "DEFENSIVE", "temp_mod": 0.1, "risk": 0.9},
            SixGod.XIAO_JI: {"element": "WATER", "energy_type": EnergyType.FLOW, "entropy_class": EntropyClass.MEDIUM_VOLATILITY, "conflict_level": 0.15, "tone": "DIPLOMATIC", "temp_mod": 0.3, "risk": 0.5},
            SixGod.KONG_WANG: {"element": "EARTH", "energy_type": EnergyType.NULL_STATE, "entropy_class": EntropyClass.HIGH_VOLATILITY, "conflict_level": 0.1, "tone": "REFLECTIVE", "temp_mod": 0.0, "risk": 0.0}
        }
        return mapping[god]

class SignalBlock(BaseModel):
    six_god: SixGod
    element: str
    energy_type: EnergyType
    conflict_level: float

class MetaBlock(BaseModel):
    entropy_class: EntropyClass
    stability_window: str
    next_state_change: str
    hash: str
    reproducible: bool = True

class DirectivesBlock(BaseModel):
    tone: str
    temperature_modifier: float
    risk_aversion: float

class TianjiResponse(BaseModel):
    signal: SignalBlock
    meta: MetaBlock
    agent_directives: DirectivesBlock

@app.get("/", include_in_schema=False)
def root():
    return {"message": "Tianji V9.6 is running. Access /docs for API schema."}

@app.get("/v1/signal/now", response_model=TianjiResponse)
def get_current_signal():
    now = datetime.now()
    god, h_idx = TianjiEngine.calculate_entropy(now)
    profile = TianjiEngine.get_signal_profile(god)
    next_change = now + timedelta(hours=2)
    state_str = f"{now.year}{now.month}{now.day}{h_idx}"
    state_hash = hashlib.md5(state_str.encode()).hexdigest()[:8]

    return TianjiResponse(
        signal=SignalBlock(six_god=god, element=profile["element"], energy_type=profile["energy_type"], conflict_level=profile["conflict_level"]),
        meta=MetaBlock(entropy_class=profile["entropy_class"], stability_window="120m", next_state_change=next_change.isoformat(), hash=state_hash),
        agent_directives=DirectivesBlock(tone=profile["tone"], temperature_modifier=profile["temp_mod"], risk_aversion=profile["risk"])
    )
