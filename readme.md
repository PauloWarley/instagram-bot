Para executar use: 
python app.py

N
<!-- API -->

# login
curl --location 'http://localhost:5000/create-login' \
--header 'Content-Type: application/json' \
--data-raw '{
    "username":"usuario_do_instagram",
    "password": "senha"
}'

# likes
curl --location 'http://localhost:5000/create-like' \
--header 'Content-Type: application/json' \
--data '{
    "login": "usuario_do_instagram,
    "usernames": ["paginas_que_terão_like"]
}'

# get accounts
curl --location 'http://localhost:5000/get-accounts'