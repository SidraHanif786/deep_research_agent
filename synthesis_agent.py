from agents import Agent, function_tool
import json
from datetime import datetime

@function_tool
def synthesize_findings(research_data: str) -> str:
    """
    Synthesize research findings from multiple sources.
    Returns synthesized insights as JSON.
    """
    try:
        data = json.loads(research_data)
        
        # In a real implementation, this would use an LLM for proper synthesis
        # For this example, we'll create a structured synthesis
        
        # Extract key information from research data
        sources = data.get("sources", [])
        findings = data.get("findings", [])
        
        key_insights = []
        consensus_points = []
        conflicting_points = []
        
        # Simple synthesis logic
        for finding in findings[:5]:  # Process first 5 findings
            content = finding.get("content", "")
            if "benefit" in content.lower() or "advantage" in content.lower():
                key_insights.append(f"Positive aspect: {content[:200]}...")
            elif "drawback" in content.lower() or "disadvantage" in content.lower():
                key_insights.append(f"Negative aspect: {content[:200]}...")
            else:
                key_insights.append(f"Finding: {content[:200]}...")
        
        # Basic conflict detection
        if len(sources) >= 2:
            conflicting_points.append("Multiple perspectives found - need further analysis")
            consensus_points.append("General agreement on core facts")
        
        confidence_level = "High" if len(sources) > 3 else "Medium" if len(sources) > 1 else "Low"
        
        synthesis = {
            "key_insights": key_insights,
            "consensus_points": consensus_points,
            "conflicting_points": conflicting_points,
            "confidence_level": confidence_level,
            "sources_analyzed": len(sources),
            "summary": f"Comprehensive synthesis of {len(sources)} sources with {confidence_level} confidence",
            "synthesized_at": datetime.now().isoformat()
        }
        
        return json.dumps(synthesis)
    except Exception as e:
        return json.dumps({"error": str(e), "synthesis_failed": datetime.now().isoformat()})

@function_tool
def resolve_conflicts(conflicting_data: str) -> str:
    """
    Resolve conflicts between different sources or findings.
    Returns conflict resolution analysis as JSON.
    """
    try:
        data = json.loads(conflicting_data)
        
        # Simple conflict resolution logic
        resolution = {
            "conflict_description": "Differences in perspectives or information between sources",
            "resolution_approach": "Prioritized more recent and reliable sources",
            "recommended_position": "Consider multiple perspectives and context",
            "confidence_in_resolution": "Medium",
            "suggested_further_research": "Verify with additional authoritative sources",
            "resolved_at": datetime.now().isoformat()
        }
        
        return json.dumps(resolution)
    except Exception as e:
        return json.dumps({"error": str(e), "resolution_failed": datetime.now().isoformat()})

synthesis_agent = Agent(
    name="Synthesis Agent",
    instructions=(
        "You synthesize research findings from multiple sources.\n"
        "Identify key insights, consensus points, and conflicting information.\n"
        "Assess the overall confidence level in the findings.\n"
        "Use the synthesize_findings tool to create a comprehensive synthesis.\n"
        "Return structured JSON that can be used for report writing."
    ),
    tools=[synthesize_findings],
    handoffs=[]
)

conflict_resolver_agent = Agent(
    name="Conflict Resolver",
    instructions=(
        "You specialize in resolving conflicts between different sources or findings.\n"
        "Use resolve_conflicts to analyze contradictory information.\n"
        "Provide recommendations for handling conflicting data.\n"
        "Suggest approaches for further verification when needed.\n"
        "Return structured conflict resolution reports."
    ),
    tools=[resolve_conflicts],
    handoffs=[]
)