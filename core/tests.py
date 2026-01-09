from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model

class AIHubIntegrationTests(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.client.force_authenticate(user=self.user)

    def test_ai_connection_method_allowed(self):
        """
        Verify that AI connection test endpoint accepts POST and rejects GET.
        Fixes Q3: Method 'GET' not allowed.
        """
        url = reverse('ai-test-connection')
        
        # Test GET (should fail with 405)
        response_get = self.client.get(url)
        self.assertEqual(response_get.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
        # Test POST (should be allowed, might return 400 if config_id missing, but not 405)
        response_post = self.client.post(url, {}, format='json')
        self.assertNotEqual(response_post.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        # It usually returns 400 because config_id is required
        self.assertEqual(response_post.status_code, status.HTTP_400_BAD_REQUEST)

    def test_agent_route_payload_key(self):
        """
        Verify that Agent Route endpoint validates 'task' key.
        Fixes Q3: Task description is required.
        """
        url = reverse('agent-route')
        
        # Test with wrong key 'text' (should fail)
        response_wrong = self.client.post(url, {'text': 'Some task'}, format='json')
        self.assertEqual(response_wrong.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Task description is required', str(response_wrong.data))
        
        # Test with correct key 'task' (should succeed/process)
        response_correct = self.client.post(url, {'task': 'Some task'}, format='json')
        self.assertEqual(response_correct.status_code, status.HTTP_200_OK)
