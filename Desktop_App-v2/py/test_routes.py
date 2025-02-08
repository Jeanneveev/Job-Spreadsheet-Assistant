# ROUTES
from flask import Flask, request, session
from flask_session import Session
from flask_cors import CORS
import redis, json
#for forcibly clearing session files
import atexit

app = Flask(__name__)

# Configurations
app.config["SECRET_KEY"]="change_later"
app.config["SESSION_TYPE"] = "redis"
app.config["SESSION_PERMANENT"] = False
r = redis.from_url('redis://127.0.0.1:6379')
app.config['SESSION_REDIS'] = r
def test_redis_connection(redis_session):
    """Check that Redis is connected to"""
    try:
        redis_session.ping()  # Check if Redis is alive
        print("Redis connection successful!")
    except redis.exceptions.ConnectionError as e:
        print(f"Redis connection error: {e}")
        exit()  # Or handle the error appropriately
test_redis_connection(r)
app.config["CORS_HEADERS"] = "Content-Type"

# Initialize Plugins
sess=Session()
sess.init_app(app)
CORS(app,supports_credentials=True)

#check that the server's running and connected
@app.route("/", methods=["GET","POST"])
def check():
    return {"result":"Server active!"}

### ERROR!!!: This only works as an independent Flask app
#       It seems like every time this is run,
#       it makes a new session variable, rather than getting the old one
#           Maybe it's not recognizing it's the same session?
@app.route("/add_detail/<detail>",methods=["GET","POST"])
def add_detail_to_list(detail):
    """Add a q_detail to a list of q_details"""
    # Initialize the list if it doesn't exist
    if 'lst' not in session:
        print("Session variable not found. Initializing...")
        session['lst'] = json.dumps([])
        session.modified = True

    # Append to the list
    lst:list[str]=json.loads(session['lst'])
    print("Before appending:",lst)
    lst.append(detail)
    print("After appending:",lst)
    session['lst'] = json.dumps(lst)
    session.modified = True
    
    return {"response":f"{lst}"}
@app.route("/get_all_details",methods=["GET"])
def get_all_details():
    details:list[str]=session.get("lst",[])
    return {"result":details}
@app.route("/check_detail/<detail>")
def check_detail(detail):
    details:list[str]=session.get("lst",[])
    if detail in details:
        return {"result":"True","detail_list":details}
    else:
        return {"result":"False","detail_list":details}


## NOTE: Make sure this works in production
### ERROR!!! Doesn't work with Electron app
#       Maybe due to how the Flask app is killed?
def clear_redis_sessions(redis_session):
    """Clears all session data from Redis."""
    try:
        for key in redis_session.keys("session:*"): # Important: Use a pattern to only delete session keys
            redis_session.delete(key)
        print("Redis sessions cleared.")
    except Exception as e:
        print(f"Error clearing Redis sessions: {e}")
atexit.register(clear_redis_sessions,redis_session=r)  # Register the cleanup function


# print(app.url_map)

if __name__ == "__main__":
    app.run(debug=True)