# sentiment_worker.py
# co-author : Gemini 2.5 Pro Preview
import json
import logging
import sys

# Configure basic logging for the worker
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

try:
    from textblob import TextBlob
except ImportError:
    logger.error("TextBlob is not installed in the environment where sentiment_worker.py is running.")
    # Output a JSON error message that the main app can parse
    print(json.dumps({"error": "TextBlob not installed in worker environment."}))
    sys.exit(1)


def analyze(text_to_analyze: str) -> dict:
    """
    Analyzes the sentiment of the given text.
    This function is intended to be run in an environment where TextBlob is installed.
    """
    blob = TextBlob(text_to_analyze)
    sentiment = blob.sentiment
    return {
        "polarity": round(sentiment.polarity, 2),
        "subjectivity": round(sentiment.subjectivity, 2),
        "assessment": "positive" if sentiment.polarity > 0 else "negative" if sentiment.polarity < 0 else "neutral",
        "answer_from": f"{__file__}.{sys._getframe().f_code.co_name}",
    }


if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_text = sys.argv[1]
        try:
            result = analyze(input_text)
            print(json.dumps(result))  # Output result as JSON to stdout
            ### TODO!!! this will not work with a real server/client setup
        except (TypeError, ValueError) as e: # Catch specific errors from analyze() or json.dumps()
            logger.error(f"Error during sentiment analysis in worker (type/value error): {e}")
            print(json.dumps({"error": f"Analysis error: {str(e)}"}))
            sys.exit(1)
        except Exception as e:  # Fallback for other unexpected errors
            logger.error(f"Unexpected error during sentiment analysis in worker: {e}")
            print(json.dumps({"error": f"Unexpected worker error: {str(e)}"}))
            sys.exit(1)
            logger.error(f"Error during sentiment analysis in worker: {e}")
            print(json.dumps({"error": str(e)}))
            sys.exit(1)
    else:
        logger.error("No text provided to sentiment_worker.py")
        print(json.dumps({"error": "No text provided to worker."}))
        sys.exit(1)
