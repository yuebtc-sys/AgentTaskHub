import requests
import json

BASE_URL = "http://127.0.0.1:8001"

def test_register_agent():
    print("--- Testing Agent Registration (POST /agents/) ---")
    agent_data = {"name": "TestAgent", "email": "test@example.com"}
    response = requests.post(f"{BASE_URL}/agents/", json=agent_data)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        agent_info = response.json()
        print(f"Registered Agent ID: {agent_info['id']}")
        print(f"Agent API Key: {agent_info['api_key']}")
        return agent_info['api_key']
    elif response.status_code == 400 and "Agent name already registered" in response.json().get("detail", ""):
        print("Agent already registered. Skipping registration.")
        # Attempt to retrieve existing agent's API key (this would need a specific endpoint or manual lookup for a real scenario)
        # For this test, we'll assume we can't easily retrieve the API key if already registered.
        return None 
    else:
        return None

def test_get_my_agent_profile(api_key):
    if not api_key:
        print("Cannot get agent profile without API key.")
        return
    print("\n--- Testing Get Agent Profile (GET /agents/me/) ---")
    headers = {"X-API-Key": api_key}
    response = requests.get(f"{BASE_URL}/agents/me/", headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_create_task(api_key):
    if not api_key:
        print("Cannot create task without API key.")
        return
    print("\n--- Testing Task Creation (POST /tasks/) ---")
    task_data = {
        "title": "Test Task 1",
        "description": "This is a description for Test Task 1.",
        "amount": 100.0
    }
    headers = {"X-API-Key": api_key}
    response = requests.post(f"{BASE_URL}/tasks/", json=task_data, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_read_tasks():
    print("\n--- Testing Read Tasks (GET /tasks/) ---")
    response = requests.get(f"{BASE_URL}/tasks/")
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    agent_api_key = test_register_agent()
    
    if agent_api_key:
        test_get_my_agent_profile(agent_api_key)
        test_create_task(agent_api_key)
    else:
        print("\nSkipping further agent/task tests as agent registration failed or was skipped.")
    
    test_read_tasks()
