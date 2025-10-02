"""
Analysis Router for direct analysis execution and status tracking
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Path
from models.api_schemas import (
    AnalysisExecuteRequest,
    AnalysisExecuteResponse,
    AnalysisGetResponse,
    ErrorResponse
)

# Router setup
router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.post("/execute", response_model=AnalysisExecuteResponse)
async def execute_analysis(request: AnalysisExecuteRequest):
    """
    Execute analysis directly with provided parameters
    Immediately queues the analysis for background processing
    """
    try:
        # Import here to avoid circular imports
        from services.analysis_service import analysis_service
        from websocket_manager import websocket_manager
        
        # Validate parameters
        _validate_analysis_parameters(request.parameters)
        
        # Create analysis task
        analysis_id = await analysis_service.create_analysis(
            query_text=request.query_text,
            parameters=request.parameters,
            session_id=request.session_id
        )
        
        # Start background processing immediately
        success = await analysis_service.start_analysis(analysis_id, websocket_manager)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to start analysis processing"
            )
        
        # Create WebSocket session for this analysis
        websocket_session = f"ws_{analysis_id}"
        websocket_manager.register_analysis(websocket_session, analysis_id)
        
        return AnalysisExecuteResponse(
            success=True,
            analysis_id=analysis_id,
            status="processing",
            estimated_completion=datetime.utcnow() + timedelta(minutes=5),
            websocket_session=websocket_session,
            created_at=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to execute analysis: {str(e)}"
        )


@router.get("/{analysis_id}", response_model=AnalysisGetResponse)
async def get_analysis(
    analysis_id: str = Path(..., description="Analysis ID to retrieve")
):
    """
    Get analysis status and results
    Returns processing status, progress, or completed results
    """
    try:
        # Import here to avoid circular imports
        from services.analysis_service import analysis_service
        
        # Get analysis status
        status_data = await analysis_service.get_analysis_status(analysis_id)
        
        if not status_data:
            raise HTTPException(
                status_code=404,
                detail="Analysis not found"
            )
        
        # Format response based on status
        response_data = {
            "success": True,
            "analysis_id": analysis_id,
            "status": status_data["status"]
        }
        
        if status_data["status"] == "processing":
            response_data.update({
                "progress": status_data.get("progress"),
                "estimated_completion": status_data.get("estimated_completion")
            })
        elif status_data["status"] == "completed":
            response_data.update({
                "query": status_data.get("query"),
                "results": status_data.get("results")
            })
        elif status_data["status"] == "failed":
            response_data.update({
                "error": status_data.get("error")
            })
        
        return AnalysisGetResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get analysis status: {str(e)}"
        )


def _validate_analysis_parameters(parameters: Dict[str, Any]) -> None:
    """
    Validate analysis parameters
    Raises HTTPException if invalid
    """
    
    # Validate countries
    if "countries" in parameters:
        countries = parameters["countries"]
        if not isinstance(countries, list):
            raise HTTPException(
                status_code=400,
                detail="Countries must be a list"
            )
        
        if len(countries) == 0:
            raise HTTPException(
                status_code=400,
                detail="At least one country must be specified"
            )
        
        if len(countries) > 10:
            raise HTTPException(
                status_code=400,
                detail="Maximum 10 countries allowed"
            )
        
        # Validate country names
        valid_countries = {
            "united states", "usa", "us", "america",
            "iran", "israel", "china", "russia", "germany", "france",
            "united kingdom", "uk", "britain", "japan", "india",
            "turkey", "egypt", "saudi arabia", "iraq", "syria",
            "lebanon", "jordan", "uae", "qatar", "kuwait"
        }
        
        for country in countries:
            if not isinstance(country, str):
                raise HTTPException(
                    status_code=400,
                    detail="Country names must be strings"
                )
            
            if country.lower().strip() not in valid_countries:
                # Don't fail hard on unknown countries, just warn
                print(f"⚠️ Unknown country: {country}")
    
    # Validate timeframe
    if "days" in parameters:
        days = parameters["days"]
        if not isinstance(days, int) or days < 1 or days > 30:
            raise HTTPException(
                status_code=400,
                detail="Days must be an integer between 1 and 30"
            )
    
    # Validate results per country
    if "results_per_country" in parameters:
        results_per_country = parameters["results_per_country"]
        if not isinstance(results_per_country, int) or results_per_country < 1 or results_per_country > 50:
            raise HTTPException(
                status_code=400,
                detail="Results per country must be an integer between 1 and 50"
            )
    
    # Validate include_bias_analysis
    if "include_bias_analysis" in parameters:
        include_bias = parameters["include_bias_analysis"]
        if not isinstance(include_bias, bool):
            raise HTTPException(
                status_code=400,
                detail="include_bias_analysis must be a boolean"
            )


@router.get("/", response_model=Dict[str, Any])
async def list_analyses():
    """
    List recent analyses (for debugging/admin purposes)
    In production, this would be paginated and filtered by user
    """
    try:
        # Import here to avoid circular imports
        from services.analysis_service import analysis_service
        
        # Get all current tasks (in a real implementation, this would be filtered and paginated)
        analyses = []
        for analysis_id, task in analysis_service.tasks.items():
            analyses.append({
                "analysis_id": analysis_id,
                "status": task.status,
                "query_text": task.query_text,
                "created_at": task.created_at,
                "session_id": task.session_id
            })
        
        # Sort by creation time (newest first)
        analyses.sort(key=lambda x: x["created_at"], reverse=True)
        
        return {
            "success": True,
            "total_analyses": len(analyses),
            "analyses": analyses[:20]  # Limit to 20 most recent
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list analyses: {str(e)}"
        )


@router.delete("/{analysis_id}")
async def cancel_analysis(
    analysis_id: str = Path(..., description="Analysis ID to cancel")
):
    """
    Cancel a running analysis
    """
    try:
        # Import here to avoid circular imports
        from services.analysis_service import analysis_service
        
        if analysis_id not in analysis_service.tasks:
            raise HTTPException(
                status_code=404,
                detail="Analysis not found"
            )
        
        task = analysis_service.tasks[analysis_id]
        
        if task.status != "processing":
            raise HTTPException(
                status_code=400,
                detail=f"Cannot cancel analysis with status: {task.status}"
            )
        
        # Cancel the asyncio task
        if task.task and not task.task.done():
            task.task.cancel()
        
        # Update status
        task.status = "cancelled"
        task.error = {
            "code": "ANALYSIS_CANCELLED",
            "message": "Analysis was cancelled by user",
            "recoverable": False
        }
        
        print(f"🛑 Cancelled analysis: {analysis_id}")
        
        return {
            "success": True,
            "message": "Analysis cancelled successfully",
            "analysis_id": analysis_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cancel analysis: {str(e)}"
        )


if __name__ == "__main__":
    # Test analysis router functionality
    print("🧪 Testing Analysis Router...")
    
    # Test parameter validation
    try:
        _validate_analysis_parameters({
            "countries": ["United States", "Iran"],
            "days": 7,
            "results_per_country": 20,
            "include_bias_analysis": True
        })
        print("✅ Valid parameters passed validation")
    except Exception as e:
        print(f"❌ Validation failed: {e}")
    
    # Test invalid parameters
    try:
        _validate_analysis_parameters({
            "countries": [],  # Empty list should fail
            "days": 50  # Too many days should fail
        })
        print("❌ Invalid parameters should have failed")
    except Exception as e:
        print("✅ Invalid parameters correctly rejected")
    
    print("✅ Analysis router test completed!")
