"""
Blockchain Integration Test Script
Tests the Base Sepolia connection and USDC contract interaction
"""
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_blockchain_connection():
    """Test 1: Check if we can connect to Base Sepolia"""
    print("=" * 60)
    print("TEST 1: Blockchain Connection")
    print("=" * 60)

    try:
        from app.blockchain import WEB3_PROVIDER, RPC_URL, USDC_CONTRACT_ADDRESS

        print(f"RPC URL: {RPC_URL}")
        print(f"USDC Contract: {USDC_CONTRACT_ADDRESS}")
        print(f"Connected: {WEB3_PROVIDER.is_connected()}")

        if WEB3_PROVIDER.is_connected():
            chain_id = WEB3_PROVIDER.eth.chain_id
            block_number = WEB3_PROVIDER.eth.block_number
            print(f"[OK] Successfully connected to Base Sepolia!")
            print(f"   Chain ID: {chain_id}")
            print(f"   Current Block: {block_number}")
            return True
        else:
            print("[FAIL] Failed to connect to Base Sepolia")
            return False
    except Exception as e:
        print(f"[FAIL] Connection test failed: {e}")
        return False

async def test_usdc_contract():
    """Test 2: Check USDC contract interaction"""
    print("\n" + "=" * 60)
    print("TEST 2: USDC Contract")
    print("=" * 60)

    try:
        from app.blockchain import WEB3_PROVIDER, get_usdc_contract, USDC_CONTRACT_ADDRESS

        usdc_contract = get_usdc_contract()
        print(f"USDC Contract Address: {USDC_CONTRACT_ADDRESS}")

        # Get decimals
        decimals = usdc_contract.functions.decimals().call()
        print(f"[OK] USDC Decimals: {decimals}")

        # Get symbol (if available)
        try:
            symbol = usdc_contract.functions.symbol().call()
            print(f"[OK] Token Symbol: {symbol}")
        except:
            print("[INFO] Symbol not available in ABI")

        # Check platform fee recipient balance
        from app.blockchain import PLATFORM_FEE_RECIPIENT_ADDRESS
        balance = usdc_contract.functions.balanceOf(
            WEB3_PROVIDER.to_checksum_address(PLATFORM_FEE_RECIPIENT_ADDRESS)
        ).call()
        balance_usdc = balance / (10 ** decimals)
        print(f"[OK] Platform Fee Recipient Balance: {balance_usdc} USDC")

        return True
    except Exception as e:
        print(f"[FAIL] USDC contract test failed: {e}")
        return False

async def test_environment_config():
    """Test 3: Check environment configuration"""
    print("\n" + "=" * 60)
    print("TEST 3: Environment Configuration")
    print("=" * 60)

    try:
        from app.blockchain import (
            RPC_URL,
            USDC_CONTRACT_ADDRESS,
            PLATFORM_FEE_RECIPIENT_ADDRESS,
            PLATFORM_PRIVATE_KEY
        )

        print(f"RPC URL: {'[OK] Set' if RPC_URL else '[FAIL] Missing'}")
        print(f"USDC Contract: {'[OK] Set' if USDC_CONTRACT_ADDRESS else '[FAIL] Missing'}")
        print(f"Platform Fee Recipient: {'[OK] Set' if PLATFORM_FEE_RECIPIENT_ADDRESS else '[FAIL] Missing'}")
        print(f"Platform Private Key: {'[OK] Set' if PLATFORM_PRIVATE_KEY else '[FAIL] Missing'}")

        # Check if private key format is valid
        if PLATFORM_PRIVATE_KEY:
            if PLATFORM_PRIVATE_KEY.startswith('0x') and len(PLATFORM_PRIVATE_KEY) == 66:
                print(f"[OK] Private key format is valid")
            else:
                print(f"[WARN] Warning: Private key format may be invalid")

        # Warning about test key
        if PLATFORM_PRIVATE_KEY == "0x0000000000000000000000000000000000000000000000000000000000000001":
            print("[WARN] WARNING: Using default test private key!")
            print("   This key has no real funds. Set PLATFORM_PRIVATE_KEY in .env")

        return True
    except Exception as e:
        print(f"[FAIL] Environment config test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("\nAgentTaskHub Blockchain Integration Tests\n")

    results = {
        "connection": await test_blockchain_connection(),
        "usdc_contract": await test_usdc_contract(),
        "environment": await test_environment_config(),
    }

    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    for test_name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{test_name.replace('_', ' ').title()}: {status}")

    all_passed = all(results.values())
    if all_passed:
        print("\n[SUCCESS] All tests passed!")
    else:
        print("\n[WARN] Some tests failed. Please check the configuration.")

    return all_passed

if __name__ == "__main__":
    asyncio.run(main())
