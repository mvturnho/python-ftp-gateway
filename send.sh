curl -X POST \
  http://localhost:5000/upload \
  -H 'api-key: your_api_key' \
  -H 'platename: wallplate2' \
  -H 'filename: your_image.png' \
  -F 'file=@./info.png'