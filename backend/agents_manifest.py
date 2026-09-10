"""
ADK Agents Manifest - Exposes agents for ADK web UI discovery
"""

from app.agents.vision_agent import vision_agent
from app.agents.phi_agent import phi_agent
from app.agents.parser_agent import parser_agent
from app.agents.med_info_agent import med_info_agent
from app.agents.safety_agent import safety_agent
from app.agents.explanation_agent import explanation_agent
from app.services.orchestrator import orchestrator

# Export all agents for ADK discovery
__all__ = [
    "vision_agent",
    "phi_agent",
    "parser_agent",
    "med_info_agent",
    "safety_agent",
    "explanation_agent",
    "orchestrator",
]
