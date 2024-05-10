from aiogram.utils import markdown
from string import Template

welcome_text = f"✨Welcome to Moon Horoscope! Here you can get a free quality horoscope from a certified astrologer!\n\n📜You can also learn a lot of interesting new information about astrology"

start_texts = ['✨Get a horoscope', '📜Educational Menu']

study_text = "⭐️In the educational menu, you can explore the amazing science of astrology!\n\nClick on the question that"

study_menu_texts = {
    "✨What is astrology?": "In simple terms, astrology is the study of the connection between humans and the cosmos, revealing itself in their continuous interaction and development.\n\nAstrology originated in Mesopotamia in the Tigris and Euphrates Valley, where ancient Babylonian and Assyrian priests observed the movements of planets, the positions of the Sun and Moon, and eclipses: they believed that all these phenomena could influence the state",
    "✨What is a horoscope?": "Horoscope is an organized representation of the mutual arrangement of planets in the starry sky within a specific time frame based on zodiac signs. It is used in astrology for many purposes.\n\nEach zodiac sign is named after the nearest constellation: Aries, Taurus, Gemini, Cancer, Leo, Virgo, Libra, Scorpio, Sagittarius, Capricorn, Aquarius, Pisces. The annual cycle of the zodiac begins from the point of the vernal equinox along the Sun's path, corresponding to the end of March and the beginning of the sign of Aries",
    "✨How did the first horoscope appear?": 'History of Horoscope The first horoscopes began to be compiled by the peoples of Mesopotamia around the 5th century BC. The Sumerians, Assyrians, and other inhabitants of the Ancient Near East actively used the "guidance" from the heavens for planning and conducting agricultural work.',
    "✨What do they study in astrology?": '3. Astrology studies the interrelation between stars and their potential influence on people and life on Earth. Despite astrology originating from the Greek word for "study of stars" (astro + logus)',
    "✨What are the 12 houses in astrology?": "The houses of the horoscope are sectors of the ecliptic calculated in the system of sidereal time (the rotation of the Earth on its axis). There are 12 of them, just like the zodiac signs. In astrology, they are associated with various qualities of a person, abilities, manifestations, and areas of activity.",
    "✨Which house is responsible for work?": "The VI house characterizes our everyday routines, caring for loved ones, attitude towards sports, animals, our work, and health (the house is expressed in employees, doctors, and athletes).",
    "✨Which house is responsible for family?": "In the early stages of life, the fourth house indicates the parental family, family karma, and heredity. The significance of planets related to the 4th and 10th houses will be evident in the family structure. As a person matures, important individuals come into their life."
}
# Астро-совет
astro_advices = \
    [
        "Determine what is the most urgent and important thing for today. What can you do about it? How? And act now so that no obstacles dissuade you from achieving the result. There is no need to discuss, ask for approval, or convince. Don’t let yourself be drawn into verbal games that will only waste your energy. A good day for comrades “on their own” who quietly but persistently stick to their line. There are two dangers of this day. First: spend your energy on words, not on deeds. Second: say too much. Promise, agree, spill information, boast, etc. To your own detriment.",
        "This is the most productive day for you. If you know everything for sure, have weighed, calculated and estimated your options - go ahead! If not, you will simply be “carried” on a wave of feelings. Uncontrollable desires, whims, impenetrable stubbornness... Who's going to stop you, come on, to your health! It’s all a matter of how to deal with it later, and the consequences will not be obvious and not quick. But irreparable.",
        "If you don’t have a goal for today and don’t have a clear plan, you’ll be tugged at by everyone and everything you can think of, and you’ll spend the day in empty troubles and fuss. Communicate less. Loneliness and concentration are the most effective behavior model if you need to achieve something. The danger of this day is that there may be tearfulness, touchiness out of the blue, or a wave of some old pain that has not been experienced in its time will cover you. Don't dive into these sad waters, don't. These are all stars, soon your mental well-being will brighten.",
        "The most favorable day for business contacts and discussion of practical issues. Hide your emotions away. You find the necessary convincing words, present not only your arguments, but also make it clear that you also understand the position of your interlocutor. And there is no need to rush to end the conversation quickly, be patient, things can still turn around. Confirm the agreement by repeating the results out loud again. The same applies to the preparation of papers and documents of a legal or official nature.",
        "Today you are precise, extremely specific and cold-blooded. By weighing each word, you understand what reaction it can cause in the listener. There are no impulsive emotional decisions today. A good day for studying technical issues, discussing business and personal problems - most discussions will be constructive. Proceed from considerations of practicality, but for the long term. Winning a momentary battle can result in unpleasant long-term consequences.",
        "Today is a day just to de-stress. The best thing is active rest and physical activity. Forget about everything, turn off tasks and plans from your head. Recover yourself! Things can wait. Let me note that getting some sleep or just lying around won’t work, as you won’t turn off your “record” and won’t gain new energy. Move, walk, go to the gym or to the park, or to the sea. Communication also takes energy.",
        "Mercury is at a tight angle to Uranus, but good to Mars. Too much excitement, turmoil. Events can come quickly, and feelings can overwhelm you. Your task is to control yourself. On the other hand, for those who are in the mood to invent, to act creatively, this is a great day. Today nothing holds back the imagination, and the mind works clearly and quickly. Try not to miss details and nuances; big-picture thinking usually misses all sorts of little things, and they are important."
    ]

# 0, 1, 2 --- shouldn't work
random_texts_year = [
    "2023 will especially shake your love sphere. There was a lot of disagreement. You felt apathy and lack of strength.\n\nHowever! In 2024, Pluto enters the 7th house of the horoscope; with the right actions, the sphere of love and relationships can change globally for the better. You will be able to find strong romantic and friendly connections.",
    "2023 tested your strength and took a lot of energy...\n\n2024 will be a fateful year! Planets enter the most important houses of the horoscope, changes are coming in your career, love affairs and your position in society. If you take into account all the rules, you will be able to reach a completely different level of life💫",
    "2023 has not been the best year for you. The twins had particularly high levels of anxiety and fear for the future, as twins are prone to mental turmoil. The financial sphere and health have collapsed, although you may not realize it yet, life may be at a fateful crossroads...\n\nBUT do not despair! In 2024, Saturn enters the 10th house of the horoscope; with the right actions, your situation may improve and your life will radically change for the better. Especially global changes will be expected in the financial sector.",

    "2023 was not the best year for you, there was a high level of anxiety and the unpredictability of tomorrow...\n\nBut in 2024, Saturn enters the 9th house, with the right actions, your situation may improve and life will become magical, especially in the financial sphere.",
    "2023 tested your strength and took a lot of energy...\n\n2024 will be a fateful year! Planets enter the most important houses of the horoscope, changes are coming in your career, love affairs and your position in society. You will be able to reach a completely different level of life💫",
    "2023 especially shook your nervous system, at times there was apathy and indifference, but 2024 will be completely different!\n\nIn 2024, Pluto enters the 7th house of the horoscope, with the right actions, life can change globally for the better"

]

text_for_referal_sending = Template(f"Hello! I decided to select a few people and give away my complete package of courses {markdown.hbold('free')}, which usually costs $165 and up!\n\n🍃This package includes a 21-day course, designed individually for you and for solution to your problems!\n\nTo receive it, you need to invite 4 friends to us using the link: $link\n\nI will only take 10 people, places may run out in a couple of days, and maybe even today, hurry up🙏🏻🤗\n\nCheck the number of friends invited, as well as the reviews of my clients, you can use the buttons below👇")

how_to_invite_friends = Template("🙏To invite your friend, just send him this text:\n\nHello! I want to recommend an interesting astrological bot where you can get a free astrological analysis for 2024 from a famous astrologer. Here is the link to the bot - $link.")

to_connect = ''

