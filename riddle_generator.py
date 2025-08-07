import os
import json
import lmstudio as lms
import openai
from pymongo import MongoClient
from dotenv import load_dotenv


class RiddleGenerator:
    def __init__(self, model="local", mongo_url="mongodb://localhost:27017") -> None:
        # self.model = lms.llm(model)
        self.mongo_url = mongo_url
        self.meta = {}
        self.mode = model.lower()
        self.riddle = ""

        if self.mode == "local":
            self.model = lms.llm("llama-3.2-1b-instruct") 
        elif self.mode == "chatgpt":
            from dotenv import load_dotenv
            load_dotenv()
            openai.api_key = os.getenv("OPENAI_API_KEY")
            self.model = openai  
        else:
            raise ValueError(f"[RiddleGenerator] Unknown model mode: {model}")

    def loadMetaFromDB(self, landmark_id):
        client = MongoClient(self.mongo_url)
        collection = client["scavengerhunt"]["landmark_metadata"]
        self.meta = collection.find_one({"landmarkId": landmark_id})
        if self.meta and "_id" in self.meta:
            self.meta["_id"] = str(self.meta["_id"])  # convert ObjectID to string
        return self

    def generateRiddle(self, language="English", style="medieval", difficulty=50):

        # ========== basic info collection ==========   
        meta = self.meta.get("meta", {})
        description = meta.get("description", {})

        if not description:
            self.riddle = "No riddle generated"
            return self

        history = description.get("history", [])
        architecture = description.get("architecture", [])
        significance = description.get("significance", [])

        history_str = "history: " + ", ".join(history) if history else ""
        architecture_str = "architecture: " + ", ".join(architecture) if architecture else ""
        significance_str = "significance: " + ", ".join(significance) if significance else ""

        reference = ""
        if "wikipedia" in meta:
            reference = "reference:\n" + meta["wikipedia"]
        
        # ========== prompt based on difficulty ==========   
        user_prompt = "\n".join(filter(None, [history_str, architecture_str, significance_str, reference]))
        system_prompt = self._generateSystemPrompt(language, style, difficulty) 
        
        # ========== response based on model selection ==========   
        
        if self.mode == "local":
            # LMSTUDIO GUI STYLE
            ## Prompt format: https://www.llama.com/docs/model-cards-and-prompt-formats/meta-llama-3/
            template = r"""
            <|begin_of_text|><|start_header_id|>system<|end_header_id|>
            {system}
            <|eot_id|><|start_header_id|>user<|end_header_id|>
            {user}
            <|eot_id|><|start_header_id|>assistant<|end_header_id|>
            """

            final_prompt = template.format(system=system_prompt, user=user_prompt)

            result = self.model.respond(final_prompt)
            if hasattr(result, 'text'):
                self.riddle = result.text
            else:
                self.riddle = str(result)  # fallback to string conversion
            print(f"[PuzzleAgent]: {self.riddle}")
            return self
        elif self.mode == "chatgpt":
            # chatGPT
            response = self.model.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.5,
                max_tokens=500
            )
            self.riddle = response.choices[0].message.content.strip()
            print(f"[PuzzleAgent]: {self.riddle}")
            return self
        else:
            raise ValueError(f"Unsupported mode: {self.mode}. Please choose either 'local' or 'chatgpt'.")
    
    def _generateSystemPrompt(self, language="English", style="Medieval", difficulty=50):

        try:
            difficulty = float(difficulty)
        except (ValueError, TypeError):
            difficulty = 50.0  
            print("[PuzzleAgent]: Invalid difficulty input, defaulting to 50.0")
        
        if difficulty < 33.3:
            diff_prompt = "Write a simple and clear riddle suitable for beginners or young audiences (around 10 years old)."
        elif difficulty < 66.6:
            diff_prompt = "Write a moderately challenging riddle with some use of rhetorical devices, but still solvable based on the context."
        else:
            diff_prompt = "Write a challenging and abstract riddle that relies on metaphor and indirect clues, avoiding clear landmark descriptions."

        system_prompt = f"""
            Written in {language}. You are a master riddle writer. {diff_prompt} Do not include any extra explanations or mention the landmark's name explicitly.
            
            Use the following details as reference:
            \\begin{{quote}}
            \\textbf{{History}}: Highlight significant events or periods related to the landmark.
            \\textbf{{Architecture}}: Mention unique structural or design features, pay attention to color
            \\textbf{{Significance}}: Emphasize its cultural, religious, or social importance.
            \\textbf{{Length}}: No more than 5 lines.
            The riddle should be concise, engaging, and reflect a {style}.
            \\end{{quote}}

            Create a {style} riddle based on the information about {self.meta.get("name", "the landmark")} in {self.meta.get("city", "the city")}. 
            """
        return system_prompt

    def saveToFile(self, filename):
        os.makedirs("outputfiles", exist_ok=True)
        path = os.path.join("outputfiles", filename)
        with open(path, 'w', encoding="utf-8") as f:
            json.dump(self.meta, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    generator = RiddleGenerator()
    generator.loadMetaFromDB("6839d130b70cd905e96e359f").saveToFile("raw_meta.json")
    generator.generateRiddle()
    print(generator.riddle)