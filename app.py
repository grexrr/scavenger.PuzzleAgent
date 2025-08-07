from flask import Flask, request, jsonify  
from riddle_generator import RiddleGenerator

app = Flask(__name__)

@app.route("/generate-riddle", methods=["POST"])
def generate_riddle():
    data = request.get_json()
    
    language = data.get("language", "English")
    style = data.get("style", "Medieval")
    lm_id = data.get("landmarkId")
    difficulty = data.get("difficulty")
    
    print(f"[Python Flask] Received landmarkId {lm_id}: difficulty {difficulty}.")

    
    generator = RiddleGenerator(model="chatgpt")
    generator.loadMetaFromDB(lm_id).generateRiddle(language, style, difficulty)
    return jsonify({
        "status": "ok",
        "riddle": generator.riddle # temporary testing
    })

if __name__ == "__main__":
    app.run(port=5001)
