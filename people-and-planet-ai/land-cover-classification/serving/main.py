# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import io
import os
from typing import List

import ee
import flask
import google.auth
import numpy as np
import requests
import tensorflow as tf

app = flask.Flask(__name__)


INPUT_BANDS = [
    "B1",
    "B2",
    "B3",
    "B4",
    "B5",
    "B6",
    "B7",
    "B8",
    "B8A",
    "B9",
    "B10",
    "B11",
    "B12",
]

DEFAULT_MODEL_PATH = os.environ["MODEL_PATH"]


@app.route("/predict/<float(signed=True):lat>/<float(signed=True):lon>/<int:year>")
def predict(lat: float, lon: float, year: int) -> List:
    patch_size = flask.request.args.get("patch-size", 256, type=int)
    model_path = flask.request.args.get("model-path", DEFAULT_MODEL_PATH)
    include_inputs = flask.request.args.get("include-inputs", "false") == "true"

    ee_init()

    scale = 10
    image = sentinel2_image(f"{year}-01-01", f"{year}-12-31")
    point = ee.Geometry.Point([lon, lat])
    region = point.buffer(scale * patch_size / 2, 1).bounds(1)
    url = image.getDownloadURL(
        {
            "region": region,
            "dimensions": [patch_size, patch_size],
            "format": "NPY",
            "bands": INPUT_BANDS,
        }
    )

    response = requests.get(url)
    response.raise_for_status()
    patch = np.load(io.BytesIO(response.content), allow_pickle=True)

    model = tf.keras.models.load_model(model_path)
    model_inputs = np.stack([patch[name] for name in INPUT_BANDS], axis=-1)
    probabilities = model.predict(np.stack([model_inputs]))[0]
    outputs = np.argmax(probabilities, axis=-1).astype(np.uint8)

    if include_inputs:
        inputs = {name: patch[name].tolist() for name in patch.dtype.names}
        return {"inputs": inputs, "outputs": outputs.tolist()}
    else:
        return {"outputs": outputs.tolist()}


def ee_init() -> None:
    credentials, project = google.auth.default(
        scopes=[
            "https://www.googleapis.com/auth/cloud-platform",
            "https://www.googleapis.com/auth/earthengine",
        ]
    )
    ee.Initialize(credentials, project=project)


def sentinel2_image(start_date: str, end_date: str) -> ee.Image:
    def mask_sentinel2_clouds(image: ee.Image) -> ee.Image:
        CLOUD_BIT = 10
        CIRRUS_CLOUD_BIT = 11
        bit_mask = (1 << CLOUD_BIT) | (1 << CIRRUS_CLOUD_BIT)
        mask = image.select("QA60").bitwiseAnd(bit_mask).eq(0)
        return image.updateMask(mask)

    return (
        ee.ImageCollection("COPERNICUS/S2")
        .filterDate(start_date, end_date)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
        .map(mask_sentinel2_clouds)
        .median()
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
