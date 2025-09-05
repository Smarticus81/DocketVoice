import os
import json
from dotenv import load_dotenv
from voice_utils import voice_prompt, start_voice_conversation, end_voice_conversation
from pdf_generator import generate_bankruptcy_petition_pdf

def ask_case_type():
    while True:
        resp = voice_prompt("Are you filing under Chapter 7 (liquidation) or Chapter 13 (repayment plan)?")
        if resp.lower() in ["7", "chapter 7", "liquidation", "seven"]:
            return "Chapter 7"
        if resp.lower() in ["13", "chapter 13", "repayment", "repayment plan", "thirteen"]:
            return "Chapter 13"
        voice_prompt("Please say 'Chapter 7' or 'Chapter 13'.")

def ask_basic_info():
    name = voice_prompt("Cool. Let’s start easy—what’s your full name?")
    while not name:
        name = voice_prompt("Sorry, I didn't catch that. Could you tell me your full name?")
    dob = voice_prompt("Perfect. And what’s your date of birth?")
    while not dob:
        dob = voice_prompt("Could you give me your date of birth?")
    address = voice_prompt("Got it. Now, what’s your current home address?")
    while not address:
        address = voice_prompt("Could you tell me your home address?")
    zip_code = voice_prompt("Nice, thanks. And zip code?")
    while not (zip_code.isdigit() and len(zip_code) == 5):
        zip_code = voice_prompt("Please enter a 5-digit zip code.")
    phone = voice_prompt("Alright, let’s get a phone number in case the court or trustee needs to reach you.")
    while not phone:
        phone = voice_prompt("Could you give me a phone number?")
    email = voice_prompt("Cool, got it. Do you have an email you’d like to use for any official stuff?")
    voice_prompt("Great. Thanks, {}! We'll use this info throughout your forms.".format(name))
    return {
        "name": name,
        "dob": dob,
        "address": address,
        "zip_code": zip_code,
        "phone": phone,
        "email": email
    }

def ask_marital_and_dependents():
    voice_prompt("Okay, shifting gears a little—are you currently married, single, separated?")
    marital = voice_prompt("What is your current marital status?")
    while not marital:
        marital = voice_prompt("Could you tell me your marital status? Single, married, divorced, widowed?")

    deps = []
    more = voice_prompt("And do you have any dependents—like kids or anyone you support financially?")
    if more.lower() in ["yes", "yeah", "yep", "sure"]:
        voice_prompt("Perfect, I'll make a note of that.")
        while True:
            dname = voice_prompt("What's the first dependent's name?")
            while not dname:
                dname = voice_prompt("Could you tell me the dependent's name?")

            dage = voice_prompt("And their age?")
            while not dage:
                dage = voice_prompt("What's their age?")

            drel = voice_prompt("What's your relationship to them?")
            while not drel:
                drel = voice_prompt("What's your relationship to this dependent?")

            deps.append({"name": dname, "age": dage, "relationship": drel})

            cont = voice_prompt("Do you have another dependent to add?")
            if cont.lower() not in ["yes", "yeah", "yep", "sure"]:
                break

    voice_prompt("Thanks for letting me know.")
    return {"marital_status": marital, "dependents": deps}

def ask_employment_income():
    voice_prompt("Now, let's talk about work.")
    emp = voice_prompt("What's your current job, or are you unemployed right now?")
    while not emp:
        emp = voice_prompt("Could you tell me about your employment situation?")

    income = voice_prompt("What was your monthly income, roughly, before taxes?")
    while not income:
        income = voice_prompt("What's your monthly income before taxes?")

    side_income = voice_prompt("And just so we cover all bases—do you have any side income, like gig work, rental, or anything like that?")
    if side_income.lower() in ["yes", "yeah", "yep", "sure"]:
        side_details = voice_prompt("Could you tell me about that side income?")
        income = f"{income} + {side_details}"

    voice_prompt("Steady gig—thanks." if "warehouse" in emp.lower() or "work" in emp.lower() else "Okay, thanks for being straight with me.")
    return {"employer": emp, "gross_income_last_6m": income}

def ask_assets_liabilities():
    voice_prompt("Last big section for today—any cars, houses, or major stuff you own?")
    voice_prompt("Doesn't have to be fancy, just anything in your name.")

    assets = []
    while True:
        item = voice_prompt("What's one asset you own, or say 'done' if you're finished?")
        if item.lower() in ["done", "finished", "that's all", "no more"]:
            break

        value = voice_prompt("What's the estimated value of that?")
        while not value:
            value = voice_prompt("Could you give me an estimated value?")

        assets.append({"item": item, "value": value})

        cont = voice_prompt("Do you have another asset to add?")
        if cont.lower() not in ["yes", "yeah", "yep", "sure"]:
            break

    # Now collect debts/liabilities
    voice_prompt("Now let's talk about your debts and bills.")
    debts = []
    while True:
        cred = voice_prompt("What's one creditor you owe money to, or say 'done' if you're finished?")
        if cred.lower() in ["done", "finished", "that's all", "no more"]:
            break

        amt = voice_prompt("How much do you owe them?")
        while not amt:
            amt = voice_prompt("Could you tell me the amount owed?")

        debt_type = voice_prompt("Is this a credit card, loan, medical bill, or other type of debt?")
        while not debt_type:
            debt_type = voice_prompt("What type of debt is this?")

        debts.append({"creditor": cred, "amount": amt, "type": debt_type})

        cont = voice_prompt("Do you have another debt to add?")
        if cont.lower() not in ["yes", "yeah", "yep", "sure"]:
            break

    voice_prompt("Got it. Thanks, that's all super helpful.")
    voice_prompt("We'll wrap this up now, but this gives us everything we need for your petition.")

    return {"assets": assets, "liabilities": debts}

def main():
    load_dotenv()  # ...existing code...
    hf_token = os.getenv("hf_token")

    # Start continuous voice conversation
    start_voice_conversation()

    voice_prompt("Welcome to the Bankruptcy Petition Assistant. Let's get started!")

    data = {}
    data["case_type"] = ask_case_type()
    data.update(ask_basic_info())
    data.update(ask_marital_and_dependents())
    data.update(ask_employment_income())
    data.update(ask_assets_liabilities())

    # Save collected data
    output_path = os.path.join(os.getcwd(), "petition_data.json")
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)

    # Generate PDF petition
    pdf_path = generate_bankruptcy_petition_pdf(data)
    voice_prompt("Perfect! I've generated your bankruptcy petition PDF.")

    voice_prompt("Awesome—thanks for hanging in with me. You did great.")

    # End continuous voice conversation
    end_voice_conversation()

    print(f"\nAll done! Your petition data is saved to {output_path}.")
    print(f"Your bankruptcy petition PDF has been generated: {pdf_path}")
    print("You can now review both files or submit them to the court.")

if __name__ == "__main__":
    main()
