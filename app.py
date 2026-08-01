import os
import json
import socket
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

app = Flask(__name__)
app.secret_key = 'greengrid_ai_p2p_hyperlocal_secret_key_2026'

DATA_FILE = os.path.join(app.root_path, 'data', 'energy_data.json')

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def get_member_by_username(data, username):
    members = data.get('members', [])
    for m in members:
        if m.get('username', '').lower() == username.lower():
            return m
    return None

def get_current_user_full_data(data, username):
    member = get_member_by_username(data, username)
    if not member:
        return data.get('currentUser', {})
    
    user_data = {
        "username": member.get('username'),
        "name": member.get('name'),
        "houseNumber": member.get('houseNumber'),
        "role": f"Microgrid {member.get('status')} Node",
        "walletBalance": member.get('walletBalance', 1000.0),
        "todayConsumption": round(member.get('currentDemand', 5.0) * 2.8, 1),
        "weeklyConsumption": round(member.get('currentDemand', 5.0) * 18.2, 1),
        "monthlyConsumption": round(member.get('currentDemand', 5.0) * 75.0, 1),
        "yearlyConsumption": round(member.get('currentDemand', 5.0) * 900.0, 1),
        "availableEnergy": member.get('availableEnergy', 0.0),
        "currentDemand": member.get('currentDemand', 0.0),
        "pricePerKwh": member.get('pricePerKwh', 10.0),
        "energyGenerated": round(member.get('availableEnergy', 0.0) + member.get('currentDemand', 0.0), 1),
        "energyShared": member.get('energySold', 0.0),
        "energyPurchased": member.get('energyBought', 0.0),
        "solarCapacity": member.get('solarCapacity', '5.0 kW peak'),
        "batteryStorage": "10.0 kWh (80% charged)",
        "joinedDate": "January 2025"
    }
    return user_data

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '').strip()
        
        data = load_data()
        member = get_member_by_username(data, username)
        
        if member and password == '12345':
            session['user'] = {
                'username': member['username'],
                'name': member['name'],
                'houseNumber': member['houseNumber']
            }
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password. Valid members: srujana, bhumi, yashu, harshi, meghana, pranavi, pooji (Password: 12345)')
            
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    data = load_data()
    username = session.get('user', {}).get('username', 'srujana')
    user_info = get_current_user_full_data(data, username)
    members = data.get('members', [])
    
    total_available = sum(m.get('availableEnergy', 0) for m in members)
    total_producers = sum(1 for m in members if m.get('status') in ['Producer', 'Both'])
    
    return render_template(
        'dashboard.html',
        user=session.get('user'),
        current_user_data=user_info,
        total_available=total_available,
        total_producers=total_producers,
        ai_prediction=data.get('aiPrediction', {}),
        notifications=data.get('notifications', [])
    )

@app.route('/members')
@login_required
def members():
    data = load_data()
    username = session.get('user', {}).get('username')
    user_info = get_current_user_full_data(data, username)
    return render_template('members.html', user=session.get('user'), current_user_data=user_info, members=data.get('members', []))

@app.route('/microgrid')
@login_required
def microgrid():
    data = load_data()
    username = session.get('user', {}).get('username')
    user_info = get_current_user_full_data(data, username)
    return render_template('microgrid.html', user=session.get('user'), current_user_data=user_info, members=data.get('members', []))

@app.route('/profile')
@login_required
def profile():
    data = load_data()
    username = session.get('user', {}).get('username', 'srujana')
    user_info = get_current_user_full_data(data, username)
    return render_template('profile.html', user=session.get('user'), current_user_data=user_info, profile_data=user_info)

@app.route('/trading')
@login_required
def trading():
    data = load_data()
    username = session.get('user', {}).get('username', 'srujana')
    user_info = get_current_user_full_data(data, username)
    other_members = [m for m in data.get('members', []) if m.get('username') != username]
    return render_template('trading.html', user=session.get('user'), current_user_data=user_info, sellers=other_members)

@app.route('/transactions')
@login_required
def transactions():
    data = load_data()
    username = session.get('user', {}).get('username')
    user_info = get_current_user_full_data(data, username)
    return render_template('transactions.html', user=session.get('user'), current_user_data=user_info, transactions=data.get('transactions', []))

@app.route('/notifications')
@login_required
def notifications():
    data = load_data()
    username = session.get('user', {}).get('username')
    user_info = get_current_user_full_data(data, username)
    return render_template(
        'notifications.html',
        user=session.get('user'),
        current_user_data=user_info,
        notifications=data.get('notifications', []),
        energy_requests=data.get('energyRequests', [])
    )

# API Endpoints
@app.route('/api/data', methods=['GET'])
@login_required
def api_get_data():
    return jsonify(load_data())

@app.route('/api/chat', methods=['POST'])
@login_required
def api_chat():
    payload = request.get_json() or {}
    user_msg = payload.get('message', '').strip().lower()
    
    if not user_msg:
        return jsonify({'response': 'Please type a question or report an issue to the GreenGrid Helpdesk!'})
        
    data = load_data()
    username = session.get('user', {}).get('username', 'srujana')
    user_info = get_current_user_full_data(data, username)
    members = data.get('members', [])
    tickets = data.get('helpdeskTickets', [])

    # 0. Friendly Greetings ("hi", "hii", "hello", "hey", "good morning", "good evening", "help")
    if any(user_msg == g or user_msg.startswith(g + ' ') or user_msg.endswith(' ' + g) for g in ['hi', 'hii', 'hiii', 'hello', 'hey', 'heyy', 'good morning', 'good afternoon', 'good evening', 'greetings', 'help', 'start', 'test']):
        return jsonify({
            'response': f"👋 **Hello {user_info.get('name')}! Welcome to the GreenGrid 24/7 AI Helpdesk.**\n\nHow can I assist you today?\n\n• Ask about energy rates (*'who offers cheapest energy'*)\n• Check device usage (*'which device uses most power'*)\n• View your usage details (*'my consumption'*)\n• Report a meter issue (*'open ticket'*)\n• Contact Admin Hotline (**+91 98765 43210**)",
            'isFallback': False
        })

    # 1. Create Helpdesk Support Ticket ("create ticket", "open ticket", "report issue", "report bug", "fault", "problem", "complain")
    if any(k in user_msg for k in ['create ticket', 'open ticket', 'report issue', 'report bug', 'report meter', 'fault', 'problem', 'complain', 'helpdesk ticket', 'issue']):
        category = "General Grid Support"
        if any(k in user_msg for k in ['meter', 'sensor', 'hardware', 'solar']):
            category = "Smart Meter & Hardware"
        elif any(k in user_msg for k in ['billing', 'wallet', 'payment', 'money', 'refund']):
            category = "Billing & Wallet Discrepancy"

        ticket_id = f"TICKET-{int(datetime.now().timestamp()) % 10000}"
        new_ticket = {
            "id": ticket_id,
            "user": f"{user_info.get('name')} (House {user_info.get('houseNumber')})",
            "username": username,
            "category": category,
            "subject": user_msg[:60],
            "status": "In Progress",
            "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "assignedTo": "Support Specialist Srujana (+91 98765 43210)"
        }
        data.setdefault('helpdeskTickets', []).insert(0, new_ticket)
        save_data(data)

        return jsonify({
            'response': f"🎫 **Helpdesk Support Ticket Created!**\n\n• **Ticket Reference:** **{ticket_id}**\n• **User Node:** {user_info.get('name')} (House {user_info.get('houseNumber')})\n• **Category:** {category}\n• **Status:** **In Progress**\n• **Assigned Agent:** Srujana / Grid Helpdesk Admin (+91 98765 43210)\n\nWe have logged your issue into the microgrid support system. Type *'check ticket status'* anytime to view live updates!",
            'isFallback': False
        })

    # 2. Check Ticket Status ("check ticket", "ticket status", "my tickets", "ticket-")
    elif any(k in user_msg for k in ['check ticket', 'ticket status', 'my tickets', 'ticket-']):
        user_tickets = [t for t in tickets if t.get('username') == username or t.get('user', '').lower().find(user_info.get('name', '').lower()) != -1]
        if not user_tickets:
            return jsonify({
                'response': "📋 You currently have no active helpdesk support tickets. Type *'Report Issue'* if you'd like me to open a new ticket for you!",
                'isFallback': False
            })
        
        ticket_summary = "\n".join([f"• **{t['id']}**: {t['category']} — **Status: {t['status']}** (Assigned: {t.get('assignedTo', 'Admin')})" for t in user_tickets[:5]])
        return jsonify({
            'response': f"📋 **Your Active Helpdesk Support Tickets:**\n\n{ticket_summary}\n\nFor urgent escalation, call our 24/7 Helpdesk Hotline: **+91 98765 43210**.",
            'isFallback': False
        })

    # 3. Device & Appliance Power Consumption Queries
    elif any(k in user_msg for k in ['device', 'appliance', 'most power', 'highest consumption', 'highest power', 'power usage', 'what uses power', 'which device', 'ac', 'ev charger', 'fridge']):
        appliances = data.get('houseAppliances', [
            { "name": "HVAC / Central Air Conditioner", "dailyKwh": 5.8, "percentage": 41 },
            { "name": "EV Home Charger (Level 2)", "dailyKwh": 4.2, "percentage": 30 },
            { "name": "Refrigerator & Deep Freezer", "dailyKwh": 2.1, "percentage": 15 },
            { "name": "Smart Lighting & Ceiling Fans", "dailyKwh": 1.5, "percentage": 11 },
            { "name": "Electronics & Computers", "dailyKwh": 0.6, "percentage": 3 }
        ])
        
        breakdown_lines = "\n".join([f"• **{app['name']}**: {app['dailyKwh']} kWh/day ({app['percentage']}%)" for app in appliances])
        
        return jsonify({
            'response': f"⚡ **Highest Power Consumer in Your House:**\n\n1. ❄️ **HVAC / Central Air Conditioner** is using the **most power** at **5.8 kWh/day (41% of total home energy)**!\n\n📊 **Full Household Device Breakdown:**\n{breakdown_lines}\n\n💡 **AI Saving Tip:** Setting your HVAC 2°C higher or shifting EV charging to peak solar generation hours (11 AM - 3 PM) can save up to **₹35/day**!",
            'isFallback': False
        })

    # 4. Specific Member Details Query
    for m in members:
        m_name = m.get('name', '').lower()
        m_house = str(m.get('houseNumber', ''))
        if m_name in user_msg or f"house {m_house}" in user_msg or f"h-{m_house}" in user_msg or f"h{m_house}" in user_msg:
            return jsonify({
                'response': f"🏡 **Member Profile: {m.get('name')} (House {m.get('houseNumber')})**\n• **Node Status:** {m.get('status')}\n• **Rooftop Solar:** {m.get('solarCapacity', '6.0 kW')}\n• **Available Surplus:** **{m.get('availableEnergy')} kWh**\n• **Current Demand:** **{m.get('currentDemand')} kWh**\n• **Selling Rate:** **₹{m.get('pricePerKwh')}/kWh**\n• **Wallet Balance:** ₹{m.get('walletBalance', 1000):.2f}\n• **Total Shared:** {m.get('energySold', 0)} kWh | **Total Bought:** {m.get('energyBought', 0)} kWh",
                'isFallback': False
            })

    # 5. Consumption Details Query
    if any(k in user_msg for k in ['consumption', 'usage', 'how much energy', 'today usage', 'weekly', 'monthly', 'yearly']):
        return jsonify({
            'response': f"📊 **Your Household Consumption Details ({user_info.get('name')}, House {user_info.get('houseNumber')}):**\n• **Today's Consumption:** **{user_info.get('todayConsumption')} kWh**\n• **Weekly Usage:** **{user_info.get('weeklyConsumption')} kWh**\n• **Monthly Usage:** **{user_info.get('monthlyConsumption')} kWh**\n• **Yearly Forecast:** **{user_info.get('yearlyConsumption')} kWh**\n• **Solar Generated Today:** **{user_info.get('energyGenerated')} kWh** (Surplus: +{user_info.get('availableEnergy')} kWh)",
            'isFallback': False
        })

    # 6. Cheapest / Best Rate
    elif any(k in user_msg for k in ['cheap', 'lowest', 'best price', 'who offers', 'cheapest']):
        cheapest = min(members, key=lambda m: m.get('pricePerKwh', 99))
        return jsonify({
            'response': f"⚡ **Best Market Rate:** {cheapest.get('name')} (House {cheapest.get('houseNumber')}) offers the lowest rate at **₹{cheapest.get('pricePerKwh')}/kWh** with {cheapest.get('availableEnergy')} kWh surplus available!",
            'isFallback': False
        })

    # 7. How to Buy / Trade
    elif any(k in user_msg for k in ['buy', 'trade', 'purchase', 'how to buy', 'how to trade']):
        return jsonify({
            'response': "🛒 **P2P Energy Trading Guide:**\n1. Go to the **Energy Trading** tab.\n2. Select a seller (e.g. Pranavi at ₹9/kWh).\n3. Choose your desired quantity in kWh.\n4. Click **Confirm P2P Energy Purchase** to instantly transfer power and update your wallet balance!",
            'isFallback': False
        })

    # 8. Wallet Balance
    elif any(k in user_msg for k in ['wallet', 'balance', 'money', 'credit']):
        balance = user_info.get('walletBalance', 0)
        return jsonify({
            'response': f"💳 Your current wallet balance is **₹{balance:.2f}**. Wallet credits are automatically debited when buying energy and credited when selling surplus power.",
            'isFallback': False
        })

    # 9. Members List Overview
    elif any(k in user_msg for k in ['member', 'household', 'who live', 'house']):
        names = ", ".join([f"{m['name']} (H-{m['houseNumber']})" for m in members])
        return jsonify({
            'response': f"🏡 **7 Neighborhood Members:** {names}.\n\nAsk me about any specific member (e.g. *'Tell me about Bhumi'* or *'House 106'*) for their full energy stats!",
            'isFallback': False
        })

    # 10. AI Predictions / Solar Output
    elif any(k in user_msg for k in ['predict', 'solar', 'tomorrow', 'surplus', 'forecast', 'ai']):
        pred = data.get('aiPrediction', {})
        return jsonify({
            'response': f"🔮 **AI Solar Prediction:** Tomorrow's estimated solar output is **{pred.get('tomorrowGeneration', 24)} kWh** with an expected demand of **{pred.get('tomorrowConsumption', 17)} kWh** (+7 kWh surplus). Suggested trading window: {pred.get('peakDemandWindow', '4:00 PM - 7:00 PM')}.",
            'isFallback': False
        })

    # 11. Microgrid Map / Topology
    elif any(k in user_msg for k in ['map', 'microgrid', 'topology', 'visual']):
        return jsonify({
            'response': "🌐 **Microgrid Topology Map:** Visit the **Microgrid Map** tab to view the live animated topology. Green particle flows represent surplus solar supply and orange trails indicate house demand.",
            'isFallback': False
        })

    # 12. Energy Requests
    elif any(k in user_msg for k in ['request', 'need energy']):
        return jsonify({
            'response': "📩 **Energy Requests:** Check the **Notifications** tab to view pending P2P energy requests from neighbors (e.g. Harshi requested 5 kWh). You can accept or reject requests directly.",
            'isFallback': False
        })

    # 13. Contact / Fallback Support (User's Phone Number)
    else:
        return jsonify({
            'response': "❓ I am not completely sure about that specific query.\n\nFor direct human support, emergency grid assistance, or specific queries beyond my automated AI engine, please contact the GreenGrid Administrator:\n\n📞 **Helpdesk Hotline:** +91 98765 43210\n📧 **Helpdesk Email:** support@greengrid.ai",
            'isFallback': True
        })

@app.route('/api/buy', methods=['POST'])
@login_required
def api_buy_energy():
    payload = request.get_json() or {}
    seller_username = payload.get('seller')
    quantity = float(payload.get('quantity', 0))
    buyer_username = session.get('user', {}).get('username', 'srujana')
    
    if not seller_username or quantity <= 0:
        return jsonify({'success': False, 'message': 'Invalid purchase parameters.'}), 400
        
    data = load_data()
    members = data.get('members', [])
    
    seller = next((m for m in members if m.get('username') == seller_username), None)
    buyer = next((m for m in members if m.get('username') == buyer_username), None)
    
    if not seller or not buyer:
        return jsonify({'success': False, 'message': 'Seller or Buyer node not found.'}), 404
        
    if seller.get('availableEnergy', 0) < quantity:
        return jsonify({'success': False, 'message': f"Only {seller.get('availableEnergy')} kWh available from {seller.get('name')}."}), 400
        
    price_per_kwh = seller.get('pricePerKwh', 10.0)
    total_cost = round(quantity * price_per_kwh, 2)
    
    if buyer.get('walletBalance', 0) < total_cost:
        return jsonify({'success': False, 'message': f"Insufficient wallet balance. Total required: ₹{total_cost}"}), 400
        
    seller['availableEnergy'] = round(seller['availableEnergy'] - quantity, 2)
    seller['energySold'] = round(seller.get('energySold', 0) + quantity, 2)
    seller['walletBalance'] = round(seller.get('walletBalance', 0) + total_cost, 2)
    
    buyer['walletBalance'] = round(buyer['walletBalance'] - total_cost, 2)
    buyer['energyBought'] = round(buyer.get('energyBought', 0) + quantity, 2)
    
    if buyer_username == 'srujana':
        data['currentUser']['walletBalance'] = buyer['walletBalance']
        data['currentUser']['energyPurchased'] = buyer['energyBought']
        
    txn_id = f"TXN-{int(datetime.now().timestamp()) % 10000}"
    new_txn = {
        "id": txn_id,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "buyer": f"{buyer.get('name')} (House {buyer.get('houseNumber')})",
        "seller": f"{seller.get('name')} (House {seller.get('houseNumber')})",
        "energy": quantity,
        "price": price_per_kwh,
        "total": total_cost,
        "status": "Completed"
    }
    data.setdefault('transactions', []).insert(0, new_txn)
    
    notif_id = f"NOTIF-{len(data.get('notifications', [])) + 1}"
    new_notif = {
        "id": notif_id,
        "title": "P2P Purchase Completed",
        "message": f"{buyer.get('name')} bought {quantity} kWh from {seller.get('name')} for ₹{total_cost}.",
        "type": "trade",
        "time": "Just now",
        "unread": True
    }
    data.setdefault('notifications', []).insert(0, new_notif)
    
    save_data(data)
    
    return jsonify({
        'success': True,
        'message': f"Purchase Successful! Bought {quantity} kWh from {seller.get('name')} for ₹{total_cost}.",
        'transaction': new_txn,
        'newWalletBalance': buyer['walletBalance']
    })

@app.route('/api/request/respond', methods=['POST'])
@login_required
def api_request_respond():
    payload = request.get_json() or {}
    req_id = payload.get('requestId')
    action = payload.get('action')
    current_username = session.get('user', {}).get('username', 'srujana')
    
    data = load_data()
    requests_list = data.get('energyRequests', [])
    req = next((r for r in requests_list if r.get('id') == req_id), None)
    
    if not req:
        return jsonify({'success': False, 'message': 'Request not found.'}), 404
        
    if action == 'accept':
        req['status'] = 'Accepted'
        members = data.get('members', [])
        user_member = next((m for m in members if m.get('username') == current_username), None)
        
        amount = req.get('amount', 0)
        offered_price = req.get('offeredPrice', 10)
        total_earned = round(amount * offered_price, 2)
        
        if user_member:
            user_member['availableEnergy'] = max(0, round(user_member.get('availableEnergy', 0) - amount, 2))
            user_member['walletBalance'] = round(user_member.get('walletBalance', 0) + total_earned, 2)
            user_member['energySold'] = round(user_member.get('energySold', 0) + amount, 2)
            
        txn_id = f"TXN-REQ-{int(datetime.now().timestamp()) % 10000}"
        new_txn = {
            "id": txn_id,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "buyer": f"{req.get('requester')} (House {req.get('houseNumber')})",
            "seller": f"{session['user']['name']} (House {session['user']['houseNumber']})",
            "energy": amount,
            "price": offered_price,
            "total": total_earned,
            "status": "Completed"
        }
        data.setdefault('transactions', []).insert(0, new_txn)
        
        save_data(data)
        return jsonify({'success': True, 'message': f"Request accepted! Earned ₹{total_earned}."})
        
    elif action == 'reject':
        req['status'] = 'Rejected'
        save_data(data)
        return jsonify({'success': True, 'message': 'Request rejected.'})
    
    return jsonify({'success': False, 'message': 'Invalid action.'}), 400

@app.errorhandler(404)
def page_not_found(e):
    return render_template('login.html', error="404 Page Not Found"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('login.html', error="500 Internal Server Error"), 500

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'

if __name__ == '__main__':
    local_ip = get_local_ip()
    print("=" * 65)
    print("GreenGrid AI Server Running!")
    print(f"   Local Access:   http://127.0.0.1:5000")
    print(f"   Mobile Access:  http://{local_ip}:5000  (Connect phone to same Wi-Fi)")
    print("=" * 65)
    app.run(host='0.0.0.0', port=5000, debug=True)
