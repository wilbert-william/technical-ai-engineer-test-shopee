# Explain how it's different from splitting the small vs large files.

- **customers-small.ipynb (100k rows):** a single `pd.read_csv()` loads all 12 columns at once. At this size the whole file fits in memory, so there's no reason to optimize the read.

- **customers-large.ipynb (2M rows):** same analysis, but the data reading adapted for large scale data:
  - `usecols` drops `Index`, `Phone 1`, `Phone 2`, `Website`, the columns we do not needed.
  - `chunksize` parse the CSV to one chunk at a time instead of reading whole 2M row data file at once, then the chunks concat back into one dataframe (df).

The split is't affct in business logic or insights, it's purely an engineering choise, small data gets a plain one read, large data gets a chunking and mempry wise read, so the same analysis code can run on either without spiking memory as the dataset grows.

- **Limitation of the current method:** `usecols` + `chunksize` only makes the red part fast and light it still parse the raw CSV text from scratch every time the notebook runs. CSV isn't built for repeated or long running processing.

- **For long-term/repeated processing:** convert the CSV to Parquet file, for me I used to use DuckDB as a tool to parse and analyze parquet data. Parquet is compressed data, so every read after that is far lighter than parsing the CSV each time.
