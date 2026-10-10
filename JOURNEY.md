WAHT LEARNED:

1\. when using semantic chunking strategy instead of generating embedding for each sentence use window of size n to generate embeddings this also captures context from other sentences too

when using calc simliraity scores for 2 senetnces or matrices it will return another matrix as the matrix is 2d not 1d so to get the scalar val score we use **global average**, now in **global average** we do similarity check between 1 word's embedding in matrix 1 with each with other matrix 2 then we avg it then we take next word and do same for all words in matrix 1 and again we avg all scores to get final similarity , score, but here we loose info because too much averaging , hence we use **GLOBAL MAX AVG** so instead of averaging 1 words simliraity with all other words in mat 2 we take max btw them and do same for all other words in mat 1 then we take average. Also if we do **GLOBAL MAX AVG** for only matrix then we get score w.r.t only mat 1 hence we must also do for mat2 w..rt mat 1 so we get sim\_score from both sides 

eg. • Sentence 1 is short and concise (e.g., "The cat sat on the mat."), every single one of its words might find a perfect match in a longer Sentence 2 (e.g., "Yesterday, a cute fluffy cat sat happily on the doormat while eating fish.").(PRECISION ) this score we get very high score ( HIGH PRECISION ) if we do opposite( RECALL ) low score ( LOW RECALL ) because not all words from sent2 resent in sent 1 so we take harmonic mean (f1score) of them



LEARNING GOALS:

4 components:

1\. vector DB:

&#x09;goal:  

&#x09;1. structure the text document in proper format for proper chunking and info retrieval like separating each charachters strengths , weakness their talking,style behaviour etc (idea: their behavior will decide wheather they play or not or how they fight in game)

&#x09;COMPLETED:

&#x09;1. IMPLEMENTED BASIC RAG 

&#x09;2. IMPLEMENTED BASIC PIPELINE

DONE	

2\. relational DB:

&#x09;GOAL:

&#x09;1. make relational DB with specified columns , day 2

3\. LLM Model :

&#x09;GOAL:

&#x09;1. prompt engineering to get desired output, day 3-4

&#x09;COMPLETED:

&#x09;1. USED AND TESTED NEW\_MODEL

4\. game engine:

&#x09;GOAL:

&#x09;1. backend logic , day 4-7

5\. evaluation of rag and llm



goal:1. for front end include character selection, vs bot or player (cpu = True for bot) to change the format of output

2\. create different vecdb of different players and based on id load that db only 

3\. evaluate rag output for normal chain splitter vs agent based chunking  



Probelsm to solev:

DELETE REPO LLM RPG AND CREATE NEW ONE WHERE NO .ENV FILE IS THERE

1\. when generate code and move from 1st page to 2nd when enetrd code make sure that user with id that generatd code onl moves to 2nd page

2\. add timer

\#3. make the text box available only when its their turn - done

\#4. make health bars and makeactual changes to health - done

5\. add more data of charachters

6\. sepeate eachcharch vector database and retirev accordingly 

7\. also when in 3rd page and reload it displays "Looking for match configurations..." instead of keeping reload on that redirect to 2nd page when that mesaage displays same for 2nd page rediefct to 1st page

8\. design 2 separate algo for semantic search 1 using traditional app and other using my starting from 1st and adding if the simsilaruty is below else new xhunck  









