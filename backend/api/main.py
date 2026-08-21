from fastapi import FastAPI

app = FastAPI(
    title="ResearchPilot AI",
    description="AI-powered research assistant",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "researchpilot",
    }