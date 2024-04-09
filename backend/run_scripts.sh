#!/bin/bash

# Check if an argument is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <image_path>"
    exit 1
fi

# The first argument is the image path
IMAGE_PATH=$1

echo -e 'The following is the output from running OCR (Optical Character Recognition) on a parking sign in San Francisco from different libraries. Each of these libraries performs well in specific sections of the parking plate recognition. Your task is to consider the output from all 3 OCR models we use and combine it with your knowledge of how parking signs usually are written in the San Francisco area to understand what the parking sign they scanned said. On the basis of this and taking into account the current time in PDT time zone tell me whether I can park here or not at the time of making this query. In the case of missing information or information that obviously looks wrong use your own judgement\n\nThis is the output for keras_ocr\n\n' > output.txt

# Activate the virtual environment and run the first Python script with the image path
source env2/bin/activate
python3 ras.py $IMAGE_PATH >> output.txt
deactivate

# Activate the second virtual environment and run the other Python scripts with the image path
source env/bin/activate
echo -e '\n\nThis is the output for the pytesseract model\n\n' >> output.txt
python3 tess.py $IMAGE_PATH >> output.txt
echo -e '\n\nThis is the output for the easy_ocr model\n\n' >> output.txt
python3 easy_ocr.py $IMAGE_PATH >> output.txt
current_date_time=$(date)
echo -e "Remember the time to be considered for checking if parking is allowed is the $current_date_time in PDT.\n\nAlso the response has to be Either Yes or No in the last line based on your analysis and before a line break before the explanation.This is not a definite yes or no. Its your best judgement and if there is no information for the $current_date_time assume its allowed. This is understood by end users as well. Remember the first line of the response is just Yes or no without any spaces\nAlso an important detail to note is while you can use your existing knowledge to fill in gaps and make judgements on what is written on the parking plate you cannot assume anything about whats not written there. In short we refer to the parking plate as the ultimate source of truth and anything missing from overall present on te board is not to be assumed. For eg if the board mentions Mon Tues and Fri you assume there is no information about other days and so by default it should be okay to park. By default assume its okay to park and use the information from the board to restrict your understanding. Also give a brief description of how you reached this conclusion going through each ocr">> output.txt
source oai/bin/activate 
python3 oa_api.py
deactivate
python3 final.py

