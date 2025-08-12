from flask import Flask, request, jsonify  
from riddle_generator import RiddleGenerator
from story_weaver import StoryWeaver
app = Flask(__name__)

story_weaver = StoryWeaver()
# test 
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
    
    session_id = data.get("sessionId")        # backend not sent yet
    landmark_id = data.get("landmarkId")
    language = data.get("language", "English")
    style = data.get("style", "Medieval")
    difficulty = data.get("difficulty")
    puzzle_pool = data.get("puzzlePool", [])  # backend not sent yet
    
    if not session_id:
        print("No session_id")
        return jsonify({"error": "MISSING_SESSION_ID"}), 400
    if not landmark_id:
        return jsonify({"error": "MISSING_LANDMARK_ID"}), 400
    
    try:
        story_weaver.start_episode(
            puzzle_pool=puzzle_pool, 
            session_id=session_id
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    
    # story_weaver.start_episode(
    #     puzzle_pool=puzzle_pool, 
    #     session_id=session_id
    # )

    riddle = story_weaver.serve_riddle(
        language=language,
        style=style,
        difficulty=difficulty,
        landmark_id=landmark_id,
        session_id=session_id
    )

    if "error" in riddle:
        return jsonify(riddle), 400

    return jsonify({
        "status": "ok",
        "session_id": session_id,
        "landmarkId": landmark_id,
        "riddle": riddle["riddle"]
    })

@app.route("/reset-session", methods=["POST"])
def reset_session():
    data = request.get_json(force=True)
    sid = data.get("session_id")
    if not sid:
        return jsonify({"status": "error", "message": "session_id required"}), 400

    if sid in story_weaver.sessions:
        story_weaver.sessions.pop(sid, None)
        return jsonify({"status": "ok", "message": f"Session {sid} reset"})
    else:
        return jsonify({"status": "error", "message": f"Session {sid} not found"}), 404



if __name__ == "__main__":
    app.run(port=5001)