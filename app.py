import re
import spacy  # Make sure to install the 'spacy' library

class DialogueState:
    def __init__(self):
        self.current_goal = None
        self.identified_entities = {}
        self.previous_utterances = []

    def set_current_goal(self, goal):
        self.current_goal = goal

    def add_identified_entity(self, entity_type, entity_value):
        self.identified_entities[entity_type] = entity_value

    def add_user_utterance(self, utterance):
        self.previous_utterances.append({"speaker": "User", "text": utterance})

    def add_chatbot_utterance(self, utterance):
        self.previous_utterances.append({"speaker": "Chatbot", "text": utterance})

    def add_previous_utterance(self, utterance):
        self.previous_utterances.append(utterance)

    def get_current_goal(self):
        return self.current_goal

    def get_identified_entities(self):
        return self.identified_entities

    def get_previous_utterances(self):
        return self.previous_utterances

class DialogueFSM:
    def __init__(self):
        # Define the states of the FSM.
        self.states = {
            "start": StartState(),
            "transition_to_next_state": TransitionToNextState(),
            "identify_disease": IdentifyDiseaseState(),
            "provide_medication": ProvideMedicationState(),
            "end": EndState()
        }

        # Set the current state.
        self.current_state = "start"
        self.dialogue_state = DialogueState()

    def transition(self, input_utterance):
        # Get the next state based on the current state and the input utterance.
        next_state = self.states[self.current_state].get_next_state(input_utterance)

        # Set the current state to the next state.
        self.current_state = next_state

        # Execute actions for the current state.
        self.states[self.current_state].execute_actions(input_utterance, self.dialogue_state)


class StartState:
    def get_next_state(self, input_utterance):
        # Always transition to an intermediate state before moving to the actual state.
        return "transition_to_next_state"

    def execute_actions(self, input_utterance, dialogue_state):
        # Greet the user and provide instructions on how to use the system.
        print("Welcome to the medical chatbot. I can help you find information about symptoms, diseases, and medications.")
        print("To get started, please tell me about your symptoms.")

class TransitionToNextState:
    def get_next_state(self, input_utterance):
        # Add logic here to determine the next state based on the input.
        # For example, if "symptom" is in the input, transition to "identify_disease".
        if "symptom" in input_utterance:
            return "identify_disease"
        # If the input doesn't contain symptoms and it's not a specific command, transition to "start".
        elif not any(cmd in input_utterance.lower() for cmd in ["medication", "disease"]):
            return "start"
        # Add more conditions as needed.
        else:
            return "transition_to_next_state"

    def execute_actions(self, input_utterance, dialogue_state):
        # No actions needed for this state.
        pass

class IdentifyDiseaseState:
    def get_next_state(self, input_utterance):
        # After identifying the disease, transition to the provide_medication state.
        return "provide_medication"

    def execute_actions(self, input_utterance, dialogue_state):
        # Extract symptoms from the user's input
        symptoms = extract_symptoms(input_utterance)

        # Identify the disease based on symptoms (you might use a more advanced model for this).
        identified_disease = identify_disease(symptoms)

        # Add the identified disease and symptoms to the dialogue state.
        dialogue_state.add_identified_entity("disease", identified_disease)
        dialogue_state.add_identified_entity("symptoms", symptoms)

        # Generate a response based on the identified disease.
        response = f"I believe you may have {identified_disease} based on the symptoms: {', '.join(symptoms)}. Let me provide information about the medication."

        # Add the user's input and chatbot's response to the dialogue state.
        dialogue_state.add_user_utterance(input_utterance)
        dialogue_state.add_chatbot_utterance(response)

        # Print the response to the user.
        print(response)


class ProvideMedicationState:
    def get_next_state(self, input_utterance):
        # Stay in the provide_medication state.
        return "provide_medication"

    def execute_actions(self, input_utterance, dialogue_state):
        # Get the identified disease from the dialogue state.
        identified_disease = dialogue_state.get_identified_entities().get("disease", "unknown disease")

        # Lookup medication for the disease (you might have a more sophisticated lookup mechanism).
        medication_for_disease = lookup_medication(identified_disease)

        # Generate a response with medication information.
        medication_response = f"The medication for {identified_disease} is: {medication_for_disease}"

        # Add the medication response to the dialogue state.
        dialogue_state.add_chatbot_utterance(medication_response)

        # Print the medication response to the user.
        print(medication_response)

class EndState:
    def get_next_state(self, input_utterance):
        # Stay in the end state.
        return "end"

    def execute_actions(self, input_utterance, dialogue_state):
        # Provide a closing message.
        print("Thank you for using the medical chatbot. If you have more questions, feel free to ask.")

# Add a new function to extract symptoms from user input using spaCy
def extract_symptoms(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    symptoms = [ent.text for ent in doc.ents if ent.label_ == "SYMPTOM"]
    return symptoms

# Rest of the code remains the same

# Your Flask app logic goes here
from flask import Flask, render_template, request, jsonify

app = Flask(__name__,template_folder="templates")

# Instantiate the DialogueFSM
dialog_fsm = DialogueFSM()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_input = request.form["user_input"]
        # Process the user's input
        dialog_fsm.transition(user_input)
        
        # # Get the chatbot's response
        # chatbot_response = "Some response from the chatbot"  # Replace this with your actual response

        # # Return the response as HTML
        # return jsonify({"response": chatbot_response})
    
    # Render the chatbot interface
    return render_template("index.html", dialogue_state=dialog_fsm.dialogue_state)

if __name__ == "__main__":
    app.run(debug=True)


#http://127.0.0.1:5000/