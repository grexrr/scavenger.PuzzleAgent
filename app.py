from flask import Flask, request, jsonify  
from riddle_generator import RiddleGenerator
from story_weaver import StoryWeaver
app = Flask(__name__)

story_weaver = StoryWeaver()
# @app.route("/generate-riddle", methods=["POST"])
# def generate_riddle():
#     language = "монгол хэл"
#     style = "Devilish"
#     data = request.get_json()
#     lm_id = data.get("landmarkId")
#     difficulty = data.get("difficulty")
#     print(f"[Python Flask] Received landmarkId {lm_id}: difficulty {difficulty}.")

    
#     generator = RiddleGenerator(model="chatgpt")
#     generator.loadMetaFromDB(lm_id).generateRiddle(language, style, difficulty)
#     return jsonify({
#         "status": "ok",
#         "riddle": generator.riddle # temporary testing
#     })


@app.route("/generate-riddle", methods=["POST"])
def generate_riddle():
    data = request.get_json()
    
    session_id = data.get("session_id")       # backend not sent yet
    language = data.get("language", "English")
    style = data.get("style", "Medieval")
    difficulty = data.get("difficulty")
    puzzle_pool = data.get("puzzle_pool", []) # backend not sent yet
    
    session_id = story_weaver.start_episode(
        puzzle_pool=puzzle_pool, 
        session_id=session_id
    )

    riddle = story_weaver.serve_riddle(
        language=language,
        style=style,
        difficulty=difficulty,
        session_id=session_id
    )

    return jsonify({
        "status": "ok",
        "session_id": session_id,
        "riddle": riddle["riddle"]
    })


if __name__ == "__main__":
    app.run(port=5001)