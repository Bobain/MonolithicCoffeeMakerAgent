import pyttsx3


def text_to_speech_pyttsx3(text, voice_id=None, rate=150, volume=1.0):
    """
    Synthétise le texte en parole en utilisant pyttsx3.

    Args:
        text (str): Le texte à synthétiser.
        voice_id (str, optional): L'ID de la voix à utiliser. Si None, utilise la voix par défaut.
        rate (int, optional): La vitesse de la parole (mots par minute).
        volume (float, optional): Le volume de la parole (0.0 à 1.0).
    """
    try:
        engine = pyttsx3.init()

        # Configurer la vitesse de la parole
        engine.setProperty("rate", rate)  # Vitesse de la parole (plus haut = plus rapide)

        # Configurer le volume
        engine.setProperty("volume", volume)  # Volume (0.0 à 1.0)

        # Lister les voix disponibles (optionnel, pour le débogage ou la sélection)
        engine.getProperty("voices")
        # for voice in voices:
        #     print(f"ID: {voice.id} | Name: {voice.name} | Lang: {voice.languages} | Gender: {voice.gender}")

        # Sélectionner une voix spécifique (si un ID est fourni)
        if voice_id:
            engine.setProperty("voice", voice_id)
        # Exemple pour sélectionner une voix féminine en français (peut varier selon le système)
        # else:
        #     for voice in voices:
        #         if "french" in voice.languages and voice.gender == "female": # Adaptez ceci
        #             engine.setProperty('voice', voice.id)
        #             break

        print(f"Synthèse de : '{text}'")
        engine.say(text)
        engine.runAndWait()  # Bloque jusqu'à ce que toute la parole ait été entendue
        engine.stop()  # Nécessaire pour certaines versions/plateformes pour éviter des problèmes
        print("Synthèse terminée.")

    except Exception as e:
        print(f"Une erreur est survenue avec pyttsx3 : {e}")


# Pour trouver un ID de voix spécifique, décommentez la boucle dans la fonction
# et exécutez une fois pour lister les voix, puis utilisez l'ID.
# Par exemple, sur mon Mac, une voix française pourrait être :
# text_to_speech_pyttsx3("Je parle en français.", voice_id='com.apple.speech.synthesis.voice.thomas')
