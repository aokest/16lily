from django.test import TestCase
from core.models import Customer
from django.contrib.auth.models import User
import datetime

class CustomerCodeGenerationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')

    def test_customer_code_generation(self):
        # Create a customer without code
        customer1 = Customer.objects.create(name="Test Customer 1", owner=self.user)
        
        # Check if code is generated
        self.assertTrue(customer1.customer_code.startswith("CUST-"))
        
        # Check format CUST-YYYYMM-SEQ
        now = datetime.datetime.now()
        expected_prefix = f"CUST-{now.strftime('%Y%m')}"
        self.assertTrue(customer1.customer_code.startswith(expected_prefix))
        
        # Check sequence
        customer2 = Customer.objects.create(name="Test Customer 2", owner=self.user)
        self.assertNotEqual(customer1.customer_code, customer2.customer_code)
        
        # Parse sequence
        seq1 = int(customer1.customer_code.split('-')[-1])
        seq2 = int(customer2.customer_code.split('-')[-1])
        self.assertEqual(seq2, seq1 + 1)
