from langgraph.graph import StateGraph, END
from core.models import AgentState
from Agents.supervisor import supervisor
from Agents.parallel_agents import run_required_agents
from Agents.collaborator import collaborator_agent
from Agents.validator import validator_agent

workflow = StateGraph(AgentState)
workflow.add_node("Supervisor",   supervisor)
workflow.add_node("ParallelAgents", run_required_agents)
workflow.add_node("Collaborator", collaborator_agent)
workflow.add_node("Validator",    validator_agent)

workflow.set_entry_point("Supervisor")
workflow.add_edge("Supervisor",   "ParallelAgents")
workflow.add_edge("ParallelAgents", "Collaborator")
workflow.add_edge("Collaborator", "Validator")
workflow.add_conditional_edges("Validator", __import__("Agents.validator", fromlist=["validation_route"]).validation_route, {"retry": "ParallelAgents", "final": END})

graph = workflow.compile()
