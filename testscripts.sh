# curl -X POST http://127.0.0.1:5000/lyrics -H 'Content-Type: application/json' -d '{"artist_name": "Taylor Swift", "song_name": "Cruel Summer", "lang": "en"}'
# curl -X GET http://127.0.0.1:5000/search -H 'Content-Type: application/json' -d '{"query": "Taylor swift"}'

curl -X POST http://10.1.17.114:5302/analyse/LJzp_mDxaT0/1 -H 'Content-Type: application/json' -d '{"lang": "en"}'