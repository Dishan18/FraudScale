from pyspark.sql.functions import length

def apply_heuristics(df):
    return df.filter(
        (df.review_text.isNotNull()) &
        (length("review_text") > 10)
    )