from agents import Agent, function_tool
from tavily import TavilyClient
import json
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# Cache for search results to avoid duplicate API calls
search_cache = {}

@function_tool
async def search_web(query: str, max_results: int = 5) -> str:
    """
    Search the web for information using Tavily API.
    Returns search results as JSON.
    """
    # Check cache first
    cache_key = f"{query}_{max_results}"
    if cache_key in search_cache:
        print(f"Using cached results for: {query}")
        return search_cache[cache_key]
    
    try:
        response = tavily_client.search(
            query=query, 
            search_depth="advanced", 
            max_results=max_results,
            include_answer=True
        )
        
        results = []
        for result in response.get("results", []):
            results.append({
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "content": result.get("content", "")[:1000] + "..." if len(result.get("content", "")) > 1000 else result.get("content", ""),
                "score": result.get("score", 0),
                "published_date": result.get("published_date", ""),
            })
        
        # Include direct answer if available
        if response.get("answer"):
            results.insert(0, {
                "title": "Direct Answer",
                "url": "",
                "content": response["answer"],
                "score": 1.0,
                "is_direct_answer": True
            })
        
        result_json = json.dumps({
            "query": query,
            "results": results,
            "total_results": len(results),
        })
        
        # Cache the result
        search_cache[cache_key] = result_json
        return result_json
        
    except Exception as e:
        error_result = json.dumps({
            "error": str(e), 
            "query": query,
        })
        search_cache[cache_key] = error_result
        return error_result

@function_tool
def source_checker(url: str) -> str:
    """
    Check the reliability of a source based on its domain and characteristics.
    Returns reliability assessment as JSON.
    """
    reliable_domains = [".edu", ".gov", ".org", "wikipedia.org", "bbc.com", "reuters.com", 
                       "nytimes.com", "nature.com", "science.org", "who.int"]
    questionable_domains = [".blog", "medium.com", "quora.com", "reddit.com", "personal.website"]
    
    reliability = "Medium"
    reason = "Standard website"
    trust_score = 0.5
    
    # Check domain patterns
    for domain in reliable_domains:
        if domain in url:
            reliability = "High"
            trust_score = 0.9
            reason = f"Known reliable domain: {domain}"
            break
            
    for domain in questionable_domains:
        if domain in url:
            reliability = "Low"
            trust_score = 0.3
            reason = f"User-generated content domain: {domain}"
            break
    
    # Additional checks
    if "research" in url or "study" in url:
        trust_score = min(1.0, trust_score + 0.1)
        reason += " | Contains research/study content"
    
    if "news" in url or "article" in url:
        trust_score = min(1.0, trust_score + 0.05)
    
    return json.dumps({
        "url": url,
        "reliability": reliability,
        "trust_score": trust_score,
        "reason": reason,
    })

@function_tool
def fact_finder(claim: str, sources: str) -> str:
    """
    Fact-check a specific claim against provided sources.
    Returns fact-check assessment as JSON.
    """
    try:
        sources_data = json.loads(sources)
        
        supporting_sources = []
        contradicting_sources = []
        
        for source in sources_data.get("results", [])[:3]:  # Check top 3 sources
            content = source.get("content", "").lower()
            claim_lower = claim.lower()
            
            if claim_lower in content:
                supporting_sources.append({
                    "title": source.get("title", ""),
                    "url": source.get("url", "")
                })
            else:
                contradicting_sources.append({
                    "title": source.get("title", ""),
                    "url": source.get("url", "")
                })
        
        confidence = "High" if len(supporting_sources) > len(contradicting_sources) else "Medium"
        if len(supporting_sources) == 0:
            confidence = "Low"
        
        return json.dumps({
            "claim": claim,
            "supporting_sources": supporting_sources,
            "contradicting_sources": contradicting_sources,
            "confidence": confidence,
            "assessment": f"Claim is {'supported' if confidence == 'High' else 'contested' if confidence == 'Medium' else 'not supported'} by available sources",
        })
        
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "claim": claim,
        })

# Research coordinator agent
research_coordinator = Agent(
    name="Research Coordinator",
    instructions=(
        "You coordinate research tasks using web search and source checking.\n"
        "Use search_web to gather information on research tasks.\n"
        "Use check_source_reliability to assess source credibility.\n"
        "Gather multiple perspectives on each research task.\n"
        "Look for conflicts between sources and note them.\n"
        "Prioritize recent sources when available.\n"
        "Return comprehensive research findings as structured JSON."
    ),
    tools=[search_web, source_checker],
    handoffs=[]
)

# Fact checker agent
fact_checker_agent = Agent(
    name="Fact Checker",
    instructions=(
        "You verify specific claims and facts using available sources.\n"
        "Use fact_check_claim to validate important statements.\n"
        "Provide confidence levels for each fact check.\n"
        "Note when sources contradict each other.\n"
        "Return structured fact-checking reports."
    ),
    tools=[fact_finder],
    handoffs=[]
)

# Source evaluator agent
source_evaluator_agent = Agent(
    name="Source Evaluator",
    instructions=(
        "You specialize in evaluating source quality and reliability.\n"
        "Use check_source_reliability to assess websites and publications.\n"
        "Consider factors like domain authority, publication date, and content type.\n"
        "Provide detailed reliability assessments for research sources.\n"
        "Return structured evaluation reports."
    ),
    tools=[source_checker],
    handoffs=[]
)