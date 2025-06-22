"""
FastAPI routes for Jupiter Smart Swap backend API.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import time

from backend.models.swap_request import SwapRequest, SwapMode, SelectionCriteria
from backend.models.swap_response import SwapResponse, HealthResponse
from backend.services.route_analyzer import RouteAnalyzer

router = APIRouter()

# Pydantic models for API requests
class AnalyzeRequest(BaseModel):
    input_mint: str
    output_mint: str
    amount: int
    slippage_bps: int = 50
    wrap_unwrap_sol: bool = True
    auto_select_criteria: str = "efficiency"
    demo_mode: bool = False

class AutoSwapRequest(BaseModel):
    input_mint: str
    output_mint: str
    amount: int
    slippage_bps: int = 50
    user_public_key: str
    wrap_unwrap_sol: bool = True
    auto_select_criteria: str = "efficiency"
    demo_mode: bool = False

class ManualSwapRequest(BaseModel):
    input_mint: str
    output_mint: str
    amount: int
    slippage_bps: int = 50
    wrap_unwrap_sol: bool = True
    auto_select_criteria: str = "efficiency"
    demo_mode: bool = False

@router.get("/health")
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=time.time(),
        version="1.0.0",
        jupiter_api_status="available"
    )

@router.post("/analyze")
async def analyze_routes(request: AnalyzeRequest) -> SwapResponse:
    """
    Analyze routes only - no swap execution.
    
    Args:
        request: Analysis request parameters
        
    Returns:
        Route analysis results
    """
    try:
        # Convert API request to internal model
        swap_request = SwapRequest(
            input_mint=request.input_mint,
            output_mint=request.output_mint,
            amount=request.amount,
            slippage_bps=request.slippage_bps,
            wrap_unwrap_sol=request.wrap_unwrap_sol,
            mode=SwapMode.ANALYZE_ONLY,
            auto_select_criteria=SelectionCriteria(request.auto_select_criteria)
        )
        
        # Create analyzer and process request
        analyzer = RouteAnalyzer(use_demo_mode=request.demo_mode)
        response = await analyzer.analyze_routes(swap_request)
        
        if not response.success:
            raise HTTPException(status_code=400, detail=response.error)
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/auto-swap")
async def auto_swap(request: AutoSwapRequest) -> SwapResponse:
    """
    Auto-select best route and execute swap.
    
    Args:
        request: Auto-swap request with user public key
        
    Returns:
        Swap execution results
    """
    try:
        # Convert API request to internal model
        swap_request = SwapRequest(
            input_mint=request.input_mint,
            output_mint=request.output_mint,
            amount=request.amount,
            slippage_bps=request.slippage_bps,
            user_public_key=request.user_public_key,
            wrap_unwrap_sol=request.wrap_unwrap_sol,
            mode=SwapMode.AUTO_SWAP,
            auto_select_criteria=SelectionCriteria(request.auto_select_criteria)
        )
        
        # Create analyzer and process request
        analyzer = RouteAnalyzer(use_demo_mode=request.demo_mode)
        response = await analyzer.analyze_routes(swap_request)
        
        if not response.success:
            raise HTTPException(status_code=400, detail=response.error)
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/manual-swap")
async def manual_swap(request: ManualSwapRequest) -> SwapResponse:
    """
    Get route analysis for manual selection.
    
    Args:
        request: Manual swap request parameters
        
    Returns:
        Route analysis for manual selection
    """
    try:
        # Convert API request to internal model
        swap_request = SwapRequest(
            input_mint=request.input_mint,
            output_mint=request.output_mint,
            amount=request.amount,
            slippage_bps=request.slippage_bps,
            wrap_unwrap_sol=request.wrap_unwrap_sol,
            mode=SwapMode.MANUAL_MODE,
            auto_select_criteria=SelectionCriteria(request.auto_select_criteria)
        )
        
        # Create analyzer and process request
        analyzer = RouteAnalyzer(use_demo_mode=request.demo_mode)
        response = await analyzer.analyze_routes(swap_request)
        
        if not response.success:
            raise HTTPException(status_code=400, detail=response.error)
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/demo")
async def demo_endpoints():
    """Return demo examples for all endpoints."""
    return {
        "message": "Jupiter Smart Swap API Demo",
        "endpoints": {
            "analyze": {
                "url": "/analyze",
                "method": "POST",
                "example": {
                    "input_mint": "So11111111111111111111111111111111111111112",
                    "output_mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
                    "amount": 1000000,
                    "demo_mode": True
                }
            },
            "auto_swap": {
                "url": "/auto-swap", 
                "method": "POST",
                "example": {
                    "input_mint": "So11111111111111111111111111111111111111112",
                    "output_mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
                    "amount": 1000000,
                    "user_public_key": "demo_public_key_123",
                    "demo_mode": True
                }
            },
            "manual_swap": {
                "url": "/manual-swap",
                "method": "POST", 
                "example": {
                    "input_mint": "So11111111111111111111111111111111111111112",
                    "output_mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
                    "amount": 1000000,
                    "demo_mode": True
                }
            }
        }
    } 