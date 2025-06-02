import lmstudio as lms

model = lms.llm("llama-3.2-1b-instruct")

# llm = Llama(
#     model_path="/Users/grexrr/.lmstudio/models/hugging-quants/Llama-3.2-1B-Instruct-Q8_0-GGUF/llama-3.2-1b-instruct-q8_0.gguf",
#     n_ctx=4096,
#     n_threads=8,
#     n_gpu_layers=20
# )

system_prompt = """
You are a master riddle writer. Writting **only** riddles for landmark in following format without any extra information nor mentioning landmark name.
\begin{quote}
Written in {Chinese}
Create a {style} riddle based on the information about {name}. Use the following details as context:\

\textbf{History}: Highlight significant events or periods related to the landmark.\
\textbf{Architecture}: Mention unique structural or design features, pay attention to color\
\textbf{Significance}: Emphasize its cultural, religious, or social importance.\
\textbf{Length}: No more than 5 lines.
The riddle should be concise, engaging, and reflect a {tone}, such as a medieval style. 
\end{quote}
"""

template = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>
{system}
<|eot_id|><|start_header_id|>user<|end_header_id|>
{user}
<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""

user_prompt = r"""

Saints Peter and Paul's Church, Cork

Article
Talk
Read
Edit
View history

Tools
Appearance hide
Text

Small

Standard

Large
Width

Standard

Wide
Color (beta)

Automatic

Light

Dark
Coordinates: 51.898809°N 8.474461°W
From Wikipedia, the free encyclopedia
Ss. Peter & Paul's Church
Saints Peter and Paul's Church, Cork
Eaglais Naoimh Peadar agus Pól

Portal at Saint Peter and Paul's Place
Ss. Peter & Paul's Church is located in Cork CentralSs. Peter & Paul's ChurchSs. Peter & Paul's Church
Location	Saint Peter and Paul's Place, Cork
Country	Ireland
Denomination	Roman Catholic
Website	saintspeterandpauls.ie
History
Status	In use
Dedication	Saint Peter and Saint Paul
Consecrated	August 1874
Architecture
Architect(s)	E. W. Pugin and George Ashlin
Architectural type	Church
Style	Gothic Revival
Groundbreaking	15 August 1859
Completed	1866
Administration
Archdiocese	Cashel and Emly
Diocese	Cork and Ross
Parish	SS Peter & Paul's

The nave of SS Peter and Paul's, shown in The Illustrated London News.
Saints Peter and Paul's Church is a Catholic church located on Carey's Lane in Cork City, Ireland.

History
Peter and Paul's was built to replace Carey's Lane Chapel, a much smaller structure built in 1786.[1]

Under the guidance of Archdeacon John Murphy, a design competition was run in the 1850s and won by E. W. Pugin, son of Augustus Pugin. The foundation stone was laid on 15 August 1859.[2] Though the construction of the church was completed in on 29 June 1864, and the public were granted the opportunity to view the interior of the church at this time, the church was unable to open as the debts associated with its construction had not yet been paid off.[3] Exactly two years after the church first welcomed members of the public to enter, it was dedicated for worship on 29 June 1866.[4][5]

In 1930, an associated Scout Group was formed, the 4th Cork (Ss Peter and Paul's) meeting in Brown Street, then Castle Street and now Gilabbey Park, though no longer directly connected to the parish.[citation needed]

Between 1939 and 1962, the roof of the building was renewed, and the baptistry was repaired.[6]

In the 1980s the building underwent major renovations.[6]

Architecture

Interior with stained glass
The church comprises a central nave with gable roof and two aisles. The walls are of red sandstone with limestone dressing. The aisles are at either side of the nave, which is covered with a gable roof. The ridge of the roof is decorated by ornamental ironwork, partly gilt, terminated at the western gable by an ornamental cross with foliated arms.[citation needed]

The grand altar is carved from 36 tons of Carrara marble. The pavements surrounding the altar, and the steps, are all of white Italian vein marble. The apse is decorated with blue and gold ceiling panels. The flooring of the church is in white and black marble.[citation needed]

The pulpit and confessionals were carved from Russian oak by craftsmen from Leuven and Cork.[citation needed]

### Response:
"""

final_prompt = template.format(system=system_prompt, user=user_prompt)
response = model.respond(final_prompt)

print(response)