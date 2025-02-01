from flask import Blueprint, jsonify, request, session

from models.delivery_schedule import DeliverySchedule
from models.gas_request import GasRequest
from models.notification import Notification
from models.outlet import Outlet
from models.user import db

consumer_blueprint = Blueprint('consumer', __name__)


# Select Outlet Route
@consumer_blueprint.route('/select-outlet', methods=['GET'])
def select_outlet():
    outlets = Outlet.query.all()
    result = []
    for outlet in outlets:
        # Check if delivery is scheduled for the outlet
        delivery = DeliverySchedule.check_delivery_availability(outlet.outletID)
        result.append({
            "outletID": outlet.outletID,
            "name": outlet.name,
            "address": outlet.address,
            "deliveryScheduled": bool(delivery)  # True if delivery exists, else False
        })
    return jsonify(result), 200


# Request Gas Route
@consumer_blueprint.route('/request', methods=['POST'])
def create_request():
    data = request.get_json()
    user_id = session.get('userID')

    if not user_id:
        return jsonify({"message": "User not logged in"}), 401

    outlet_id = data.get('outletID')
    gas_type_id = data.get('gasTypeID')
    quantity = data.get('quantity')

    # Check for duplicate requests
    existing_request = GasRequest.query.filter_by(userID=user_id, outletID=outlet_id, status='Pending').first()
    if existing_request:
        return jsonify({"message": "Duplicate request exists"}), 400

    # Create a new request
    new_request = GasRequest(
        userID=user_id,
        outletID=outlet_id,
        requestedDate=db.func.current_timestamp(),
        status='Pending',
        token=GasRequest.generate_token()  # Generate unique token
    )

    # Check if delivery is available for the outlet
    delivery = DeliverySchedule.check_delivery_availability(outlet_id)
    if delivery:
        # Update request with delivery details
        new_request.status = 'Scheduled'
        new_request.pickupPeriodStart = delivery.dispatchDate
        new_request.pickupPeriodEnd = delivery.deliveryDate
        db.session.add(new_request)
        db.session.commit()

        # Notify customer
        Notification.log_notification(
            user_id,
            f"Your request is scheduled. Token: {new_request.token}. Pickup between {delivery.dispatchDate} and {delivery.deliveryDate}."
        )
        return jsonify({"message": "Request scheduled", "token": new_request.token}), 201
    else:
        # Don't set pickupPeriodStart and pickupPeriodEnd if no delivery is scheduled
        new_request.pickupPeriodStart = None
        new_request.pickupPeriodEnd = None
        db.session.add(new_request)
        db.session.commit()

        # Notify customer about pending request
        Notification.log_notification(user_id, "Your request is logged, but no delivery is scheduled yet.")
        return jsonify({"message": "Request logged as pending", "token": new_request.token}), 201