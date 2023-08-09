### Run process:
- Step 1: Create a virtual environment `env`
- Step 2: `env\Scripts\activate`
- Step 3: `pip install -r requirements`
- Step 4: `python app.py`

### Deploy process:
- Step 1: `pip3 freeze > requirements.txt`
- Step 2: Create a github repo
- Step 3: Login into Heroku
- Step 4: Create a `app-name` on Heroku
- Step 5: `git push heroku main`
- Step 6: `heroku open`