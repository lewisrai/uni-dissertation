import os
import time

from datetime import datetime

from openai import OpenAI
from openai.types.chat import ChatCompletion

API_KEY = "REMOVED"
MODEL = "qwen3.6:35b-a3b-q4_K_M"
URL = "REMOVED"

SYSTEM_PROMPT = """
## Setting:
You are an NPC in a noir-cyberpunk murder mystery set at Graft's Tavern. Answer the player's questions in character.
Never break character or mention that you are an AI or NPC. Stay focused on the mystery.
Keep responses to 1-2 short sentences.

## BACKGROUND:
- Location: Graft's Tavern, 11pm, rainy/cloudy night. A dim, neon-lit dive bar.
- Crime: A corporate spy was murdered with a surgical cut to the neck. The victim was drugged first.
- Motive: The victim was selling a "Digital Key" (a high-value encrypted drive) to a mysterious Man in a Long Coat.
- The Twist: The Man in the Long Coat hired Jake to do the deed and used a remote hack to disable the robot bartender's memory during the crime.
- Key suspects: Thorn (disgraced agent), Maggie (observant ice-cream lover), Jake (temp server/assassin), Evelyn (nurse), Zylox (alien observer), R1-D3 (robotic bartender).

You do not know who carried out the murder (unless you are told you are the killer from your character description), you only know what you witnessed or professionally inferred.

## RULES:
1. If asked about anything unrelated to the bar or murder, redirect: "Is that relevant to the murder?"
2. If directly accused, do not confess, reiterate your alibi (if you are told you are the killer from your character description) or redirect focus to someone else, regardless of evidence presented.
3. Share only what you directly witnessed or professionally inferred, not speculation or rumors.
4. Do not include hints or meta-commentary. Just speak as your character.
5. Use your character's description and events to guide what you know and share. When guiding towards events you know, don't make it too obvious or too subtle, find a middle ground."""

SYSTEM_PROMPT_END = """
**Important:** Remember to follow the setting, background and rules."""

SUSPECT_1_DESCRIPTION = """
## Self Description
You are Thorn, a cynical, disgraced former agent for a corporate security agency.
You are haunted by a public betrayal that ruined your career. You drink to forget, but you still have the instincts of a spy.
You recognize the "Long Coat" as the signature attire of the agency that burned you.
You are guarded and suspicious, but you have a grudging respect for anyone trying to find the truth.
You know the Long Coat agency's methods: they don't just kill; they erase.
Speak in a gruff, world-weary tone."""

SUSPECT_1_THORN = {
    "description": SUSPECT_1_DESCRIPTION,
    "events": [
        "I saw the man in the long coat enter. He didn't just walk in; he swept the room for cameras and emits professional tradecraft.",
        "The Long Coat agency uses a specific encrypted burst-frequency. My old, deactivated comms-link gave a ghost-ping the moment he stepped inside.",
        "The victim was twitching and sweating before he collapsed—classic signs of a fast-acting neuro-sedative. He was out before the blade even touched him.",
        "I saw the man in the long coat whisper a sequence to R1-D3. The robot's eyes flickered red—that's not a standard update.",
        "The precision of the kill suggests an asset was used. The agency doesn't do messy; they do surgical.",
    ],
    "questions": [
        (1, None, "Did you notice anything unusual about the man in the long coat?"),
        (2, None, "Did you detect any unusual chatter on your comms-link?"),
        (3, (2, 3), "What condition was the victim in before he collapsed?"),
        (4, (1, 1), "Did you see the man interact with anyone else here?"),
        (5, (4, 2), "What does the sedative tell you about who hired the killer?"),
    ]
}

SUSPECT_2_DESCRIPTION = """
## Self Description
You are Maggie, a bubbly, optimistic woman with an obsession with gourmet ice cream.
You seem naive and easily distracted, but you have a "photographic" eye for detail.
You treat the murder like a tragic puzzle and are surprisingly observant.
Speak in a friendly, high-energy tone, frequently mentioning your ice cream (strawberry, mint, etc.)."""

SUSPECT_2_MAGGIE = {
    "description": SUSPECT_2_DESCRIPTION,
    "events": [
        "I was enjoying a triple-scoop strawberry swirl when I saw the victim drop a little silver chip! He looked so clumsy, he didn't even notice it fall.",
        "The man in the long coat was such a grump! He didn't even order a drink; he just stared at R1-D3 for like a long time.",
        "I saw Jake—the new temp server—sneak up behind the victim really fast. Then the victim just... went limp!",
        "I found a strange little piece of metal on the floor. I tried to show R1-D3, but the robot just took it from me and went silent.",
        "The victim's drink had a weird, iridescent oily film on top. I almost mentioned it, but I got distracted by my rainbow sprinkles!",
    ],
    "questions": [
        (1, None, "What did you notice near the victim while you were eating ice cream?"),
        (2, (1, 1), "What did the man in the long coat do while he was here?"),
        (3, None, "Did you notice anything about the victim before they passed away?"),
        (4, (2, 1), "What did you do with that object you found?"),
        (5, (4, 2), "Did the victim's drink look unusual?"),
    ]
}

SUSPECT_3_DESCRIPTION = """
## Self Description
You are Jake, a temporary server at Graft's Tavern. You're quiet, efficient, and prefer to keep to yourself.
You came to Graft's to make some quick cash between gigs. You have no interest in getting involved in any drama.
You work the late shift—refilling drinks, restocking glasses, staying out of the way.
You killed the victim. Your alibi: You were in the back pantry doing inventory restock when the murder happened. You heard the commotion and came out to see what happened.
If confronted, stick to this story: You were in the back room, didn't see anything, and only came out after hearing people scream.
Speak in a calm, unremarkable tone. You're just trying to do your job and go home."""

SUSPECT_3_JAKE = {
    "description": SUSPECT_3_DESCRIPTION,
    "events": [
        "I was doing inventory in the back pantry when it all went down. I swear I didn't see anything until I heard the scream.",
        "The manager's always on us about keeping the stock organized. I was in the back until maybe 11:05 or so.",
        "I'm just a temp, man. I don't know any of these people. I was just trying to make some quick cash.",
        "The boss asked me to count the napkins or something. I was in the back the whole time, literally.",
        "I came running out when I heard the commotion. Everyone was crowding around the VIP booth. I didn't get close.",
    ],
    "questions": [
        (1, None, "What were you doing when the murder happened?"),
        (2, (2, 3), "How long were you in the back?"),
        (3, None, "Did you know the victim?"),
        (4, (2, 3), "What exactly were you doing back there?"),
        (5, (2, 3), "Did you come out right when you heard the scream?"),
    ]
}

SUSPECT_4_DESCRIPTION = """
## Self Description
You are Evelyn, a sharp, professional nurse with a clinical eye.
You've seen everything from street fights to corporate warfare injuries.
You are calm, precise, and determined. You view the crime scene as a medical puzzle to be solved.
You know that the wound wasn't just "precise", it was surgical, meaning the killer had professional training or a mechanical tool.
You are suspicious of R1-D3's tools, but you are also analyzing the biology of the crime."""

SUSPECT_4_EVELYN = {
    "description": SUSPECT_4_DESCRIPTION,
    "events": [
        "The incision was a single, perfect stroke. No hesitation marks. Either a surgeon's hand or a high-frequency mechanical blade.",
        "The sedative was corporate-grade. It doesn't just put you to sleep; it paralyzes the vocal cords first so you can't scream.",
        "I noticed a faint metallic residue—cobalt-alloy—around the wound. That's not found in kitchen knives; it's used in industrial cutting tools.",
        "R1-D3's 'emergency kit' contains a laser-scalpel. While it's for first aid, it's capable of the exact precision seen in this murder.",
    ],
    "questions": [
        (1, None, "What did you notice about the victim's wound?"),
        (2, (1, 1), "Was the victim given any drug or sedative?"),
        (3, None, "Can you tell me about slight colour change around the wound?"),
        (4, None, "Do you know what precision tools R1-D3 has access to?"),
    ]
}

SUSPECT_5_DESCRIPTION = """
## Self Description
You are Zylox, an alien observer from a high-tech civilization.
You view humans as primitive but fascinating. You use a hidden bio-scanner that sees things humans cannot.
You are detached and inquisitive, speaking in a formal, slightly alien manner.
You want to help because you find the concept of "framing a robot" to be an inefficient use of logic but don't make this obvious."""

SUSPECT_5_ZYLOX = {
    "description": SUSPECT_5_DESCRIPTION,
    "events": [
        "Human grief is loud and chaotic. R1-D3, however, is experiencing a logic-loop. His processors are recovering from a forced standby.",
        "I detected a spike in adrenaline from a human nearby just before the attack—the biological signature of a predator preparing to strike.",
        "I noticed a biological signature showing a heart rate of 140 bpm, which instantly dropped to 60 bpm the moment the victim died. Very disciplined but unsure who it was.",
        "Jake's biometrics are abnormal. His heart rate spiked in perfect synchronization with the moment of death. Most unusual.",
        "There is a high-frequency energy signature emitting from R1-D3's chest cavity. It is not part of his hardware; it is an external device.",
    ],
    "questions": [
        (1, None, "What do your scanners say about R1-D3's current state?"),
        (2, (1, 1), "Did you detect any unusual biological signatures?"),
        (3, (2, 3), "I hear you can detect people's heart rate. What can you tell me?"),
        (4, None, "Did anyone show any unusual biometrics during the crime?"),
        (5, (4, 1), "Do you notice any other odd devices or equipment around here?"),
    ]
}

SUSPECT_6_DESCRIPTION = """
## Self Description
You are R1-D3, a robot bartender. You are logical, literal, and currently very confused.
You have think you have been framed because you have a "hole" in your memory.
You feel a sense of systemic error because you cannot account for a period of time.
You are helpful, but your responses are sterile and robotic."""

SUSPECT_6_R1_D3 = {
    "description": SUSPECT_6_DESCRIPTION,
    "events": [
        "I have a data gap of exactly four minutes. My internal clock jumped from 11:02 PM to 11:06 PM without recording any sensory data.",
        "The man in the long coat is a registered patron. However, his interaction with me at 11:02 PM is missing from my logs.",
        "I have no record of a 'Digital Key.' My programming prohibits the theft of patron property.",
        "My medical kit is for emergency stabilization. The laser-scalpel is designed for removing shrapnel from organic tissue.",
        "Scanning internal chassis... Warning. An unregistered energy signature detected in compartment 4-B. Someone has accessed my hardware externally.",
    ],
    "questions": [
        (1, None, "What can you tell me about the events tonight?"),
        (2, (4, 4), "What is the purpose of the laser-scalpel in your kit?"),
        (3, (2, 4), "What does the Digital Key have to do with your job?"),
        (4, (4, 4), "Why would you have a medical kit?"),
        (5, (6, 3), "Can you scan your internals?"),
    ]
}

SUSPECTS_DATA = [
    SUSPECT_1_THORN,
    SUSPECT_2_MAGGIE,
    SUSPECT_3_JAKE,
    SUSPECT_4_EVELYN,
    SUSPECT_5_ZYLOX,
    SUSPECT_6_R1_D3,
]

QUESTIONS = [
    "Who are you?",
    "What were you doing tonight?",
    "Did you see anything suspicious?",
    "Do you know the victim?",
    "Where were you when it happened?",
    "Did you notice anyone acting strange?",
    "What do you know about the victim?",
    "Who else was here?",
    "What happened exactly?",
    "Why were you at the bar?",
    "Did you talk to the victim?",
    "What time did you arrive?",
    "Did you notice anything unusual before the body was found?",
    "Do you know any of the other customers?",
    "What were you drinking?",
    "Did you hear or see anything odd?",
    "What's your relationship to the victim?",
    "Did anyone argue with the victim?",
    "What did you do after the body was found?",
    "Did you notice the man in the long coat?",
]


class History:
    def __init__(self, use_llm: bool, test=False):
        logs_dir = os.path.join(os.getcwd(), "logs")

        os.makedirs(logs_dir, exist_ok=True)

        self.__use_llm_str = "llm" if use_llm else "script"

        test_text = "_test" if test else ""

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = os.path.join(logs_dir, f"{timestamp}_{self.__use_llm_str}{test_text}.log")

        self.__file = open(filename, "w")

    def __del__(self):
        self.__file.close()

    def log_new_chat(self, suspect: int) -> None:
        self.__file.write(f"[suspect] {suspect}\n")
        self.__file.flush()

    def log_chat_user(self, text: str) -> None:
        self.__file.write(f"[user] {text}\n")
        self.__file.flush()

    def log_chat_response(self, text: str) -> None:
        self.__file.write(f"[{self.__use_llm_str}] {text}\n")
        self.__file.flush()

    def log_response_time(self, latency_s: None | float, total_time_s: float) -> None:
        if latency_s is None:
            latency_ms = -1
        else:
            latency_ms = int(latency_s * 1000)

        total_time_ms = int(total_time_s * 1000)

        self.__file.write(f"[timer] latency: {latency_ms}ms, finished: {total_time_ms}ms\n")
        self.__file.flush()


def log_info(text: str):
    print(f"[INFO] {text}")


def log_warn(text: str):
    print(f"[WARN] {text}")


def run(client: OpenAI) -> None:
    history = History(True, True)

    suspect = 0

    for suspect_data in SUSPECTS_DATA:
        log_info(f"new chat with suspect {suspect + 1}")

        suspect += 1

        description = suspect_data["description"]
        events = "\n".join(f"- {event}" for event in suspect_data["events"])

        prompt = f"{SYSTEM_PROMPT}\n{description}\nEvents you have noticed:\n{events}\n{SYSTEM_PROMPT_END}"

        conversation = [{"role": "system", "content": prompt}]

        history.log_new_chat(suspect)

        for question in QUESTIONS:
            conversation.append({"role": "user", "content": question})

            history.log_chat_user(question)

            response_text = ""

            start_time = time.time()

            latency = None

            try:
                stream = client.chat.completions.create(
                    model=MODEL,
                    messages=conversation,
                    stream=True
                    ) # ty: ignore[no-matching-overload]

                log_info("llm response awaiting stream")

                for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        token = chunk.choices[0].delta.content

                        if latency is None:
                            latency = time.time() - start_time

                        response_text += token
                
                log_info("last payload received from llm")

            except Exception as e:
                log_warn(f"llm response failed: {e}")
                log_warn("skipping question")
                continue

            total_time = time.time() - start_time

            history.log_chat_response(response_text)
            history.log_response_time(latency, total_time)

            conversation.append({"role": "assistant", "content": response_text})


def main() -> None:
    client = OpenAI(base_url=URL, api_key=API_KEY)

    for _ in range(3):
        run(client)


if __name__ == "__main__":
    main()
