# Create index movies
curl \
  -X POST 'http://localhost:7700/indexes' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer DEVLOCALMASTERKEY' \
  --data-binary '{
    "uid": "movies",
    "primaryKey": "id"
  }'
# Now, you're ready to index some data.
curl -i -X POST 'http://localhost:7700/indexes/movies/documents' \
  -H 'Authorization: Bearer DEVLOCALMASTERKEY' \
  --header 'content-type: application/json' \
  --data-binary @test_data.json