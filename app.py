from flask import Flask, request, jsonify  
from riddle_generator import RiddleGenerator

app = Flask(__name__)

@app.route("/generate-riddle", methods=["POST"])
def generate_riddle():
    data = request.get_json()
    lm_id = data.get("landmarkId")
    print(f"[Python Flask] Received landmarkId: {lm_id}")
    
    generator = RiddleGenerator()
    generator.loadMetaFromDB(lm_id).generateRiddle()
    return jsonify({
        "status": "ok",
        "riddle": generator.riddle # temporary testing
    })

if __name__ == "__main__":
    app.run(port=5001)
