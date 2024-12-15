# property-services-montiring
Web app for monitoring health of property services 


# Package management
Rerun the following commands only if `[tool.poetry.dependencies]` is modified in pyproject.toml. \
Poetry is used to ensure compatibility of versions across all packages.
```
poetry lock
poetry export -f requirements.txt --output requirements.txt
```

# Create virtual environment

```
python -m venv .venv/
. .venv/bin/activate
python -m pip install -r requirements.txt
```

# Start webapp
```
streamlit run webapp.py
```
                                    
