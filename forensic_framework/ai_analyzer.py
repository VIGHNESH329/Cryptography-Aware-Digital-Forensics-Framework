import json

def analyze_evidence_ai(filename, metadata_json, data_sample=""):
    """
    Simulates a Claude-based AI forensic analysis.
    In a real scenario, this would call the Anthropic API.
    """
    metadata = json.loads(metadata_json)
    
    analysis = {
        "summary": f"AI analysis of {filename} completed.",
        "risk_level": "Low",
        "findings": [],
        "recommendations": []
    }

    # Simulation logic
    if metadata.get('Error'):
        analysis["risk_level"] = "High"
        analysis["findings"].append("File metadata extraction failed. Potential obfuscation.")
    
    if "GPS GPSLatitude" in metadata:
        analysis["findings"].append(f"Geographic data found: {metadata['GPS GPSLatitude']}, {metadata['GPS GPSLongitude']}")
    
    if "Author" in metadata and "admin" in metadata["Author"].lower():
        analysis["findings"].append("File authored by high-privileged account (Admin).")

    # Keywords in filename
    suspicious_keywords = ['hack', 'password', 'exploit', 'shadow', 'unauthorized', 'malware']
    if any(kw in filename.lower() for kw in suspicious_keywords):
        analysis["risk_level"] = "High"
        analysis["findings"].append(f"Suspicious keyword detected in filename.")
        analysis["recommendations"].append("Perform deep packet inspection if this is a log or traffic dump.")

    if ".exe" in filename.lower() or ".bat" in filename.lower() or ".sh" in filename.lower():
        analysis["risk_level"] = "Critical"
        analysis["findings"].append("Executable/Script file detected in evidence vault.")
        analysis["recommendations"].append("Sandbox execution and registry monitoring.")

    if "XMP:Creator" in metadata and "Deep Web" in str(metadata["XMP:Creator"]):
        analysis["risk_level"] = "Critical"
        analysis["findings"].append("Evidence linked to flagged creative source: 'Deep Web'.")

    if not analysis["findings"]:
        analysis["findings"].append("No suspicious patterns detected in metadata or file headers.")
        analysis["recommendations"].append("Proceed with standard chain of custody.")

    return analysis
