from google.adk.agents import BaseAgent

from app.agents.vision_agent import vision_agent
from app.agents.phi_agent import phi_agent
from app.agents.parser_agent import parser_agent
from app.agents.med_info_agent import med_info_agent
from app.agents.safety_agent import safety_agent
from app.agents.explanation_agent import explanation_agent


def test_all_agents_are_adk_agents():
    agents = [
        vision_agent,
        phi_agent,
        parser_agent,
        med_info_agent,
        safety_agent,
        explanation_agent,
    ]

    for agent in agents:
        assert isinstance(agent, BaseAgent), f"{agent.__class__.__name__} is not an ADK BaseAgent"
        assert agent.name, f"{agent.__class__.__name__} is missing a name"
