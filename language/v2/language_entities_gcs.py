#
# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# DO NOT EDIT! This is a generated sample ("Request",  "language_entities_gcs")

# To install the latest published package dependency, execute the following:
#   pip install google-cloud-language

# sample-metadata
#   title: Analyzing Entities (GCS)
#   description: Analyzing Entities in text file stored in Cloud Storage
#   usage: python3 samples/v2/language_entities_gcs.py [--gcs_content_uri "gs://cloud-samples-data/language/entity.txt"]

# [START language_entities_gcs]
from google.cloud import language_v2


def sample_analyze_entities(gcs_content_uri):
    """
    Analyzing Entities in text file stored in Cloud Storage

    Args:
      gcs_content_uri Google Cloud Storage URI where the file content is located.
      e.g. gs://[Your Bucket]/[Path to File]
    """

    client = language_v2.LanguageServiceClient()

    # gcs_content_uri = 'gs://cloud-samples-data/language/entity.txt'

    # Available types: PLAIN_TEXT, HTML
    type_ = language_v2.Document.Type.PLAIN_TEXT

    # Optional. If not specified, the language is automatically detected.
    # For list of supported languages:
    # https://cloud.google.com/natural-language/docs/languages
    language_code = "en"
    document = {
        "gcs_content_uri": gcs_content_uri,
        "type_": type_,
        "language_code": language_code,
    }

    # Available values: NONE, UTF8, UTF16, UTF32
    encoding_type = language_v2.EncodingType.UTF8

    response = client.analyze_entities(
        request={"document": document, "encoding_type": encoding_type}
    )

    # Loop through entitites returned from the API
    for entity in response.entities:
        print(f"Representative name for the entity: {entity.name}")

        # Get entity type, e.g. PERSON, LOCATION, ADDRESS, NUMBER, et al
        print(f"Entity type: {language_v2.Entity.Type(entity.type_).name}")

        # Loop over the metadata associated with entity.
        # Some entity types may have additional metadata, e.g. ADDRESS entities
        # may have metadata for the address street_name, postal_code, et al.
        for metadata_name, metadata_value in entity.metadata.items():
            print(f"{metadata_name}: {metadata_value}")

        # Loop over the mentions of this entity in the input document.
        # The API currently supports proper noun mentions.
        for mention in entity.mentions:
            print(f"Mention text: {mention.text.content}")

            # Get the mention type, e.g. PROPER for proper noun
            print(
                "Mention type: {}".format(
                    language_v2.EntityMention.Type(mention.type_).name
                )
            )

            # Get the probability score associated with the first mention of the entity in the (0, 1.0] range.
            print(f"Probability score: {mention.probability}")

    # Get the language of the text, which will be the same as
    # the language specified in the request or, if not specified,
    # the automatically-detected language.
    print(f"Language code of the text: {response.language_code}")


# [END language_entities_gcs]


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--gcs_content_uri",
        type=str,
        default="gs://cloud-samples-data/language/entity.txt",
    )
    args = parser.parse_args()

    sample_analyze_entities(args.gcs_content_uri)


if __name__ == "__main__":
    main()
