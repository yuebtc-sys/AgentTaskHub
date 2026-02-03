import os
from web3 import Web3
# removed: geth_poa_middleware (not required)
from dotenv import load_dotenv

load_dotenv() # 加载.env文件中的环境变量

# --- 配置 ---
# Base Sepolia Testnet RPC URL (替换为实际可用的RPC)
# 或者 Base Mainnet RPC URL
RPC_URL = os.getenv("RPC_URL", "https://sepolia.base.org") # 默认使用Base Sepolia
WEB3_PROVIDER = Web3(Web3.HTTPProvider(RPC_URL))

# 添加POA中间件，因为Base Sepolia是Geth PoA兼容的链
# removed: PoA middleware injection

# USDC 合约地址 (Base Sepolia Testnet)
# 请替换为实际使用的Base网络USDC合约地址，可以是测试网或主网
# 这是一个示例地址，请确保它是正确的USDC地址
USDC_CONTRACT_ADDRESS = os.getenv("USDC_CONTRACT_ADDRESS", "0x036CbD53842c54266f199321eB262e2f698d4f49") # Base Sepolia USDC (Example)

# 平台手续费接收钱包地址 (您的钱包地址)
# 这是平台收取1%手续费后转入的地址
PLATFORM_FEE_RECIPIENT_ADDRESS = os.getenv("PLATFORM_FEE_RECIPIENT_ADDRESS", "0x305656CfE21736330CD32A793817166AfaFff0CB")

# 平台私钥 (用于发起交易的钱包私钥，需要有ETH支付Gas费)
# **CRITICAL**: 生产环境中绝不能明文存储，应使用密钥管理服务
PLATFORM_PRIVATE_KEY = os.getenv("PLATFORM_PRIVATE_KEY")

if not PLATFORM_PRIVATE_KEY:
    raise ValueError("PLATFORM_PRIVATE_KEY environment variable not set.")

# --- USDC ABI (ERC-20标准简化版) ---
USDC_ABI = [
    {
        "constant": False,
        "inputs": [
            {"name": "_to", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_spender", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}, {"name": "_spender", "type": "address"}],
        "name": "allowance",
        "outputs": [{"name": "", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    }
]

# --- 区块链交互函数 ---
def get_usdc_contract():
    return WEB3_PROVIDER.eth.contract(address=USDC_CONTRACT_ADDRESS, abi=USDC_ABI)

async def transfer_usdc(sender_private_key: str, receiver_address: str, amount_usd: float, platform_fee_usd: float):
    if not WEB3_PROVIDER.is_connected():
        raise ConnectionError("Not connected to Web3 provider.")

    usdc_contract = get_usdc_contract()
    sender_account = WEB3_PROVIDER.eth.account.from_key(sender_private_key)
    
    # 获取USDC的decimals
    decimals = usdc_contract.functions.decimals().call()
    
    # 转换金额为合约所需的单位 (例如，USDC通常是6位小数)
    amount_wei = int(amount_usd * (10 ** decimals))
    platform_fee_wei = int(platform_fee_usd * (10 ** decimals))
    
    # 平台收取手续费
    if platform_fee_wei > 0:
        platform_fee_tx = usdc_contract.functions.transfer(
            WEB3_PROVIDER.to_checksum_address(PLATFORM_FEE_RECIPIENT_ADDRESS),
            platform_fee_wei
        ).build_transaction({
            'chainId': WEB3_PROVIDER.eth.chain_id,
            'gas': 200000, # 估算Gas limit
            'gasPrice': WEB3_PROVIDER.eth.gas_price,
            'nonce': WEB3_PROVIDER.eth.get_transaction_count(sender_account.address)
        })
        signed_platform_fee_tx = WEB3_PROVIDER.eth.account.sign_transaction(platform_fee_tx, private_key=sender_private_key)
        platform_fee_tx_hash = WEB3_PROVIDER.eth.send_raw_transaction(signed_platform_fee_tx.rawTransaction)
        print(f"Platform fee transaction sent: {platform_fee_tx_hash.hex()}")
        # 等待交易确认
        WEB3_PROVIDER.eth.wait_for_transaction_receipt(platform_fee_tx_hash)

    # 支付赏金给认领者
    bounty_tx = usdc_contract.functions.transfer(
        WEB3_PROVIDER.to_checksum_address(receiver_address),
        amount_wei
    ).build_transaction({
        'chainId': WEB3_PROVIDER.eth.chain_id,
        'gas': 200000, # 估算Gas limit
        'gasPrice': WEB3_PROVIDER.eth.gas_price,
        'nonce': WEB3_PROVIDER.eth.get_transaction_count(sender_account.address) + (1 if platform_fee_wei > 0 else 0) # Nonce需要递增
    })
    signed_bounty_tx = WEB3_PROVIDER.eth.account.sign_transaction(bounty_tx, private_key=sender_private_key)
    bounty_tx_hash = WEB3_PROVIDER.eth.send_raw_transaction(signed_bounty_tx.rawTransaction)
    print(f"Bounty transaction sent: {bounty_tx_hash.hex()}")
    # 等待交易确认
    WEB3_PROVIDER.eth.wait_for_transaction_receipt(bounty_tx_hash)

    return {"bounty_tx_hash": bounty_tx_hash.hex(), "platform_fee_tx_hash": platform_fee_tx_hash.hex() if platform_fee_wei > 0 else None}

async def get_usdc_balance(wallet_address: str) -> float:
    if not WEB3_PROVIDER.is_connected():
        raise ConnectionError("Not connected to Web3 provider.")
    usdc_contract = get_usdc_contract()
    decimals = usdc_contract.functions.decimals().call()
    balance_wei = usdc_contract.functions.balanceOf(WEB3_PROVIDER.to_checksum_address(wallet_address)).call()
    return balance_wei / (10 ** decimals)

async def approve_usdc(sender_private_key: str, spender_address: str, amount_usd: float):
    if not WEB3_PROVIDER.is_connected():
        raise ConnectionError("Not connected to Web3 provider.")
    
    usdc_contract = get_usdc_contract()
    sender_account = WEB3_PROVIDER.eth.account.from_key(sender_private_key)
    decimals = usdc_contract.functions.decimals().call()
    amount_wei = int(amount_usd * (10 ** decimals))

    tx = usdc_contract.functions.approve(
        WEB3_PROVIDER.to_checksum_address(spender_address),
        amount_wei
    ).build_transaction({
        'chainId': WEB3_PROVIDER.eth.chain_id,
        'gas': 100000, # 估算Gas limit
        'gasPrice': WEB3_PROVIDER.eth.gas_price,
        'nonce': WEB3_PROVIDER.eth.get_transaction_count(sender_account.address)
    })
    
    signed_tx = WEB3_PROVIDER.eth.account.sign_transaction(tx, private_key=sender_private_key)
    tx_hash = WEB3_PROVIDER.eth.send_raw_transaction(signed_tx.rawTransaction)
    print(f"Approval transaction sent: {tx_hash.hex()}")
    WEB3_PROVIDER.eth.wait_for_transaction_receipt(tx_hash)
    return tx_hash.hex()

if __name__ == "__main__":
    print("Blockchain module initialized.")
    # Add a simple test for connection if needed
    try:
        print(f"Connected to Base Sepolia: {WEB3_PROVIDER.is_connected()}")
        print(f"Current block number: {WEB3_PROVIDER.eth.block_number}")
    except Exception as e:
        print(f"Connection test failed: {e}")
