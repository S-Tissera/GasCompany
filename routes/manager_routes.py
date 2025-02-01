from io import BytesIO
import qrcode
from flask import Blueprint, request, jsonify, send_file
from models.gas_request import GasRequest
from app import db
from utils.notification_service import notify_consumer

# Create a Blueprint for managers
manager_blueprint = Blueprint('manager', __name__)

@manager_blueprint.route('/verify/<token>', methods=['GET'])
def verify_request(token):
    """Verify a gas request using a token"""
    gas_request = GasRequest.query.filter_by(token=token).first()

    if not gas_request:
        return jsonify({"message": "Invalid Token"}), 404

    return jsonify({
        "requestID": gas_request.requestID,
        "userID": gas_request.userID,
        "outletID": gas_request.outletID,
        "status": gas_request.status,
        "pickupPeriodStart": gas_request.pickupPeriodStart,
        "pickupPeriodEnd": gas_request.pickupPeriodEnd
    }), 200

@manager_blueprint.route('/generate_qr/<token>', methods=['GET'])
def generate_qr(token):
    """Generate a QR code for a given token"""
    try:
        qr = qrcode.make(token)
        img_io = BytesIO()
        qr.save(img_io, format='PNG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/png')
    except Exception as e:
        return jsonify({"message": f"Error generating QR: {str(e)}"}), 500

@manager_blueprint.route('/update_status/<int:request_id>', methods=['PUT'])
def update_request_status(request_id):
    """Update the status of a gas request"""
    data = request.get_json()
    new_status = data.get('status')

    if new_status not in ['Pending', 'Completed', 'Reallocated']:
        return jsonify({"message": "Invalid status"}), 400

    gas_request = GasRequest.query.get(request_id)

    if not gas_request:
        return jsonify({"message": "Request not found"}), 404

    # Update status and commit changes
    gas_request.status = new_status
    db.session.commit()

    # Notify the consumer
    message = f"Your gas request (ID: {request_id}) is now {new_status}."
    notify_consumer(gas_request.userID, message)

    return jsonify({"message": f"Request {request_id} updated to {new_status}"}), 200

@manager_blueprint.route('/scheduled_requests', methods=['GET'])
def get_scheduled_requests():
    """Retrieve all scheduled gas requests (Pending status)"""
    scheduled_requests = GasRequest.query.filter_by(status="Scheduled").all()

    if not scheduled_requests:
        return jsonify({"message": "No scheduled requests found."}), 404

    # Convert requests to JSON format
    requests_data = [
        {
            "requestID": request.requestID,
            "userID": request.userID,
            "outletID": request.outletID,
            "status": request.status,
            "pickupPeriodStart": request.pickupPeriodStart,
            "pickupPeriodEnd": request.pickupPeriodEnd
        }
        for request in scheduled_requests
    ]

    return jsonify({"scheduledRequests": requests_data}), 200

# Fix: Renamed function to avoid duplication
@manager_blueprint.route('/test', methods=['GET'])
def test_endpoint():
    return "Works"
