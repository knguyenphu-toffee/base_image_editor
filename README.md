## Structure
```
base_image_editor/
├── base_image_editor.py
├── starting_image/
│   └── image.png     (Name doesn't matter)
└── output/

drop each component in designated folder
```
##requirements.txt
```
requests
python-dotenv
pyjwt
tqdm
```

.env
```
GEMINI_API_KEY = ""
```
Filename in starting_image should be:
```
inlfuencerX_baseimage.png
```

It will make 3 image types:
  - 5 Neutral Base Images
  - 5 Crying Base Images
  - 5 Snapchat Images
