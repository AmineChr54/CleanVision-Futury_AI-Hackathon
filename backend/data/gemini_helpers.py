# This file contains helper functions for interacting with the Google Gemini API.
import google.generativeai as genai
import os
from dotenv import load_dotenv

def initialize_gemini():
    """
    Loads environment variables from a .env file and configures the Gemini API key.
    This function must be called before any other Gemini API operations.
    """
    # Load environment variables from a .env file in the project root
    load_dotenv()
    try:
        # Configure the Gemini API with the key from the environment variables
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    except KeyError:
        # Handle the case where the API key is not found in the environment
        print("GEMINI_API_KEY not found in .env file. Please create a .env file and add your API key.")
        exit()

def list_available_models(require_method: str | None = "generateContent"):
    """Return a list of available model names, optionally filtering by a supported method.

    Args:
        require_method: If set (e.g. "generateContent"), only return models that list
                        this capability in supported_generation_methods.

    Returns:
        List[str]: Model names available to this API key/session.
    """
    try:
        models = list(genai.list_models())
    except Exception as e:
        print(f"Warning: Failed to list models: {e}")
        return []

    names: list[str] = []
    for m in models:
        try:
            methods = getattr(m, "supported_generation_methods", []) or []
            if (require_method is None) or (require_method in methods):
                names.append(getattr(m, "name", ""))
        except Exception:
            # Be permissive if model object shape changes
            continue
    # API returns fully-qualified names like 'models/gemini-1.5-flash'; normalize to short name as well
    short = []
    for n in names:
        short.append(n.split("/")[-1])
    # Deduplicate while preserving order
    seen = set()
    unique = []
    for n in short:
        if n and n not in seen:
            seen.add(n)
            unique.append(n)
    return unique


def get_gemini_model(model_name: str | None = None, verbose: bool = True):
    """Initialize and return a GenerativeModel with graceful fallback.

    Behavior:
      - If model_name is provided and supported for generateContent, use it.
      - Otherwise, pick the first available from a preferred list of stable models.

    Preferred order (most broadly available first):
      gemini-1.5-flash, gemini-1.5-pro, gemini-1.5-flash-8b
    """
    available = list_available_models(require_method="generateContent")

    # If caller specified a model explicitly, prefer honoring it directly without relying on list_models
    if model_name:
        # Normalize common alias
        cand = model_name.replace("-latest", "") if model_name.endswith("-latest") else model_name
        if verbose:
            print(f"Using requested Gemini model: {cand}")
        return genai.GenerativeModel(cand)

    # Normalized names from API are short form like 'gemini-1.5-flash'
    def is_supported(name: str) -> bool:
        return name in available or f"models/{name}" in available

    # Preferred, broadly supported options
    preferred = [
        # Current broadly available multimodal models (ordered by cost/performance balance)
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        "gemini-2.5-flash-lite",
        # Fallback previews if stable names unavailable (will likely still work for image caption)
        "gemini-flash-latest",
        "gemini-pro-latest",
    ]
    for name in preferred:
        if is_supported(name):
            if verbose:
                print(f"Using fallback Gemini model: {name}")
            return genai.GenerativeModel(name)

    # As a last resort, if we couldn't list models (or none matched), try a safe default
    safe_default = "gemini-1.5-flash"
    if verbose:
        print(
            "Could not verify available models; attempting safe default: "
            f"{safe_default}"
        )
    return genai.GenerativeModel(safe_default)
