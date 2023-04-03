from flask import Flask, redirect, url_for, render_template, request, session
import requests
from config import API_KEY

app = Flask(__name__)
app.secret_key = "secret_key"

@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        user = request.form["nm"]
        session["user"] = user
        return redirect(url_for("user"))
    else:
        return render_template("index.html")

@app.route("/user")
def user():
    if "user" in session:
        user = session["user"]
        api_url = f"https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{user}?api_key={API_KEY}"
        response = requests.get(api_url)
        summoner_id = response.json()['id']
        mastery_url = f"https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{summoner_id}?api_key={API_KEY}"
        response = requests.get(mastery_url)
        data = response.json()
        player_data = []
        for item in data:
            new_dict ={key: item[key] for key in list(item)[:8]}
            player_data.append(new_dict)


        response = requests.get("https://ddragon.leagueoflegends.com/cdn/13.1.1/data/en_US/champion.json")
        champion_data = response.json()["data"]

        champion_dict = {champion_data[champion]["name"]:champion_data[champion]["key"] for champion in champion_data}
        player_data = [{k: str(v) if isinstance(v, int) else v for k, v in inner_dict.items()} for inner_dict in player_data]

        for item in player_data:
            id = item['championId']
            for key, value in champion_dict.items():
                if id == value:
                    item['championId'] = key
        return render_template("stats.html", user=user, player_data=player_data)
    else:
        return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)