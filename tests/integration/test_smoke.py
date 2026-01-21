"""
Integration Smoke Test
Run this to verify the core pipeline works without OpenAI keys (using Mocks).
"""
import sys
import traceback
import asyncio
from app.core.models import Project, Signal, Requirement, SignalType, TestType
from app.ai.generator import create_generator

# Define a minimal valid project for testing
TEST_PROJECT = Project(
    project_id="SMOKE-TEST-001",
    system="Cooling System",
    environment="Test Env",
    signals=[
        Signal(id="T-01", type=SignalType.TEMPERATURE, range="0-100C"),
    ],
    requirements=[
        Requirement(id="REQ-01", text="Verify T-01 reads correctly.")
    ]
)

async def run_smoke_test():
    print("==================================================")
    print("🚀 STARTING PHASE 1 SMOKE TEST")
    print("==================================================")
    
    try:
        # 1. Initialize Mock Generator
        print("[INFO] Initializing Mock Generator...")
        generator = create_generator("mock")
        if not generator:
            raise ValueError("Factory returned None for 'mock' provider")

        # 2. Run Generation
        print("[INFO] Generating content...")
        
        # ------------------------------------------------------------------
        # FIX: Removed 'await'. The Mock generator is currently synchronous.
        # ------------------------------------------------------------------
        result = generator.generate(TEST_PROJECT, test_type=TestType.FAT)
        
        # 3. Verify Output Structure
        print("[INFO] Verifying output...")
        if "content" not in result:
            raise KeyError("Result missing 'content' key")
        
        if "metadata" not in result:
            raise KeyError("Result missing 'metadata' key")

        print("✅ SMOKE TEST PASSED")
        print("==================================================")
        return True

    except Exception as e:
        print("\n❌ SMOKE TEST FAILED")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        print("\n--- STACK TRACE ---")
        traceback.print_exc()
        print("-------------------")
        return False

if __name__ == "__main__":
    success = asyncio.run(run_smoke_test())
    if not success:
        sys.exit(1)