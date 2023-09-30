import csv
from agent import Agent
import datetime

INPUT_DIR = "input/"
OUTPUT_DIR = "output/"
LOG_DIR = "logs/"

processing_agent = Agent()

def generate_wikipedia_url(place, state):
    """
    Generate the Wikipedia URL based on the provided schema.
    """
    # Replace spaces with underscores and encode the place and state
    encoded_place = place.replace(" ", "_")
    encoded_state = state.replace(" ", "_")

    # Construct the Wikipedia URL
    wikipedia_url = f"https://en.wikipedia.org/wiki/{encoded_place},_{encoded_state}#Communities"
    return wikipedia_url

def process_row(row):
    try:
        country, county, state = row
        wikipedia_url = generate_wikipedia_url(county, state)
        response = processing_agent.process(country=country, url=wikipedia_url)
        print(response)
    except Exception as e:
        with open(LOG_DIR + f"log_{datetime.now().strftime('%Y-%m-%d')}.txt", 'a') as log_file:
            log_file.write(f"Error processing row {row}: {str(e)}\n")

def main(filename):
    # Main function to process the CSV file
    with open(INPUT_DIR + filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            process_row(row)    

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Please provide the filename as an argument.")
        sys.exit(1)
    main(sys.argv[1])