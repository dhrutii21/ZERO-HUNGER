# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List , Text, Union

# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
# from rasa_sdk.forms import FormAction
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []

from typing import Any, Dict, List, Text, Union

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict


class BmiForm(Action):

    def name(self) -> Text:
        return "bmi_form"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Dict[Text, Any]]:
        height = tracker.slots.get("height")
        weight = tracker.slots.get("weight")

        if not height:
            dispatcher.utter_message(text="Please provide your height.")
            return [SlotSet("requested_slot", "height")]
        elif not weight:
            dispatcher.utter_message(text="Please provide your weight.")
            return [SlotSet("requested_slot", "weight")]

        try:
            height = float(height)
            weight = float(weight)
        except ValueError:
            dispatcher.utter_message(text="Please provide valid inputs for height and weight.")
            return [SlotSet("requested_slot", None)]

        bmi = round(float(weight) / (float(height) ** 2),2)

        bmi_category = ""
        if bmi< 18.5:
        	bmi_category= 'under weight'
        elif bmi >=18.5 and bmi < 25:
        	bmi_category="normal"
        elif bmi >=25 and bmi<30:
        	bmi_category="Overweight"
        else:
        	bmi_category="Obese"
        dispatcher.utter_message(text=f"Your BMI is {bmi}, this is considered {bmi_category}")        
        return [SlotSet("requested_slot", None)]



class CalorieRecommendation(Action):
    def name(self) -> Text:
        return "calorie_form"
    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
    	return ["gender","activity_level","age","bmi"]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
    	return {
    		"gender":[
    			self.from_text(),
    			self.from_entity(entity="gender", intent=["provide_calories"])
    		],
    		"activity_level":[
    			self.from_text(),
    			self.from_entity(entity="activity_level", intent=["provide_calories"])
    		],
    		"age":[
    			self.from_text(),
    			self.from_entity(entity="age", intent=["provide_calories"])
    		]
    	} 

    def validate_age(
    	self,
    	value: Text,
    	dispatcher: CollectingDispatcher,
    	tracker: Tracker,
    	domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
    	if not value.isdigit():
    		dispatcher.utter_message(text="Please enter a valid age : ")
    		return {"age": None}
    	elif int(value)<0 or int(value) >120:
    		dispatcher.utter_message(text="Please enter valid age between 0 and 20 : ")
    		return {"age": None}
    	else: 
    		return {"age": int(value)}

    def validate_activity_level(
    	self,
    	value: Text,
    	dispatcher: CollectingDispatcher,
    	tracker: Tracker,
    	domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
    	levels = ["sedentary","moderately active","active","very active"]
    	if value.lower() not in levels: 
    		dispatcher.utter_message(text="Please choose from the following activity levels : ")
    		dispatcher.utter_message(text="Sedentary, Moderately active, Active , Very active.")
    		return {"activity_level": None}
    	else:
    		return {"activity_level": value.lower()}

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        gender = tracker.get_slot("gender")
        weight = tracker.get_slot("weight")
        height = tracker.get_slot("height")
        age = tracker.get_slot("age")
        activity_level = tracker.get_slot("activity_level")

        if gender == "male":
            bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
        elif gender == "female":
            bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
        else:
            dispatcher.utter_message(text="I'm sorry, I couldn't understand your gender.")
            return []

        if activity_level == "sedentary":
            tdee = bmr * 1.2
        elif activity_level == "lightly active":
            tdee = bmr * 1.375
        elif activity_level == "moderately active":
            tdee = bmr * 1.55
        elif activity_level == "very active":
            tdee = bmr * 1.725
        elif activity_level == "extra active":
            tdee = bmr * 1.9
        else:
            dispatcher.utter_message(text="I'm sorry, I couldn't understand your activity level.")
            return []

        recommended_calories = round(tdee, 2)

        dispatcher.utter_message(text=f"Based on your information, you should consume {recommended_calories} calories per day.")

        return []


