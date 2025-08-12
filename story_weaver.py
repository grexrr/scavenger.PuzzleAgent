import uuid
from riddle_generator import RiddleGenerator

class StoryWeaver:
    def __init__(self) -> None:
        self.sessions = {} #episode_id -> state dict
    
    def start_episode(self, puzzle_pool, session_id=None):
        # story_context = {
        #     "beat_tag": "development",
        #     "previous_riddles": [
        #         {"text": "...", "beat_tag": "opening"},
        #         {"text": "...", "beat_tag": "development"}
        #     ]
        # }

        if not session_id:
            session_id = str(uuid.uuid4())
            
        state = {
            "total_slots": len(puzzle_pool),
            "slot_index": 0,
            "beat_plan": self._generate_beat_plan(len(puzzle_pool)),
            "riddle_history": [],
            "puzzle_pool": puzzle_pool
        }
        self.sessions[session_id] = state
        
        return session_id
    
    def serve_riddle(self, language, style, difficulty, session_id=None):
        
        state = self.sessions[session_id]
        slot_index = state["slot_index"]
        beat_tag = state["beat_plan"][slot_index]

        prev_summary = self._format_previous_riddles(state["riddle_history"])
        story_context = f"Current story beat: {beat_tag}\nPrevious riddles: \n{prev_summary}"
        lmid = state["puzzle_pool"][slot_index]
        
        riddle_generator = RiddleGenerator(model="chatgpt")
        riddle_generator.loadMetaFromDB(lmid).generateRiddle(
            language=language,
            style=style,
            difficulty=difficulty, #placeholder
            story_context=story_context
        )

        riddle = riddle_generator.riddle

        #save to riddle_history
        state["riddle_history"].append({
            "text":riddle,
            "beat_tag": beat_tag
        })

        state["slot_index"] += 1

        return {
            "session_id": session_id,
            "slot_index": slot_index,  
            "total_slots": state["total_slots"],
            "beat_tag": beat_tag,
            "riddle": riddle
        }

    def _generate_beat_plan(self, total_slots):
        if total_slots == 1:
            return["opening"]
        elif total_slots == 2:
            return["opening", "ending"]
        elif total_slots == 3:
            return["opening", "development", "ending"]
        else:
            return ["opening"] + ["development"] * (total_slots-2) + ["ending"]
        
    def _format_previous_riddles(self, riddle_history):
        if not riddle_history:
            return "No previous riddles."
        
        lines = []
        for r in riddle_history:
            snippet = r["text"][:80] + ("..." if len(r["text"]) > 80 else "")
            lines.append(f"[{r['beat_tag']}] {snippet}")
        return "\n".join(lines)