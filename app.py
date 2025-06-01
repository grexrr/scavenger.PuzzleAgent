from flask import Flask, request, jsonify  

app = Flask(__name__)

@app.route("/generate-riddle", methods=["POST"])
def generate_riddle():
    data = request.get_json()
    lm_id = data.get("landmarkId")
    print(f"[Python Flask] Received landmarkId: {lm_id}")
    
    return jsonify({
        "status": "ok",
        "riddle": lm_id # temporary testing
    })

if __name__ == "__main__":
    app.run(port=5001)
