from flask import Flask, request, jsonify
from main import real_deal
app = Flask(__name__)

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json  # Receive JSON data
    url = data.get("url")
    date = data.get("date")
    time = data.get("time")
    option = data.get("option")
    # da_main(the_time,place_list,time_mode)
    # result = real_deal(url, date, time, option)
    result = real_deal(date, time, url, option)  # Call your Python function
    return jsonify({"result": result})  # Send response back to React frontend

if __name__ == '__main__':
    app.run(debug=True, port=5000)