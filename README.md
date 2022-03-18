# wi1-bot

A Discord bot to integrate Radarr (with plans for Sonarr as well), allowing commands like !addmovie and !downloads.

Usage:

1. Copy `config.yaml.template` to `config.yaml` and set the necessary values.
2. `pip install -r requirements.txt`
3. `python start.py`

TODO:

- Actually enforce download quotas
- Add Sonarr support — !addshow
- !linktmdb
    - !rate / !ratings (https://developers.themoviedb.org/3/movies/rate-movie)
    - !movierec based off of ratings and similar-to-user ratings?
        - https://towardsdatascience.com/the-4-recommendation-engines-that-can-predict-your-movie-tastes-109dc4e10c52
        - or just use TMDB's API to get recommendations (if that's possible?)
- !movieinfo showing user/public ratings and other general info (runtime, cast, director)
    - Use TMDB API to get movie metadata
    - If movie isn't on Radarr, react to message to add it?
    - Tautulli API (get_history) to show who has already seen the movie
- User leaderboard
