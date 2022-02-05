import logging
import logging.handlers
import multiprocessing
import os.path

from flask import Flask, request
import yaml

import push
from radarr import Radarr
from sonarr import Sonarr
import transcoder


with open("config.yaml", "rb") as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)

app = Flask(__name__)

logger = logging.getLogger("wi1-bot.webhook")
logger.setLevel(logging.DEBUG)

radarr = Radarr(config["radarr"]["url"], config["radarr"]["api_key"])
sonarr = Sonarr(config["sonarr"]["url"], config["sonarr"]["api_key"])


def on_grab(req: dict) -> None:
    push.send(
        req["release"]["releaseTitle"], title=f"file grabbed ({req['downloadClient']})"
    )


def on_download(req: dict) -> None:
    if "movie" in req:
        movie_json = radarr._radarr.get_movie_by_movie_id(req["movie"]["id"])

        quality_profile = radarr.get_quality_profile_name(
            movie_json["qualityProfileId"]
        )

        movie_folder = req["movie"]["folderPath"]
        basename = req["movieFile"]["relativePath"]

        push.send(basename, title="movie downloaded")

        path = os.path.join(movie_folder, basename)

        content_id = movie_json["id"]
    elif "series" in req:
        series_json = sonarr._sonarr.get_series(req["series"]["id"])
        quality_profile = sonarr.get_quality_profile_name(
            series_json["qualityProfileId"]
        )

        series_folder = req["series"]["path"]
        basename = req["episodeFile"]["relativePath"].split("/")[-1]

        push.send(basename, title="episode downloaded")

        path = os.path.join(series_folder, req["episodeFile"]["relativePath"])

        content_id = series_json["id"]
    else:
        raise ValueError("unknown download request")

    try:
        if quality_profile not in config["transcoding"]["profiles"]:
            return
    except KeyError:
        return

    quality_options = config["transcoding"]["profiles"][quality_profile]

    transcoder.queue.add(
        path=path,
        video_bitrate=quality_options["video_bitrate"],
        audio_codec=quality_options["audio_codec"],
        audio_channels=quality_options["audio_channels"],
        audio_bitrate=quality_options["audio_bitrate"],
        content_id=content_id,
    )


@app.route("/", methods=["POST"])
def index():
    try:
        if request.json is None or "eventType" not in request.json:
            return "", 400

        #  logger.debug(f'got request: {request.json}')

        if request.json["eventType"] == "Grab":
            on_grab(request.json)
        elif request.json["eventType"] == "Download":
            on_download(request.json)
    except Exception:
        logger.warning(f"error handling request: {str(request.data)}", exc_info=True)

    return "", 200


def run(logging_queue: multiprocessing.Queue) -> None:
    queue_handler = logging.handlers.QueueHandler(logging_queue)

    logger.addHandler(queue_handler)

    logger.debug("starting webhook listener")

    app.run(host="localhost", port=9000)


if __name__ == "__main__":
    app.run(host="localhost", port=9000)