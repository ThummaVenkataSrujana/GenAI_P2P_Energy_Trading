import unittest
import json
from app import app, load_data, DATA_FILE

class GreenGridAppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_01_login_redirect_and_authentication(self):
        # Unauthenticated access to dashboard should redirect to login
        res = self.client.get('/dashboard')
        self.assertEqual(res.status_code, 302)
        self.assertIn('/login', res.headers['Location'])

        # Invalid login
        res = self.client.post('/login', data={'username': 'srujana', 'password': 'wrongpassword'})
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Invalid username or password', res.data)

        # Successful login
        res = self.client.post('/login', data={'username': 'srujana', 'password': '12345'}, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Welcome, Srujana', res.data)

    def test_02_all_routes_authenticated(self):
        # Login session
        with self.client as c:
            with c.session_transaction() as sess:
                sess['user'] = {'username': 'srujana', 'name': 'Srujana', 'houseNumber': '101'}

            routes = ['/dashboard', '/members', '/microgrid', '/profile', '/trading', '/transactions', '/notifications']
            for route in routes:
                res = c.get(route)
                self.assertEqual(res.status_code, 200, f"Route {route} failed with status {res.status_code}")

    def test_03_p2p_buy_energy_api(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess['user'] = {'username': 'srujana', 'name': 'Srujana', 'houseNumber': '101'}

            # Initial data state
            data = load_data()
            pranavi_before = next(m for m in data['members'] if m['username'] == 'pranavi')['availableEnergy']
            wallet_before = data['currentUser']['walletBalance']

            # Execute purchase of 5 kWh from Pranavi (@ ₹9/kWh = ₹45 total)
            payload = {'seller': 'pranavi', 'quantity': 5}
            res = c.post('/api/buy', data=json.dumps(payload), content_type='application/json')
            self.assertEqual(res.status_code, 200)
            res_data = json.loads(res.data)
            self.assertTrue(res_data['success'])

            # Verify mutated data state
            data_after = load_data()
            pranavi_after = next(m for m in data_after['members'] if m['username'] == 'pranavi')['availableEnergy']
            wallet_after = data_after['currentUser']['walletBalance']

            self.assertEqual(pranavi_after, round(pranavi_before - 5, 2))
            self.assertEqual(wallet_after, round(wallet_before - 45, 2))
            self.assertEqual(data_after['transactions'][0]['seller'], 'Pranavi (House 106)')
            self.assertEqual(data_after['transactions'][0]['energy'], 5.0)

    def test_04_logout(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess['user'] = {'username': 'srujana', 'name': 'Srujana', 'houseNumber': '101'}
            res = c.get('/logout')
            self.assertEqual(res.status_code, 302)
            self.assertIn('/login', res.headers['Location'])

    def test_05_chatbot_api(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess['user'] = {'username': 'srujana', 'name': 'Srujana', 'houseNumber': '101'}

            # Known query
            res = c.post('/api/chat', data=json.dumps({'message': 'Who offers cheapest energy?'}), content_type='application/json')
            self.assertEqual(res.status_code, 200)
            data = json.loads(res.data)
            self.assertIn('Pranavi', data['response'])
            self.assertFalse(data['isFallback'])

            # Unknown query -> Fallback contact support number
            res = c.post('/api/chat', data=json.dumps({'message': 'What is quantum physics?'}), content_type='application/json')
            self.assertEqual(res.status_code, 200)
            data = json.loads(res.data)
            self.assertIn('+91 98765 43210', data['response'])
            self.assertTrue(data['isFallback'])

    def test_06_chatbot_device_and_member_queries(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess['user'] = {'username': 'srujana', 'name': 'Srujana', 'houseNumber': '101'}

            # Device power usage query
            res = c.post('/api/chat', data=json.dumps({'message': 'Which device is using most power in my house?'}), content_type='application/json')
            self.assertEqual(res.status_code, 200)
            data = json.loads(res.data)
            self.assertIn('HVAC / Central Air Conditioner', data['response'])
            self.assertIn('5.8 kWh/day', data['response'])

            # Individual member lookup query
            res = c.post('/api/chat', data=json.dumps({'message': 'Tell me about Bhumi'}), content_type='application/json')
            self.assertEqual(res.status_code, 200)
            data = json.loads(res.data)
            self.assertIn('House 102', data['response'])
            self.assertIn('Bhumi', data['response'])

            # Consumption metrics query
            res = c.post('/api/chat', data=json.dumps({'message': 'What are my consumption details?'}), content_type='application/json')
            self.assertEqual(res.status_code, 200)
            data = json.loads(res.data)
            self.assertIn('Today\'s Consumption', data['response'])

    def test_07_helpdesk_ticket_workflow(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess['user'] = {'username': 'srujana', 'name': 'Srujana', 'houseNumber': '101'}

            # Create ticket via Chatbot Helpdesk
            res = c.post('/api/chat', data=json.dumps({'message': 'Open ticket for smart meter sync issue'}), content_type='application/json')
            self.assertEqual(res.status_code, 200)
            data = json.loads(res.data)
            self.assertIn('Helpdesk Support Ticket Created!', data['response'])
            self.assertIn('TICKET-', data['response'])
            self.assertIn('+91 98765 43210', data['response'])

            # Check ticket status via Chatbot Helpdesk
            res = c.post('/api/chat', data=json.dumps({'message': 'Check my ticket status'}), content_type='application/json')
            self.assertEqual(res.status_code, 200)
            data = json.loads(res.data)
            self.assertIn('Active Helpdesk Support Tickets', data['response'])
            self.assertIn('Status: In Progress', data['response'])

    def test_08_chatbot_greetings(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess['user'] = {'username': 'srujana', 'name': 'Srujana', 'houseNumber': '101'}

            # Test "hii" greeting
            res = c.post('/api/chat', data=json.dumps({'message': 'hii'}), content_type='application/json')
            self.assertEqual(res.status_code, 200)
            data = json.loads(res.data)
            self.assertIn('Welcome to the GreenGrid 24/7 AI Helpdesk', data['response'])
            self.assertFalse(data['isFallback'])

if __name__ == '__main__':
    unittest.main()
