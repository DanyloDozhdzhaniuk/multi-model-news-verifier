from flask import Flask, render_template, request, jsonify
from flask_limiter import Limiter, util as util_limiter

from modules import get_score


app = Flask(__name__, template_folder="./templates", static_folder="./static")

limiter = Limiter(
   util_limiter.get_remote_address, 
   app = app    
)

@app.route("/")
def hello_world():
    return render_template("index.html")

    
@app.route("/verifyNews", methods=['POST'])
@limiter.limit("1 per 1 second")
def predict_news():
    if request.is_json:

        data = request.get_json()
        user_input = data.get('user_input')


        try:

            score = get_score(user_input)

        except Exception as e:

            if type(e) is Exception:

                return jsonify({"prediction": None, "error": str(e)})

            return jsonify({"prediction": None, "error": "Something Went Wrong"})
        

        score = int(score * 100)

   
        return jsonify({"prediction": score, "error": None})