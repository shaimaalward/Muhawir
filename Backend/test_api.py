import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# Load Adam's personality
with open("prompts/adam.txt", "r", encoding="utf-8") as file:
    adam_prompt = file.read()


print("\n==========================")
print("     MUHAWIR - ADAM")
print("==========================\n")


# Adam starts the conversation
response = client.responses.create(
    model="gpt-5.4-mini",
    instructions=adam_prompt,
    input="""
Start the conversation naturally.

You recently heard that Muslims around the world
pray toward the Kaaba.

Ask the trainee why Muslims do this.
"""
)

print("ADAM:")
print(response.output_text)
print()


# Save the conversation state
previous_response_id = response.id


# Conversation loop
while True:

    user_answer = input("YOU: ")

    # Allow us to end the test
    if user_answer.lower().strip() in ["exit", "quit", "end"]:
        print("\nConversation ended.")
        break

    # Send the trainee's answer back to Adam
    response = client.responses.create(
        model="gpt-5.4-mini",
        instructions=adam_prompt,
        previous_response_id=previous_response_id,
        input=user_answer
    )

    print("\nADAM:")
    print(response.output_text)
    print()

    # Remember this response for the next turn
    previous_response_id = response.id