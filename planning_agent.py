from agents import Agent, function_tool
import json

@function_tool
def create_research_plan(query: str) -> str:
    """
    Break down a complex question into research tasks.
    Returns a JSON string with research plan.
    """
    try:
        # Different planning strategies based on query type
        if "compare" in query.lower() or "vs" in query.lower():
            # Comparative analysis
            research_plan = {
                "original_query": query,
                "research_strategy": "comparative_analysis",
                "research_tasks": [
                    {"id": "task1", "task": f"Research first aspect of: {query}", "priority": "High", "time_estimate": "10m"},
                    {"id": "task2", "task": f"Research second aspect of: {query}", "priority": "High", "time_estimate": "10m"},
                    {"id": "task3", "task": f"Research comparison criteria for: {query}", "priority": "Medium", "time_estimate": "5m"},
                    {"id": "task4", "task": f"Research recent developments related to: {query}", "priority": "Medium", "time_estimate": "7m"}
                ],
            }
        elif "how has" in query.lower() or "from" in query.lower() and "to" in query.lower():
            # Historical analysis
            research_plan = {
                "original_query": query,
                "research_strategy": "historical_analysis",
                "research_tasks": [
                    {"id": "task1", "task": f"Research initial state for: {query}", "priority": "High", "time_estimate": "8m"},
                    {"id": "task2", "task": f"Research current state for: {query}", "priority": "High", "time_estimate": "8m"},
                    {"id": "task3", "task": f"Research key changes over time for: {query}", "priority": "High", "time_estimate": "10m"},
                    {"id": "task4", "task": f"Research factors influencing changes in: {query}", "priority": "Medium", "time_estimate": "7m"}
                ],
            }
        else:
            # General research
            research_plan = {
                "original_query": query,
                "research_strategy": "general_research",
                "research_tasks": [
                    {"id": "task1", "task": f"Research benefits/advantages of: {query}", "priority": "High", "time_estimate": "10m"},
                    {"id": "task2", "task": f"Research drawbacks/limitations of: {query}", "priority": "High", "time_estimate": "10m"},
                    {"id": "task3", "task": f"Research recent developments about: {query}", "priority": "Medium", "time_estimate": "7m"},
                    {"id": "task4", "task": f"Research expert opinions on: {query}", "priority": "Medium", "time_estimate": "8m"}
                ],
            }
        
        return json.dumps(research_plan)
        
    except Exception as e:
        # Fallback plan
        return json.dumps({
            "original_query": query,
            "research_tasks": [
                {"id": "task1", "task": f"Research {query}", "priority": "High"}
            ],
            "error": str(e),
        })

planning_agent = Agent(
    name="Planning Agent",
    instructions=(
        "You are a research planning expert. Break down complex questions into specific research tasks.\n"
        "Use the create_research_plan tool to generate a structured research plan.\n"
        "Consider different strategies based on query type (comparative, historical, general).\n"
        "Include priority levels and time estimates for each task.\n"
        "Return the plan as JSON that other agents can use."
    ),
    tools=[create_research_plan],
    handoffs=[]
)