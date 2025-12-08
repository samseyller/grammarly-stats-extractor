# Grammarly Statistics Extractor

Every week, Grammarly users receive an email highlighting their statistics for the prior week. These Python scripts can be used to extract the statistics from these messages and organize them in a CSV file.

## Example Email

![Email from Grammarly](images\grammarly-email-example.png)

## Preparing Email Files

Download your weekly Grammarly emails as `.EML` files to the emails folder in the project directory. I suggest downloading the messages as soon as you receive them so you do not miss a week and naming them consecutively. Ex. 01.eml, 02.eml, 03.eml...

Example in Outlook Web:

![Outlook Web dialog Download as EML](images\outlook-download-eml.png)

## Extract Statistics from a Single Email

Run `extract.py .\emails\01.eml`

Output:

```text
📊 Grammarly Metrics Extracted:
- date_range: November 24 - November 30
- writing_streak: 20
- words_analyzed: 50807
- productivity_percentile: 90
- alerts_shown: 104
- accuracy_percentile: 84
- unique_words: 3532
- vocab_percentile: None
- informative: 33
- confident: 29
- direct: 18
- formal: 8
- informal: 8
- curious: 3
- skeptical: 1
```

## Extract All Statistics as a CSV

Run `extract_to_csv.py` to process all `.EML` files in the `.\emails` directory.

Output is saved to `grammarly_metrics.csv`
