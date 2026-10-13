
import os
import config

print("Current working directory:")
print(os.getcwd())

print("\nConfiguration file being loaded:")
print(config.__file__)

print("\nModel configured:")
print(repr(config.LLM_MODEL))

print("\nAPI key exists:")
print(bool(config.GROQ_API_KEY))
