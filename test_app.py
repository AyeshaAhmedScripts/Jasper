import unittest
import json
import os
from app import app, save_profiles, load_profiles

class SurvivorProfileSystemTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.sample_profile = {
            "name": "Test User",
            "role": "Scout",
            "skills": "Tracking, Hunting",
            "location": "Camp A",
            "status": "Alive",
            "age": "25",
            "contact": "1234",
            "emergency": "Channel 5",
            "description": "Quick, silent, and efficient.",
            "priority": "High"
        }
        save_profiles([])  # Reset profiles.json

    def tearDown(self):
        save_profiles([])

    def test_add_profile(self):
        response = self.client.post("/add-profile", data=self.sample_profile, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        data = self.client.get("/profiles").get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Test User")
        self.assertIn("Tracking", data[0]["skills"])
        self.assertEqual(data[0]["description"], "Quick, silent, and efficient.")
        self.assertEqual(data[0]["priority"], "High")

    def test_duplicate_name(self):
        self.client.post("/add-profile", data=self.sample_profile)
        response = self.client.post("/add-profile", data=self.sample_profile)
        self.assertIn(b"Name already exists!", response.data)

    def test_edit_profile_get(self):
        self.client.post("/add-profile", data=self.sample_profile)
        response = self.client.get("/edit-profile/Test%20User")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Edit Survivor Profile", response.data)

    def test_edit_profile_post(self):
        self.client.post("/add-profile", data=self.sample_profile)
        edit_data = self.sample_profile.copy()
        edit_data["role"] = "Medic"
        edit_data["skills"] = "First Aid"
        edit_data["priority"] = "Critical"
        response = self.client.post("/edit-profile/Test%20User", data=edit_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        updated = self.client.get("/profiles").get_json()[0]
        self.assertEqual(updated["role"], "Medic")
        self.assertIn("First Aid", updated["skills"])
        self.assertEqual(updated["priority"], "Critical")

    def test_delete_profile(self):
        self.client.post("/add-profile", data=self.sample_profile)
        response = self.client.post("/delete-profile/Test%20User")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(len(load_profiles()), 0)

    def test_search_filter(self):
        self.client.post("/add-profile", data=self.sample_profile)
        response = self.client.get("/search?query=Test&role=Scout&location=Camp%20A&status=Alive")
        self.assertIn(b"Test User", response.data)

    def test_dashboard_counts(self):
        profile1 = self.sample_profile.copy()
        profile2 = self.sample_profile.copy()
        profile2["name"] = "Injured Survivor"
        profile2["status"] = "Injured"
        profile2["priority"] = "Low"

        save_profiles([{
            "name": profile1["name"],
            "role": profile1["role"],
            "skills": ["Tracking", "Hunting"],
            "location": profile1["location"],
            "status": profile1["status"],
            "age": profile1["age"],
            "contact": profile1["contact"],
            "emergency": profile1["emergency"],
            "description": profile1["description"],
            "priority": profile1["priority"]
        }, {
            "name": profile2["name"],
            "role": profile2["role"],
            "skills": ["Healing"],
            "location": profile2["location"],
            "status": profile2["status"],
            "age": profile2["age"],
            "contact": profile2["contact"],
            "emergency": profile2["emergency"],
            "description": "Injured and needs medical attention.",
            "priority": profile2["priority"]
        }])

        response = self.client.get("/dashboard")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Total Survivors: <strong>2</strong>", response.data)
        self.assertIn(b"Alive: <strong>1</strong>", response.data)
        self.assertIn(b"Injured: <strong>1</strong>", response.data)

    def test_profile_details(self):
        self.client.post("/add-profile", data=self.sample_profile)
        response = self.client.get("/profile-details/Test%20User")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Test User's Profile", response.data)
        self.assertIn(b"Quick, silent, and efficient.", response.data)

    def test_profile_details_not_found(self):
        response = self.client.get("/profile-details/UnknownUser", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Profile not found.", response.data)

if __name__ == '__main__':
    unittest.main()
