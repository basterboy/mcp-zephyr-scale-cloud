#!/usr/bin/env python3
"""Debug script to test folder update functionality."""

import asyncio
import json
import os
from datetime import datetime

import httpx
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our schemas and client
from src.mcp_zephyr_scale_cloud.clients.zephyr_client import ZephyrClient
from src.mcp_zephyr_scale_cloud.config import ZephyrConfig
from src.mcp_zephyr_scale_cloud.schemas.test_case import TestCaseUpdateInput


async def debug_folder_update():
    """Debug the folder update process."""
    
    # Set up client - load config from environment
    api_token = os.getenv("ZEPHYR_SCALE_API_TOKEN")
    base_url = os.getenv("ZEPHYR_SCALE_BASE_URL", "https://api.zephyrscale.smartbear.com/v2")
    
    if not api_token:
        print("❌ ZEPHYR_SCALE_API_TOKEN environment variable not set!")
        return
    
    config = ZephyrConfig(api_token=api_token, base_url=base_url)
    client = ZephyrClient(config)
    
    test_case_key = "RGM-T1882"
    folder_id = 24718271
    
    print(f"🔍 Debugging folder update for {test_case_key} to folder {folder_id}")
    print("=" * 60)
    
    # Step 1: Get current test case
    print("\n1. Getting current test case...")
    current_result = await client.get_test_case(test_case_key)
    if not current_result.is_valid:
        print(f"❌ Failed to get test case: {current_result.errors}")
        return
    
    current_data = current_result.data
    print(f"✅ Current test case retrieved")
    print(f"   - Name: {current_data.name}")
    print(f"   - Current folder: {getattr(current_data, 'folder', 'None (root level)')}")
    
    # Step 2: Create update input with FOLDER OBJECT (not folderId)
    print(f"\n2. Creating update input with folder object for ID {folder_id}")
    
    # Test 1: Using folderId (what we were doing - WRONG)
    update_input_wrong = TestCaseUpdateInput(folder_id=folder_id)
    update_data_wrong = update_input_wrong.model_dump(by_alias=True, exclude_none=True)
    print(f"   - Wrong format (folderId): {json.dumps(update_data_wrong, indent=2)}")
    
    # Test 2: Manual folder object (what we should do - CORRECT)
    folder_object = {
        "id": folder_id,
        "self": f"{config.base_url}/folders/{folder_id}"
    }
    update_data_correct = {"folder": folder_object}
    print(f"   - Correct format (folder object): {json.dumps(update_data_correct, indent=2)}")
    
    # We'll test the correct format
    update_data = update_data_correct
    
    # Step 3: Build request data (simulate what our client does)
    print(f"\n3. Building request data...")
    request_data = current_data.model_dump(by_alias=True, exclude_none=True, mode='json')
    print(f"   - Current data keys: {list(request_data.keys())}")
    print(f"   - Current folder in data: {request_data.get('folder', 'NOT PRESENT')}")
    
    # Apply updates
    request_data.update(update_data)
    print(f"   - After update, folder in data: {request_data.get('folderId', 'NOT PRESENT')}")
    print(f"   - Final request data keys: {list(request_data.keys())}")
    
    # Step 4: Show what we're sending to API
    print(f"\n4. Request data that will be sent to API:")
    print(json.dumps(request_data, indent=2))
    
    # Step 5: Make the actual API call with detailed logging
    print(f"\n5. Making API call to update test case...")
    
    async with httpx.AsyncClient() as http_client:
        url = f"{config.base_url}/testcases/{test_case_key}"
        headers = {
            "Authorization": f"Bearer {config.api_token}",
            "Content-Type": "application/json",
        }
        
        print(f"   - URL: {url}")
        print(f"   - Headers: {dict(headers)}")
        print(f"   - Method: PUT")
        
        try:
            response = await http_client.put(
                url,
                headers=headers,
                json=request_data,
                timeout=10.0,
            )
            
            print(f"   - Response status: {response.status_code}")
            print(f"   - Response headers: {dict(response.headers)}")
            
            if response.text:
                print(f"   - Response body: {response.text}")
            else:
                print(f"   - Response body: (empty)")
                
            response.raise_for_status()
            print("✅ API call succeeded")
            
        except Exception as e:
            print(f"❌ API call failed: {e}")
            return
    
    # Step 6: Verify the update worked
    print(f"\n6. Verifying update...")
    await asyncio.sleep(1)  # Give API time to process
    
    updated_result = await client.get_test_case(test_case_key)
    if updated_result.is_valid:
        updated_data = updated_result.data
        print(f"✅ Retrieved updated test case")
        print(f"   - Name: {updated_data.name}")
        print(f"   - Updated folder: {getattr(updated_data, 'folder', 'None (root level)')}")
        
        if hasattr(updated_data, 'folder') and updated_data.folder:
            print(f"   - Folder ID: {updated_data.folder.id}")
            if updated_data.folder.id == folder_id:
                print("🎉 SUCCESS: Folder was updated correctly!")
            else:
                print(f"❌ FAILED: Expected folder {folder_id}, got {updated_data.folder.id}")
        else:
            print("❌ FAILED: Test case still has no folder assigned")
    else:
        print(f"❌ Failed to verify update: {updated_result.errors}")


if __name__ == "__main__":
    asyncio.run(debug_folder_update())
