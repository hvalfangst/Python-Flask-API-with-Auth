import logging

from .messages import UserMessages
from .models import CreateUserRequest, UpdateUserRequest
from .repository import UsersRepository
from .security import authenticate, generate_jwt_token
from common import db_config, jwt_config
import sys
import traceback
import bcrypt
from flask import request, jsonify
from pydantic import EmailStr

# Configure the logging module
logging.basicConfig(stream=sys.stderr, level=logging.ERROR)

# Create a logger for this module
logger = logging.getLogger(__name__)

# Initialize the UsersRepository
db = UsersRepository(config=db_config)


def create_user_handler():
    """
    Handle the creation of a user.

    Creates a new user with the provided data in the request.

    Returns:
        tuple: Tuple containing the JSON response and HTTP status code.
    """
    try:
        req = CreateUserRequest(**request.get_json())
        hashed_password = bcrypt.hashpw(req.password.encode('utf-8'), bcrypt.gensalt())
        req.password = hashed_password.decode('utf-8')
        db.create(request=req)
        return jsonify({"message": "User created"}), 201
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": "Unauthorized"}), 401


def update_user_handler(email: EmailStr):
    """
  Handle the update of a user.

  Updates an existing user with the provided data in the request.

  Args:
      email (EmailStr): Email of the user to be updated.

  Returns:
      tuple: Tuple containing the JSON response and HTTP status code.
  """
    try:
        user = db.get_by_email(email)
        if user is None:
            return jsonify({"error": f"No user found with email: {email}"}), 404

        req = UpdateUserRequest(**request.get_json())
        db.update(email=email, request=req)
        return jsonify({"message": "Successfully updated account."})
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": "Unauthorized"}), 401


def list_users_handler():
    """
 Handle the listing of users.

 Lists all users present in the system.

 Returns:
     tuple: Tuple containing the JSON response and HTTP status code.
 """
    try:
        users = db.list()

        if not users:
            return jsonify({"error": f"No users present"}), 404

        for user in users:
            print(f"password: {user.password}")

        users_dict = [user.to_dict() for user in users]
        return jsonify(users_dict)
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": "Unauthorized"}), 401


def get_user_handler(email: EmailStr):
    """
   Handle the retrieval of a user.

   Retrieves the user with the specified email.

   Args:
       email (EmailStr): Email of the user to be retrieved.

   Returns:
       tuple: Tuple containing the JSON response and HTTP status code.
   """
    try:
        user = db.get_by_email(email)

        if user is None:
            return jsonify({"error": f"No user found with email: {email}"}), 404

        user_data = user.to_dict()
        return jsonify(user_data)

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": "Unauthorized"}), 401


def delete_user_handler(email: EmailStr):
    """
   Handle the deletion of a user.

   Deletes the user with the specified email.

   Args:
       email (EmailStr): Email of the user to be deleted.

   Returns:
       tuple: Tuple containing the JSON response and HTTP status code.
   """
    try:
        user = db.get_by_email(email)

        if user is None:
            return jsonify({"error": f"No user found with email: {email}"}), 404

        db.delete_by_email(email)
        return jsonify({"message": f"User associated with email {email} has been deleted."})
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": "Unauthorized"}), 401


def login_user_handler():
    """
   Handle user login.

   Authenticates the user with the provided email and password.
   Generates a JWT token upon successful authentication.

   Returns:
       tuple: Tuple containing the JSON response and HTTP status code.
   """
    try:
        request_json = request.get_json()
        email: EmailStr = request_json.get('email')
        password = request_json.get('password')

        if not (email and password):
            return jsonify({"error": UserMessages.MISSING_CREDENTIALS}), 400

        authenticated, access = authenticate(db, email, password)

        if authenticated:
            token = generate_jwt_token(config=jwt_config, email=email, access=access)
            return jsonify({"token": token})
        else:
            return jsonify({"error": UserMessages.USER_UNAUTHORIZED}), 401
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": "Unauthorized"}), 401
