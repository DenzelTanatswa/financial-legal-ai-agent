from langgraph.graph import StateGraph, END

from AI.state import AgentState
from AI.Agents.supervisor import supervisor
from AI.router import route
from AI.Agents.collaborator import collaborator_agent
from AI.Agents.validator import validator_agent

workflow = StateGraph(AgentState)

workflow.add_node("Supervisor",   supervisor)
workflow.add_node("Agent",        route)
workflow.add_node("Collaborator", collaborator_agent)
workflow.add_node("Validator",    validator_agent)

workflow.set_entry_point("Supervisor")

workflow.add_edge("Supervisor",   "Agent")
workflow.add_edge("Agent",        "Collaborator")
workflow.add_edge("Collaborator", "Validator")
workflow.add_edge("Validator",    END)

graph = workflow.compile()