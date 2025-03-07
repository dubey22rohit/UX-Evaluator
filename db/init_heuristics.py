from loguru import logger

def get_default_heuristics():
    """
    Returns a list of Nielsen's 10 usability heuristics with descriptions
    """
    return [
        {
            "name": "Visibility of System Status",
            "description": "The system should always keep users informed about what is going on, through appropriate feedback within reasonable time.",
            "category": "feedback"
        },
        {
            "name": "Match Between System and Real World",
            "description": "The system should speak the users' language, with words, phrases and concepts familiar to the user, rather than system-oriented terms.",
            "category": "language"
        },
        {
            "name": "User Control and Freedom",
            "description": "Users often choose system functions by mistake and will need a clearly marked 'emergency exit' to leave the unwanted state.",
            "category": "navigation"
        },
        {
            "name": "Consistency and Standards",
            "description": "Users should not have to wonder whether different words, situations, or actions mean the same thing. Follow platform conventions.",
            "category": "design"
        },
        {
            "name": "Error Prevention",
            "description": "Even better than good error messages is a careful design which prevents a problem from occurring in the first place.",
            "category": "errors"
        },
        {
            "name": "Recognition Rather Than Recall",
            "description": "Minimize the user's memory load by making objects, actions, and options visible. Instructions should be visible or easily retrievable.",
            "category": "memory"
        },
        {
            "name": "Flexibility and Efficiency of Use",
            "description": "Accelerators -- unseen by the novice user -- may often speed up the interaction for the expert user.",
            "category": "efficiency"
        },
        {
            "name": "Aesthetic and Minimalist Design",
            "description": "Dialogues should not contain information which is irrelevant or rarely needed.",
            "category": "design"
        },
        {
            "name": "Help Users Recognize, Diagnose, and Recover from Errors",
            "description": "Error messages should be expressed in plain language (no codes), precisely indicate the problem, and constructively suggest a solution.",
            "category": "errors"
        },
        {
            "name": "Help and Documentation",
            "description": "Even though it is better if the system can be used without documentation, it may be necessary to provide help and documentation.",
            "category": "help"
        }
    ]

async def init_heuristics(db):
    """
    Initialize the heuristics collection with Nielsen's 10 usability heuristics
    """
    try:
        # Check if heuristics collection is empty
        if db.heuristics.count_documents({}) == 0:
            # Get default heuristics
            heuristics = get_default_heuristics()
            
            # Insert heuristics into database
            result = db.heuristics.insert_many(heuristics)
            
            logger.info(f"Successfully initialized {len(result.inserted_ids)} heuristics")
        else:
            logger.info("Heuristics collection already initialized")
            
    except Exception as e:
        logger.error(f"Error initializing heuristics: {str(e)}")
        raise