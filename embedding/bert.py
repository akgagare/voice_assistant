from sentence_transformers import SentenceTransformer, util

# Load the pre-trained SBERT model
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

def compare_answers(candidate_answer, expected_answer):
    # Convert answers into embeddings
    candidate_embedding = model.encode(candidate_answer, convert_to_tensor=True)
    expected_embedding = model.encode(expected_answer, convert_to_tensor=True)

    # Compute cosine similarity
    similarity_score = util.pytorch_cos_sim(candidate_embedding, expected_embedding).item()
    
    # Scale similarity score to percentage
    percentage_score = round(similarity_score * 100, 2)

    return percentage_score

# Example Usage
expected_answer = "React is a JavaScript library for building user interfaces, developed by Facebook. It allows developers to build reusable UI components and manage state efficiently using a virtual DOM. React follows a declarative programming approach and enables fast updates through its reconciliation process."
candidate_answer = "react is used for frontend designing and can work well for state management and efficient state handling"

score = compare_answers(candidate_answer, expected_answer)
print(f"Similarity Score: {score}%")
