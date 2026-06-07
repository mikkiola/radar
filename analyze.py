import requests
import os
from datetime import date

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
VAULT_PATH = os.path.expanduser("~/radar/01_Assessments")

def analyze_and_save(projects):
    today = date.today().strftime("%Y-%m-%d")
    
    for p in projects[:5]:
        title = p.get("title", "")
        desc = p.get("description", "")
        url = p.get("url", "")
        
        prompt = f"""You are a measurement tool for the AI and agent market.

Analyze this opensource project and fill in the assessment in the exact format below.

Project: {title}
Description: {desc}
URL: {url}

Reply STRICTLY in this format:
ASSESSMENT: SHIFT or NOISE
CONFIDENCE: high or medium or low
WHAT_CHANGES: [2-3 sentences - what specifically changes in the ecosystem structure]
ARGUMENT: [1-2 sentences why this assessment]
CRITERION: [one concrete observable event in one year that will confirm or refute the assessment]"""

        try:
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": "claude-haiku-4-5-20251001",
                    "max_tokens": 500,
                    "messages": [{"role": "user", "content": prompt}]
                },
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"   API error for {title}: {response.status_code}")
                continue
                
            text = response.json()["content"][0]["text"]
            
            lines = {}
            for line in text.strip().split("\n"):
                if ": " in line:
                    key, val = line.split(": ", 1)
                    lines[key.strip()] = val.strip()
            
            assessment = lines.get("ASSESSMENT", "NOISE")
            confidence = lines.get("CONFIDENCE", "low")
            what = lines.get("WHAT_CHANGES", "")
            arg = lines.get("ARGUMENT", "")
            criterion = lines.get("CRITERION", "")
            
            safe_title = title.replace("/", "-").replace(" ", "_")[:50]
            filename = f"{today} {safe_title}.md"
            filepath = os.path.join(VAULT_PATH, filename)
            
            content = f"""# Assessment: {title}

**Date:** {today}
**Repository:** {url}
**Assessment:** {assessment}
**Confidence:** {confidence}

## What changes in the ecosystem
{what}

## Argument
{arg}

## Revision criterion
I will change this assessment if: {criterion}

## Assessment history
- {today} - {assessment}: first assessment

## Links
"""
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            
            print(f"   {assessment} - {title}")
            
        except Exception as e:
            print(f"   Error {title}: {e}")

if __name__ == "__main__":
    test_projects = [
        {"title": "github/github-mcp-server", "description": "GitHub's official MCP Server", "url": "https://github.com/github/github-mcp-server"},
        {"title": "browser-use/browser-use", "description": "Make websites accessible for AI agents", "url": "https://github.com/browser-use/browser-use"},
        {"title": "n8n-io/n8n", "description": "Fair-code workflow automation platform with native AI capabilities", "url": "https://github.com/n8n-io/n8n"},
    ]
    print("Analyzing and saving to vault...")
    analyze_and_save(test_projects)
    print("\nDone. Check 01_Assessments in Obsidian.")
