from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # This acts as a strict blueprint. 
    # It tells Python: "Expect a string variable named DATABASE_URL inside the environment."
    DATABASE_URL: str 

    # This extra block tells Pydantic exactly where to hunt for that string
    model_config = SettingsConfigDict(env_file=".env")

# We initialize the settings class right here so any other file can easily import it
settings = Settings()
