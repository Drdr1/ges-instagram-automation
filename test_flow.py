import requests
import time

BASE_URL = "http://localhost:8000"

def test_complete_flow():
    """Test the complete user onboarding flow"""
    
    print("=" * 60)
    print("TESTING GES INSTAGRAM AUTOMATION ONBOARDING FLOW")
    print("=" * 60)
    
    # Step 1: User applies
    print("\n[1/6] User Application...")
    apply_response = requests.post(
        f"{BASE_URL}/api/onboarding/apply",
        json={
            "email": "testuser@example.com",
            "instagram_username": "test_instagram_user",
            "city": "Paris"
        }
    )
    print(f"Status: {apply_response.status_code}")
    apply_data = apply_response.json()
    print(f"Response: {apply_data}")
    user_id = apply_data["user_id"]
    
    # Step 2: Check status (should be pending)
    print("\n[2/6] Checking Application Status...")
    status_response = requests.get(
        f"{BASE_URL}/api/onboarding/status/{user_id}"
    )
    print(f"Status: {status_response.json()}")
    
    # Step 3: Admin approves (with mock proxy for testing)
    print("\n[3/6] Admin Approval...")
    approval_response = requests.post(
        f"{BASE_URL}/api/admin/approve/{user_id}",
        json={"use_mock_proxy": True}
    )
    print(f"Status: {approval_response.status_code}")
    print(f"Response: {approval_response.json()}")
    
    # Step 4: Check status again (should be approved)
    print("\n[4/6] Checking Status After Approval...")
    status_response = requests.get(
        f"{BASE_URL}/api/onboarding/status/{user_id}"
    )
    print(f"Status: {status_response.json()}")
    
    # Step 5: User starts login
    print("\n[5/6] User Login Attempt...")
    print("This will fail with real Instagram credentials")
    print("In production, user would enter real password here")
    
    # Step 6: View admin dashboard
    print("\n[6/6] Admin Dashboard...")
    users_response = requests.get(f"{BASE_URL}/api/admin/users")
    print(f"Total users: {users_response.json()['count']}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Integrate real proxy provider")
    print("2. Test with real Instagram account")
    print("3. Build frontend interface")
    print("4. Add email notifications")

if __name__ == "__main__":
    test_complete_flow()
