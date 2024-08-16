import json, random

from flask import Flask, request, jsonify, abort
from twilio.twiml.messaging_response import MessagingResponse

# Flask Application
app = Flask(__name__)


"""
Functions Section

This section contains all the functions used in the application, both by the 
base script and the endpoints.
"""

def check_constraints(potential_assignments):
    """
    This function is used to verify that the constrains defined in `data.json`
    are being met based on the passed in `potential_assignments`.

    Args:
        potential_assignments (dict): Potentially valid assignemnts to check. 
            The key is a user and the value is another user that the original 
            user has been assigned as a gift giver.
            ie. { "Adam": "Beatrice", ...}
    
    Returns:
        boolean: Returns true if the potential assignments are all valid based 
            on the constraints defined in `data.json`. Returns false if the 
            potential assignments are not valid.
    """
    constraints = {person: info['constraints'] for person, info in people_info.items()}

    for person, recipient in potential_assignments.items():
        if recipient in constraints.get(person, []):
            return False
    return True


def create_assignments():
    """
    This function is used to create the global `assignments` variable which we
    will use in our other functions and endpoints. This has to be created only
    once so that the assignments stay the same between different calls.

    Returns:
        dict: A dictionary of valid assignments based on the constraints defined
            in the `data.json` file.
    """
    people = list(people_info.keys())

    # Keep shuffling until a valid assignments is found
    # TODO: Probably should make it so this can't infinite loop, however 
    # unlikely that is.
    while True:
        random.shuffle(people)
        working_assignments = {people[i]: people[(i + 1) % len(people)] for i in range(len(people))}
        if check_constraints(working_assignments):
            break

    # Sort the assignments alphabetically by name
    final_assignments = dict(sorted(working_assignments.items(), key=lambda x: x[0]))
    return final_assignments

def get_name_by_phone_number(phone_number):
    """
    This function returns a users name based on their phone number using the
    information found in `data.json`. It will return None if no user is found.

    Args:
        phone_number (string): The phone number of the user who's name we want
            to return.

    Returns:
        string or None: The name of the user based on the phone number or None
            if no user is found.
    """
    for name, info in people_info.items():
        if info["phone_number"] == phone_number:
            return name
    return None


def create_message(users_name):
    """
    Generate the message string that is output via Twilio SMS if the user is a 
    valid user (which is based on their phone number).

    Args:
        users_name (string): The user's name to generate the message for.

    Returns:
        string or None: Returns the message we want to send via SMS to the user
            to let them know their Christmas assignment.  Returns None if the
            user's name is not in the `assignments` variable.
    """
    if users_name in assignments:
        recipient = assignments[users_name]
        # This message was being blocked by carriers, probably because it had
        # the word "gift" in it. Right now we are just sending the assignment
        # name with nothing else.
        #return f"Welcome to the Ellert Family Gift Exchange {person}! Your gift recipient is {recipient}. Merry Christmas!"
        return f"{recipient}"
    else:
        return None


def extract_phone_numbers():
    """
    This function returns a list of all the phone numbers in `data.json`.

    Returns:
        list: A list of the phone numbers from `data.json`.
    """
    return [info["phone_number"] for info in people_info.values()]


def is_authorized_number(phone_number):
    """
    This function checks if a phone number is valid by checking it against the
    list of phone numbers in `data.json`.

    Args:
        phone_number (string): The phone number we are checking against the list
            of valid phone numbers.

    Returns:
        boolean: Returns true if the phone number is in `data.json` and false if
            it is not.
    """
    phone_numbers = extract_phone_numbers()
    return phone_number in phone_numbers

"""
Base Script Section

This section contains the base script which randomizes the users and assigns 
them.

First, we read combined data from the JSON file and create the `people_info` 
variable. We make `people_info` a global variable so we are not constantly 
opening the file to read the contents as that would be slow.

`people_info` will be a 2D dict structured as shown below. The key is the user's 
name and then phone number and constraints for that user will be under that key:

    {
        "Adam": {
            "phone_number": "+15556667777",
            "constraints": ["Beatrice"]
        },
        "Beatrice": {
            "phone_number": "+15556667777",
            "constraints": ["Adam"]
        },
        ...
    }

As an example, to get a user's phone number we can use the following:

user = "Adam"
people_info[user]["phone_number"] # +15556667777

Once we have the `people_info` variable set, we create the assignments for the
gift exchange. We also make the `assignments` variable a global variable because
we want to keep the assignements the same between different calls. We do not
want to randomize the assignments more than once in the lifetime of the 
application.
"""
with open('data.json') as json_file:
    people_info = json.load(json_file)

assignments = create_assignments()

"""
API Endpoints Section

This section of the script contains all the API endpoints that are used in the 
application.
"""

@app.route("/", methods=['POST'])
def sms_reply():
    """
    This function is used as the main endpoint for the application and handles
    the SMS responses. This is the endpoint that you will hook into your Twilio
    number for recieving SMS messages.

    This function checks if the user is valid based on their phone number, then
    checks if their message is one we want to respond to or not and based on
    what the user sent to us we either send them their Christmas exchange
    assignment, or some other text based on the situation.
    """
    incoming_msg = request.form.get('Body').strip()
    from_number = request.form.get('From')

    person = get_name_by_phone_number(from_number)

    if person:
        resp = MessagingResponse()
        if is_authorized_number(from_number) and incoming_msg.lower() == "christmas":
            resp.message(create_message(person))
            return str(resp)
        elif is_authorized_number(from_number) and incoming_msg.lower() == "subscribe":
            resp.message("You are now subscribed!")
            return str(resp)
        else:
            lucky_num = random.randrange(1, 100)
            resp.message(f"Your lucky number is {lucky_num}!")
            return str(resp)
    else:
        abort(403)
    

@app.route("/sms/test", methods=['POST'])
def sms_reply_test():
    """
    This function is used with Postman (or whatever API testing suite you want)
    to test out the sms_reply() function above.

    This function checks if the user is valid based on their phone number, then
    checks if their message is one we want to respond to or not and based on
    what the user sent to us we either send them their Christmas exchange
    assignment, or some other text based on the situation.
    """
    incoming_msg = request.form.get('Body').strip()
    from_number = request.form.get('From')

    person = get_name_by_phone_number(from_number)

    if person:
        if is_authorized_number(from_number) and incoming_msg.lower() == "christmas":
            xmas_message = create_message(person)
            return xmas_message
        elif is_authorized_number(from_number) and incoming_msg.lower() == "subscribe":
            return 'You are now subscribed.'
        else:
            lucky_num = random.randrange(1, 100)
            return f"Your lucky number is {lucky_num}!"
    else:
        abort(403)


@app.route("/assignments", methods=['GET'])
def get_assignments():
    """
    This endpoint returns all assignments for the current gift exchange.
    """
    return jsonify(assignments)


@app.route("/user/<person>", methods=['GET'])
def get_user(person):
    """
    This endpoint returns information about a particular user if they are valid
    or a 404 if they are not a valid user.
    """
    if person in assignments:
        recipient = assignments[person]
        user_info = {
            'name': person,
            'phone': people_info[person]['phone_number'],
            'recipient': recipient,
            'recipient phone': people_info[recipient]['phone_number'],
            'sms message': create_message(person)
        }
        return jsonify(user_info)
    else:
        abort(404, description=f"User with name {person} not found")


@app.route("/valid-phone-numbers", methods=['GET'])
def get_phone_numbers():
    """
    This endpoint returns a list of valid phone numbers (ie. the phone nunbers
    of all the users defined in `data.json`).
    """
    return jsonify(extract_phone_numbers())


@app.route("/validate-number/<phone_number>", methods=['GET'])
def validate_phone_number(phone_number):
    """
    This endpoint will validate a particular phone number against the list of
    valid phone numbers (ie. the phone numbers of all the users defined in
    `data.json`).
    """
    if is_authorized_number("+" + phone_number):
        return f"+{phone_number} is an authorized phone number."
    else:
        return f"+{phone_number} is not an authorized phone number.", 403
    

if __name__ == "__main__":
    """
    Run the Flask application
    """
    app.run(host="0.0.0.0", port=5000)